"""瀏覽器介面。入口 mount(container_id)，供既有 Pyodide 主程式呼叫。
HTML 是介面模板；Python 負責事件、轉換、縮排、歷史紀錄。
"""
import json
from tree_core import markdown_to_tree, tree_to_markdown

PROJECT = '''+ MyWebsite
  + content
    + index.md
    + 程式研究
      + 樹狀目錄.md
  + quartz
    + static
      + tools
        + tree-editor
          + index.html
          + tree_core.py
          + tree_editor.py
          + style.css
  + quartz.config.yaml'''
DOCUMENT = '''+ 工程筆記
  + 電動操作閥
    + Rotork
    + Limitorque
  + 程式研究
    + Python
    + TypeScript
  + 數燈研究
    + 規則
    + 公式推導'''
TEMPLATE = '''
<div class="te-app">
  <header><span class="te-tag">PYTHON TOOL</span><h1>樹狀目錄產生器</h1>
  <p>寫下清單，整理你的程式與筆記結構。</p></header>
  <div class="te-toolbar"><button data-action="project">網站範例</button>
  <button data-action="document">筆記範例</button>
  <button data-action="clear">清空</button>
  <label>歷史紀錄 <select data-role="history"><option value="">選擇紀錄</option></select></label></div>
  <div class="te-grid">
    <section><div class="te-panelhead"><label for="__ID__-md">Markdown 清單</label><div>
    <button data-action="copy-md">複製</button></div></div>
    <textarea id="__ID__-md" data-role="md" spellcheck="false" aria-label="Markdown 清單"></textarea></section>
    <section><div class="te-panelhead"><label for="__ID__-tree">樹狀文字</label><div>
    <button data-action="copy-tree">複製</button></div></div>
    <textarea id="__ID__-tree" data-role="tree" spellcheck="false" aria-label="樹狀文字"></textarea></section>
  </div>
  <p data-role="status" role="status" aria-live="polite"></p>
  <footer>左右兩側都可編輯，內容即時同步。清單側：Tab 增加縮排，Shift+Tab 減少縮排。<br>
  每行以 +、- 或 * 開頭；歷史紀錄最多保留 20 筆於此瀏覽器。</footer>
</div>'''

class TreeEditor:
    def __init__(self, container_id):
        from js import document, window
        self.document, self.window = document, window
        self.container = document.getElementById(container_id)
        if self.container is None:
            raise ValueError(f'找不到容器 #{container_id}')
        self.container.innerHTML = TEMPLATE.replace('__ID__', container_id)
        self.md = self.container.querySelector('[data-role="md"]')
        self.tree = self.container.querySelector('[data-role="tree"]')
        self.status = self.container.querySelector('[data-role="status"]')
        self.history_select = self.container.querySelector('[data-role="history"]')
        self.proxies, self.listeners, self.history = [], [], []
        self.storage_key = 'yuzihe.tree-editor.v1.' + container_id
        self.storage_ok = True
        self.save_timer = None
        from pyodide.ffi import create_proxy
        self.timer_proxy = create_proxy(self.save_history)
        self.proxies.append(self.timer_proxy)
        try:
            history = json.loads(str(window.localStorage.getItem(self.storage_key) or '[]'))
            if isinstance(history, list):
                self.history = [x for x in history if isinstance(x, dict) and isinstance(x.get('md'), str) and len(x['md']) <= 200_000][:20]
        except Exception:
            self.storage_ok = False
        self.bind(self.md, 'input', lambda event: self.sync('md'))
        self.bind(self.tree, 'input', lambda event: self.sync('tree'))
        self.bind(self.md, 'keydown', self.indent)
        self.bind(self.history_select, 'change', self.restore)
        for button in self.container.querySelectorAll('[data-action]'):
            self.bind(button, 'click', self.dispatch)
        self.refresh_history()
        self.md.value = self.history[0]['md'] if self.history else PROJECT
        self.sync('md', save=False)

    def bind(self, element, event_name, callback):
        from pyodide.ffi import create_proxy
        proxy = create_proxy(callback)
        self.proxies.append(proxy)
        self.listeners.append((element, event_name, proxy))
        element.addEventListener(event_name, proxy)

    def say(self, text, error=False):
        self.status.textContent = text
        self.status.className = 'te-error' if error else 'te-status'

    def sync(self, source, save=True):
        try:
            if source == 'md':
                self.tree.value = markdown_to_tree(str(self.md.value))
            else:
                self.md.value = tree_to_markdown(str(self.tree.value))
            count = sum(bool(x.strip()) for x in str(self.md.value).splitlines())
            self.say(f'已同步 · {count} 個項目' + ('' if self.storage_ok else ' · 此瀏覽器無法保存歷史紀錄'))
            if save:
                if self.save_timer is not None:
                    self.window.clearTimeout(self.save_timer)
                self.save_timer = self.window.setTimeout(self.timer_proxy, 800)
        except ValueError as error:
            if self.save_timer is not None:
                self.window.clearTimeout(self.save_timer)
                self.save_timer = None
            self.say(str(error) + '（另一側保留上次成功轉換的內容）', True)

    def save_history(self):
        self.save_timer = None
        from datetime import datetime
        md = str(self.md.value)
        if self.history and self.history[0]['md'] == md:
            return
        entry = {'md': md, 'time': datetime.now().strftime('%m/%d %H:%M:%S')}
        self.history = [entry] + self.history[:19]
        try:
            self.window.localStorage.setItem(self.storage_key, json.dumps(self.history, ensure_ascii=False))
        except Exception:
            self.storage_ok = False
            self.say('已同步 · 此瀏覽器無法保存歷史紀錄')
        self.refresh_history()

    def refresh_history(self):
        self.history_select.textContent = ''
        option = self.document.createElement('option')
        option.value, option.textContent = '', '選擇紀錄'
        self.history_select.appendChild(option)
        for i, entry in enumerate(self.history):
            option = self.document.createElement('option')
            option.value = str(i)
            title = entry['md'].splitlines()[0] if entry['md'] else '空白'
            option.textContent = f"{entry.get('time', '')} · {title[:30]}"
            self.history_select.appendChild(option)

    def restore(self, event):
        if self.save_timer is not None:
            self.window.clearTimeout(self.save_timer)
            self.save_timer = None
        value = str(self.history_select.value)
        if value:
            self.md.value = self.history[int(value)]['md']
            self.sync('md', save=False)

    def indent(self, event):
        if event.key != 'Tab':
            return
        event.preventDefault()
        text = str(self.md.value)
        start, end = int(self.md.selectionStart), int(self.md.selectionEnd)
        first = text.rfind('\n', 0, start)+1
        last = end
        if end > start and text[end-1:end] == '\n':
            last -= 1
        line_end = text.find('\n', last)
        if line_end == -1:
            line_end = len(text)
        lines = text[first:line_end].split('\n')
        changed, deltas = [], []
        for line in lines:
            if event.shiftKey:
                remove = min(2, len(line)-len(line.lstrip(' ')))
                changed.append(line[remove:]); deltas.append(-remove)
            else:
                changed.append('  '+line); deltas.append(2)
        self.md.setRangeText('\n'.join(changed), first, line_end, 'preserve')
        self.md.setSelectionRange(max(first, start+deltas[0]), max(first, end+sum(deltas)))
        self.sync('md')

    def dispatch(self, event):
        import asyncio
        # DOM 的 currentTarget 在事件返回後會清空，必須立即擷取。
        action = str(event.currentTarget.getAttribute('data-action'))
        asyncio.ensure_future(self.action(action))

    async def action(self, action):
        if action in ('project', 'document', 'clear'):
            self.md.value = {'project': PROJECT, 'document': DOCUMENT, 'clear': ''}[action]
            self.sync('md')
        elif action.startswith('copy-'):
            source = self.md if action.endswith('md') else self.tree
            try:
                await self.window.navigator.clipboard.writeText(str(source.value))
                self.say('已複製到剪貼簿')
            except Exception:
                source.focus(); source.select()
                self.say('已選取文字，請按 Ctrl+C（Mac：⌘C）複製。')

    def destroy(self):
        if self.save_timer is not None:
            self.window.clearTimeout(self.save_timer)
        for element, name, proxy in self.listeners:
            element.removeEventListener(name, proxy)
        for proxy in self.proxies:
            proxy.destroy()
        self.listeners.clear(); self.proxies.clear()
        self.container.innerHTML = ''

_instances = {}
def mount(container_id='tree-editor-app'):
    """重複掛載前清除舊事件，避免重複觸發。呼叫端應先載入 style.css。"""
    if container_id in _instances:
        _instances.pop(container_id).destroy()
    app = TreeEditor(container_id)
    _instances[container_id] = app
    return app

def unmount(container_id='tree-editor-app'):
    if container_id in _instances:
        _instances.pop(container_id).destroy()
