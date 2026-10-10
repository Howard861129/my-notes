#!/usr/bin/env python3
"""數燈結構研究編輯器：Quartz / Pyodide 網頁版。

安裝：將本檔放到既有 Python 模組資料夾，manifest.json 的檔案清單加入
lightup.py；main.py 匯入 run_lightup，頁面具有 lightup-app 時呼叫它。

Markdown 容器：<div id="lightup-app"></div>
main.py：
    from lightup import run_lightup
    if document.getElementById("lightup-app"):
        run_lightup()

也可 run_lightup("gui-test-app") 或傳入容器元素。
不需要 tkinter、Pillow 或新增 npm 套件。
瀏覽器重載後會嘗試還原該頁面上次棋盤；重要資料請下載 JSON 備份。

資料編碼：-2＝黑格0、-1＝無數字黑格、0＝白格、1～4＝數字黑格、5＝燈。
CSV 只存格子；JSON 也存框線。框線樣式是繪圖標記，不阻擋光線。
本工具不枚舉解、不自動求解，也沒有模擬開放棋盤的外部入光。
"""
from __future__ import annotations

import csv
import io
import json
import asyncio

WHITE, BLACK, LAMP, ZERO_BLACK = 0, -1, 5, -2
CLUES = {ZERO_BLACK: 0, 1: 1, 2: 2, 3: 3, 4: 4}
CELL_VALUES = {WHITE, BLACK, LAMP, *CLUES}
YELLOW, INK = '#ffe680', '#171717'
LIMIT = 100


def matrix(rows, cols, value=0):
    return [[value for _ in range(cols)] for _ in range(rows)]


def valid_matrix(value, rows, cols, allowed, name):
    if (not isinstance(value, list) or len(value) != rows
            or any(not isinstance(row, list) or len(row) != cols for row in value)
            or any(type(v) is not int or v not in allowed for row in value for v in row)):
        raise ValueError(f'{name} 的尺寸或數值不正確。')
    return [row[:] for row in value]


class Board:
    """cells: -2 數字0黑格、-1 純黑、0 白、1~4 數字黑格、5 燈；edge: 0 實線、1 虛線。"""
    def __init__(self, rows=6, cols=8):
        if type(rows) is not int or type(cols) is not int or not (1 <= rows <= LIMIT and 1 <= cols <= LIMIT):
            raise ValueError(f'列數與欄數必須是 1～{LIMIT} 的整數。')
        self.rows, self.cols = rows, cols
        self.cells = matrix(rows, cols)
        self.h_edges = matrix(rows + 1, cols)
        self.v_edges = matrix(rows, cols + 1)

    def data(self):
        return {'format': 'lightup-research', 'version': 1,
                'rows': self.rows, 'cols': self.cols,
                'cells': [r[:] for r in self.cells],
                'h_edges': [r[:] for r in self.h_edges],
                'v_edges': [r[:] for r in self.v_edges]}

    @classmethod
    def from_data(cls, data):
        if not isinstance(data, dict) or data.get('format') != 'lightup-research' or type(data.get('version')) is not int or data.get('version') != 1:
            raise ValueError('不支援的檔案格式或版本。')
        b = cls(data.get('rows'), data.get('cols'))
        b.cells = valid_matrix(data.get('cells'), b.rows, b.cols, CELL_VALUES, 'cells')
        b.h_edges = valid_matrix(data.get('h_edges'), b.rows + 1, b.cols, {0, 1}, 'h_edges')
        b.v_edges = valid_matrix(data.get('v_edges'), b.rows, b.cols + 1, {0, 1}, 'v_edges')
        return b

    @classmethod
    def from_csv(cls, text):
        lines = [row for row in csv.reader(io.StringIO(text.lstrip('\ufeff'))) if row]
        if not lines:
            raise ValueError('CSV 不可為空。')
        try:
            values = [[int(v.strip()) for v in row] for row in lines]
        except ValueError:
            raise ValueError('CSV 必須只包含以逗號分隔的整數。') from None
        b = cls(len(values), len(values[0]))
        b.cells = valid_matrix(values, b.rows, b.cols, CELL_VALUES, 'CSV')
        return b

    def csv_text(self):
        stream = io.StringIO(newline='')
        csv.writer(stream, lineterminator='\n').writerows(self.cells)
        return stream.getvalue()

    def analyze(self):
        """按水平／垂直白格區段處理，O(rows*cols)，框線不影響照光。"""
        lit, conflicts = set(), set()
        for horizontal in (True, False):
            outer, inner = (self.rows, self.cols) if horizontal else (self.cols, self.rows)
            for a in range(outer):
                segment = []
                for k in range(inner + 1):
                    pos = (a, k) if horizontal else (k, a)
                    if k < inner and self.cells[pos[0]][pos[1]] in (WHITE, LAMP):
                        segment.append(pos)
                    else:
                        lamps = [p for p in segment if self.cells[p[0]][p[1]] == LAMP]
                        if lamps:
                            lit.update(segment)
                        if len(lamps) > 1:
                            conflicts.update(lamps)
                        segment = []
        clues = []
        whites = lamps_count = 0
        for r, row in enumerate(self.cells):
            for c, v in enumerate(row):
                whites += v in (WHITE, LAMP)
                lamps_count += v == LAMP
                if v in CLUES:
                    adjacent = sum(0 <= rr < self.rows and 0 <= cc < self.cols and self.cells[rr][cc] == LAMP
                                   for rr, cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)))
                    if adjacent != CLUES[v]:
                        clues.append((r, c, CLUES[v], adjacent))
        return {'lit': lit, 'conflicts': conflicts, 'clues': clues,
                'white_count': whites, 'lamp_count': lamps_count,
                'unlit': whites - len(lit),
                'solved': whites == len(lit) and not conflicts and not clues}


def hit_test(x, y, rows, cols, size, margin=24, edge_only=False):
    """傳回 ('cell'|'h'|'v', row, col)；交點採距離最近邊，平手取水平邊。"""
    x, y = x - margin, y - margin
    tolerance = min(8, size * .17)
    if x < -tolerance or y < -tolerance or x > cols*size+tolerance or y > rows*size+tolerance:
        return None
    candidates = []
    hr, vc = round(y / size), round(x / size)
    c, r = min(cols-1, max(0, int(x // size))), min(rows-1, max(0, int(y // size)))
    if 0 <= hr <= rows and -tolerance <= x <= cols*size+tolerance:
        candidates.append((abs(y-hr*size), 'h', hr, c))
    if 0 <= vc <= cols and -tolerance <= y <= rows*size+tolerance:
        candidates.append((abs(x-vc*size), 'v', r, vc))
    if candidates:
        d, kind, a, b = min(candidates)
        if d <= tolerance:
            return kind, a, b
    if not edge_only and 0 <= x < cols*size and 0 <= y < rows*size:
        return 'cell', int(y//size), int(x//size)
    return None


def scene(board, size=64, margin=24):
    """跨 Tk / SVG / PNG 共用的圖元，不含工具列與診斷提示。"""
    lit = board.analyze()['lit']
    shapes = []
    for r, row in enumerate(board.cells):
        for c, value in enumerate(row):
            x, y = margin+c*size, margin+r*size
            fill = (YELLOW if (r,c) in lit else 'white') if value in (WHITE,LAMP) else INK
            shapes.append(('rect', (x,y,x+size,y+size), fill))
            if value == LAMP:
                d = size * .24
                cx, cy = x+size/2, y+size/2
                shapes.append(('circle', (cx-d,cy-d,cx+d,cy+d), 'white'))
            elif value in CLUES:
                shapes.append(('text', (x+size/2,y+size/2), str(CLUES[value])))
    for r, row in enumerate(board.h_edges):
        for c, dash in enumerate(row):
            shapes.append(('line', (margin+c*size,margin+r*size,margin+(c+1)*size,margin+r*size), dash))
    for r, row in enumerate(board.v_edges):
        for c, dash in enumerate(row):
            shapes.append(('line', (margin+c*size,margin+r*size,margin+c*size,margin+(r+1)*size), dash))
    return board.cols*size+2*margin, board.rows*size+2*margin, shapes


def svg_text(board, size=64):
    w,h,shapes = scene(board,size)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           '<title>Light Up research board</title>', '<rect width="100%" height="100%" fill="white"/>']
    for kind, box, value in shapes:
        if kind == 'rect':
            x,y,x2,y2 = box
            out.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" fill="{value}"/>')
        elif kind == 'circle':
            x,y,x2,y2 = box
            out.append(f'<circle cx="{(x+x2)/2}" cy="{(y+y2)/2}" r="{(x2-x)/2}" fill="white" stroke="{INK}" stroke-width="2"/>')
        elif kind == 'text':
            x,y = box
            out.append(f'<text x="{x}" y="{y}" dy="0.35em" text-anchor="middle" font-family="Arial, sans-serif" font-size="{size*.48}" font-weight="bold" fill="white">{value}</text>')
        else:
            x,y,x2,y2 = box
            # 白色底線令黑格邊界上的虛線也可辨識。
            if value:
                out.append(f'<path d="M{x} {y} L{x2} {y2}" stroke="white" stroke-width="2"/>')
            dash = ' stroke-dasharray="6 4"' if value else ''
            out.append(f'<path d="M{x} {y} L{x2} {y2}" stroke="{INK}" stroke-width="2"{dash}/>')
    out.append('</svg>')
    return '\n'.join(out)



class WebEditor:
    """DOM 事件委派：每個容器只綁一組事件，重畫 SVG 不增加監聽器。"""
    def __init__(self, container):
        from js import document, window, Blob, URL, Object, Image
        from pyodide.ffi import create_proxy, to_js
        self.document, self.window = document, window
        self.Blob, self.URL, self.Object, self.Image = Blob, URL, Object, Image
        self.create_proxy, self.to_js = create_proxy, to_js
        self.container = container
        self.board = Board()
        self.undo_stack, self.redo_stack = [], []
        self.listeners, self.tasks = [], set()
        self.alive = True
        self.size = 64
        self.tool = 'lamp'
        self.storage_key = 'lightup-research:v1:' + str(window.location.pathname) + ':' + str(container.id)
        self.restore_warning = ''
        try:
            raw = window.localStorage.getItem(self.storage_key)
            if raw:
                self.board = Board.from_data(json.loads(str(raw)))
        except Exception:
            self.restore_warning = '瀏覽器暫存不可用或資料無法讀取；請使用 JSON 備份。'
        self.build_ui()
        self.listen(container, 'click', self.on_click)
        self.listen(container, 'change', self.on_change)
        self.listen(container, 'contextmenu', self.on_contextmenu)
        self.listen(container, 'keydown', self.on_keydown)
        self.redraw()
        if self.restore_warning:
            self.message(self.restore_warning)

    def options(self, values):
        return self.to_js(values, dict_converter=self.Object.fromEntries)

    def el(self, name):
        return self.container.querySelector('[data-lu="' + name + '"]')

    def listen(self, element, event, function):
        def safe_callback(e):
            if not self.alive:
                return
            try:
                function(e)
            except Exception as exc:
                self.message('操作失敗：' + str(exc))
        proxy = self.create_proxy(safe_callback)
        element.addEventListener(event, proxy)
        self.listeners.append((element, event, proxy))

    def schedule(self, coroutine):
        task = asyncio.ensure_future(coroutine)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)

    def dispose(self):
        """重新掛載前移除 Python 回呼；供 Quartz SPA 或載入器清理使用。"""
        self.alive = False
        for element, event, proxy in self.listeners:
            element.removeEventListener(event, proxy)
            proxy.destroy()
        self.listeners.clear()
        for task in tuple(self.tasks):
            task.cancel()
        self.tasks.clear()

    def build_ui(self):
        self.container.innerHTML = '''
<style>
.lu-editor { color:#171717; background:#f5f7fa; border:1px solid #aab3bf; border-radius:12px; padding:16px; font:15px/1.5 Arial,sans-serif; }
.lu-editor * { box-sizing:border-box; }
.lu-editor h3 { margin:0 0 12px; color:#171717; }
.lu-editor .lu-row { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:10px 0; }
.lu-editor label { display:inline-flex; align-items:center; gap:5px; color:#171717; }
.lu-editor button, .lu-editor input, .lu-editor select { font:inherit; color:#171717; background:white; border:1px solid #8793a4; border-radius:6px; padding:6px 10px; margin:0; }
.lu-editor button { cursor:pointer; }
.lu-editor button:disabled { opacity:.4; cursor:default; }
.lu-editor button[aria-pressed="true"] { color:white; background:#245b9f; border-color:#245b9f; }
.lu-editor input[type="number"] { width:85px; }
.lu-editor .lu-board { overflow:auto; max-height:70vh; background:#e4e8ee; border:1px solid #aab3bf; border-radius:6px; padding:8px; touch-action:pan-x pan-y; }
.lu-editor .lu-board svg { display:block; max-width:none; width:auto; height:auto; cursor:crosshair; }
.lu-editor .lu-status { white-space:pre-wrap; margin-top:12px; color:#171717; }
.lu-editor .lu-message { white-space:pre-wrap; color:#174873; min-height:1.5em; }
.lu-editor .lu-help { margin:8px 0; font-size:13px; color:#465365; }
.lu-editor :focus-visible { outline:3px solid #2683d9; outline-offset:2px; }
</style>
<section class="lu-editor" tabindex="0" aria-label="數燈棋盤編輯器">
<h3>數燈 · 結構研究編輯器</h3>
<div class="lu-row">
<label>列數 <input data-lu="rows" type="number" min="1" max="100" value="6"></label>
<label>欄數 <input data-lu="cols" type="number" min="1" max="100" value="8"></label>
<button type="button" data-action="new">建立空白棋盤</button>
<button type="button" data-action="undo" data-lu="undo">復原</button>
<button type="button" data-action="redo" data-lu="redo">重做</button>
</div>
<div class="lu-row" role="group" aria-label="編輯工具">
<button type="button" data-tool="lamp">燈泡</button>
<button type="button" data-tool="black">黑格</button>
<label>黑格數字 <select data-lu="clue"><option value="none">無</option><option>0</option><option>1</option><option>2</option><option>3</option><option>4</option></select></label>
<button type="button" data-tool="white">白格</button>
<button type="button" data-tool="edge">框線</button>
<button type="button" data-action="clear">清除燈泡</button>
<button type="button" data-action="check">檢查配置</button>
</div>
<div class="lu-row">
<label>畫面格寬 <select data-lu="zoom"><option>28</option><option>40</option><option>48</option><option selected>64</option><option>80</option><option>96</option></select></label>
<label>匯出格寬 <input data-lu="export-size" type="number" min="20" max="200" value="80"> px</label>
<button type="button" data-action="svg">匯出 SVG</button>
<button type="button" data-action="png" data-lu="png">匯出 PNG</button>
<button type="button" data-action="json">下載 JSON</button>
<button type="button" data-action="csv">匯出 CSV</button>
<button type="button" data-action="open">匯入 JSON／CSV</button>
<input data-lu="file" type="file" accept=".json,.csv,application/json,text/csv" hidden>
</div>
<p class="lu-help">點格子套用工具；燈泡再點一次移除。點邊線切換實／虛線；右鍵將格子還原白格。框線樣式不阻擋光線。黃色＝已照亮。<br>CSV 編碼：-2＝黑格0、-1＝純黑格、0＝白格、1～4＝數字黑格、5＝燈泡。JSON 保留框線；CSV 不保留。<br>工具內快捷鍵：Ctrl／⌘＋Z 復原、Shift＋Z 或 Y 重做、S 下載 JSON。檢查以棋盤內燈泡為準，尚未加入外部入光。</p>
<div class="lu-board" data-lu="board" tabindex="0" aria-label="棋盤，請選工具後點擊"></div>
<div class="lu-status" data-lu="status" role="status"></div>
<div class="lu-message" data-lu="message" role="status" aria-live="polite"></div>
</section>'''

    def message(self, text):
        if self.alive:
            self.el('message').textContent = text

    def redraw(self):
        self.el('board').innerHTML = svg_text(self.board, self.size)
        self.el('rows').value, self.el('cols').value = str(self.board.rows), str(self.board.cols)
        self.el('undo').disabled = not self.undo_stack
        self.el('redo').disabled = not self.redo_stack
        buttons = self.container.querySelectorAll('[data-tool]')
        for i in range(buttons.length):
            button = buttons.item(i)
            button.setAttribute('aria-pressed', 'true' if str(button.getAttribute('data-tool')) == self.tool else 'false')
        a = self.board.analyze()
        self.el('status').textContent = (
            f'{self.board.rows}×{self.board.cols}　白格 {a["white_count"]}　燈泡 {a["lamp_count"]}　'
            f'已照亮 {len(a["lit"])}　未照亮 {a["unlit"]}\n'
            f'互照燈泡 {len(a["conflicts"])}　未滿足數字黑格 {len(a["clues"])}'
            + ('　✓ 合法解' if a['solved'] else ''))

    def persist(self):
        try:
            self.window.localStorage.setItem(self.storage_key, json.dumps(self.board.data()))
        except Exception:
            self.message('無法寫入瀏覽器暫存；請下載 JSON 備份。')

    def trim_history(self, stack):
        # 限制大型棋盤復原資料，最多100步，合計最多約25萬格／框線。
        weight = sum(3 * d['rows'] * d['cols'] + d['rows'] + d['cols'] for d in stack)
        while len(stack) > 100 or (weight > 250_000 and len(stack) > 1):
            d = stack.pop(0)
            weight -= 3 * d['rows'] * d['cols'] + d['rows'] + d['cols']

    def commit(self, before):
        if before != self.board.data():
            self.undo_stack.append(before)
            self.trim_history(self.undo_stack)
            self.redo_stack.clear()
            self.message('')
            self.redraw()
            self.persist()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.board.data())
            self.trim_history(self.redo_stack)
            self.board = Board.from_data(self.undo_stack.pop())
            self.redraw()
            self.persist()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.board.data())
            self.trim_history(self.undo_stack)
            self.board = Board.from_data(self.redo_stack.pop())
            self.redraw()
            self.persist()

    def hit(self, event, erase=False):
        svg = self.el('board').querySelector('svg')
        if not svg or not svg.contains(event.target):
            return None
        # 螢幕座標轉 SVG 座標，捲動、縮放及 CSS transform 後仍正確。
        point = svg.createSVGPoint()
        point.x, point.y = event.clientX, event.clientY
        transform = svg.getScreenCTM()
        if not transform:
            return None
        point = point.matrixTransform(transform.inverse())
        if erase:
            x, y = point.x - 24, point.y - 24
            if 0 <= x < self.board.cols*self.size and 0 <= y < self.board.rows*self.size:
                return 'cell', int(y//self.size), int(x//self.size)
            return None
        return hit_test(point.x, point.y, self.board.rows, self.board.cols,
                        self.size, edge_only=self.tool == 'edge')

    def edit(self, event, erase=False):
        hit = self.hit(event, erase)
        if not hit:
            return
        kind, r, c = hit
        before = self.board.data()
        if kind in ('h', 'v'):
            edges = self.board.h_edges if kind == 'h' else self.board.v_edges
            edges[r][c] ^= 1
        elif erase or self.tool == 'white':
            self.board.cells[r][c] = WHITE
        elif self.tool == 'black':
            choice = str(self.el('clue').value)
            self.board.cells[r][c] = BLACK if choice == 'none' else ZERO_BLACK if choice == '0' else int(choice)
        elif self.tool == 'lamp':
            if self.board.cells[r][c] not in (WHITE, LAMP):
                self.message('燈泡只能放白格；請先用白格工具或右鍵移除黑格。')
                return
            self.board.cells[r][c] = WHITE if self.board.cells[r][c] == LAMP else LAMP
        self.commit(before)

    def on_contextmenu(self, event):
        if self.el('board').contains(event.target):
            event.preventDefault()
            self.edit(event, True)

    def on_click(self, event):
        button = event.target.closest('button')
        if button and self.container.contains(button):
            tool = button.getAttribute('data-tool')
            if tool:
                self.tool = str(tool)
                self.redraw()
                self.message('')
                return
            action = str(button.getAttribute('data-action'))
            if action == 'new':
                board = Board(int(str(self.el('rows').value)), int(str(self.el('cols').value)))
                if not self.window.confirm('建立空白棋盤會清除目前內容；完成後仍可用「復原」返回。是否繼續？'):
                    return
                before = self.board.data()
                self.board = board
                self.commit(before)
                self.el('board').scrollTop = self.el('board').scrollLeft = 0
            elif action == 'undo':
                self.undo()
            elif action == 'redo':
                self.redo()
            elif action == 'clear':
                before = self.board.data()
                self.board.cells = [[WHITE if v == LAMP else v for v in row] for row in self.board.cells]
                self.commit(before)
            elif action == 'check':
                self.check()
            elif action == 'open':
                self.el('file').click()
            elif action == 'json':
                self.download_text(json.dumps(self.board.data(), ensure_ascii=False, indent=2), 'json', 'application/json')
            elif action == 'csv':
                self.download_text('\ufeff' + self.board.csv_text(), 'csv', 'text/csv;charset=utf-8')
                self.message('CSV 只存格子；保留框線請另外下載 JSON。')
            elif action == 'svg':
                self.download_text(svg_text(self.board, self.export_size()), 'svg', 'image/svg+xml;charset=utf-8')
            elif action == 'png':
                self.schedule(self.export_png())
        elif self.el('board').contains(event.target):
            self.edit(event)

    def on_change(self, event):
        if event.target == self.el('zoom'):
            self.size = int(str(event.target.value))
            self.redraw()
        elif event.target == self.el('clue'):
            self.tool = 'black'
            self.redraw()
        elif event.target == self.el('file'):
            files = event.target.files
            if files.length:
                file = files.item(0)
                event.target.value = ''  # 可再次匯入同一檔案。
                self.schedule(self.import_file(file))

    def on_keydown(self, event):
        if str(event.target.tagName).lower() in ('input', 'textarea', 'select'):
            return
        if not (event.ctrlKey or event.metaKey) or event.altKey:
            return
        key = str(event.key).lower()
        if key in ('z', 'y', 's'):
            event.preventDefault()
            if key == 's':
                self.download_text(json.dumps(self.board.data(), ensure_ascii=False, indent=2), 'json', 'application/json')
            elif key == 'y' or event.shiftKey:
                self.redo()
            else:
                self.undo()

    def export_size(self):
        size = int(str(self.el('export-size').value))
        if not 20 <= size <= 200:
            raise ValueError('匯出格寬必須是20～200的整數。')
        return size

    def filename(self, extension):
        return f'lightup_{self.board.rows}x{self.board.cols}.{extension}'

    def download_url(self, url, filename):
        link = self.document.createElement('a')
        link.href, link.download = url, filename
        link.style.display = 'none'
        self.document.body.appendChild(link)
        try:
            link.click()
        finally:
            link.remove()

    def download_text(self, text, extension, mime):
        blob = self.Blob.new(self.to_js([text]), self.options({'type': mime}))
        url = self.URL.createObjectURL(blob)
        self.download_url(url, self.filename(extension))
        # 留出瀏覽器開始下載的時間；回呼完成後釋放 proxy。
        proxy = None
        def release():
            self.URL.revokeObjectURL(url)
            proxy.destroy()
        proxy = self.create_proxy(release)
        self.window.setTimeout(proxy, 10_000)
        self.message('已開始下載 ' + extension.upper() + '。')

    async def export_png(self):
        button = self.el('png')
        if button.disabled:
            return
        button.disabled = True
        url = None
        try:
            size = self.export_size()
            # 不先產生大量圖元才檢查上限。
            w, h = self.board.cols*size+48, self.board.rows*size+48
            if w*h > 30_000_000 or max(w, h) > 16_384:
                raise ValueError('PNG太大，請降低匯出格寬或改匯出SVG。')
            filename = self.filename('png')
            text = svg_text(self.board, size)
            self.message('正在產生 PNG…')
            blob = self.Blob.new(self.to_js([text]), self.options({'type': 'image/svg+xml;charset=utf-8'}))
            url = self.URL.createObjectURL(blob)
            image = self.Image.new()
            image.src = url
            await image.decode()
            if not self.alive:
                return
            canvas = self.document.createElement('canvas')
            canvas.width, canvas.height = w, h
            context = canvas.getContext('2d')
            if not context:
                raise RuntimeError('瀏覽器無法建立Canvas。')
            context.drawImage(image, 0, 0, w, h)
            # Canvas 的瀏覽器 PNG 編码器，無需 Pillow。
            data_url = str(canvas.toDataURL('image/png'))
            canvas.width = canvas.height = 1
            if not data_url.startswith('data:image/png'):
                raise RuntimeError('瀏覽器無法輸出這個尺寸的PNG。')
            self.download_url(data_url, filename)
            self.message('已開始下載 PNG。')
        except Exception as exc:
            self.message('PNG 匯出失敗：' + str(exc))
        finally:
            if url:
                self.URL.revokeObjectURL(url)
            if self.alive:
                button.disabled = False

    async def import_file(self, file):
        try:
            if file.size > 5_000_000:
                raise ValueError('檔案超過5 MB，請選擇棋盤JSON或CSV。')
            text = str(await file.text()).lstrip('\ufeff')
            is_csv = str(file.name).lower().endswith('.csv')
            board = Board.from_csv(text) if is_csv else Board.from_data(json.loads(text))
            if not self.alive:
                return
            before = self.board.data()
            self.board = board
            self.commit(before)
            self.redraw()
            self.message('已匯入CSV；框線設為實線。' if is_csv else '已匯入JSON棋盤。')
        except Exception as exc:
            self.message('匯入失敗：' + str(exc))

    def check(self):
        a = self.board.analyze()
        lines = ['目前配置是合法解。' if a['solved'] else '目前配置尚未滿足全部規則。',
                 f'未照亮白格：{a["unlit"]}；互照燈泡：{len(a["conflicts"])}；未滿足數字：{len(a["clues"])}',
                 '座標為（列, 欄），從1開始。']
        if a['conflicts']:
            lines.append('互照燈泡：' + ', '.join(f'({r+1},{c+1})' for r,c in sorted(a['conflicts'])[:30]))
        for r,c,want,have in a['clues'][:30]:
            lines.append(f'黑格({r+1},{c+1})：要求{want}顆，相鄰有{have}顆。')
        self.message('\n'.join(lines))


_instances = {}


def run_lightup(app_id='lightup-app'):
    """掛載完整編輯器。允許傳入容器id或DOM元素；同容器重掛不重複綁事件。"""
    from js import document
    container = document.getElementById(app_id) if isinstance(app_id, str) else app_id
    if not container:
        raise ValueError(f'找不到數燈容器：{app_id}。請先在Markdown加入對應div。')
    # Quartz SPA 切換後，釋放已離開文件的容器及其 Python 回呼。
    for key, editor in list(_instances.items()):
        if not editor.container.isConnected or editor.container == container:
            editor.dispose()
            del _instances[key]
    editor = WebEditor(container)
    _instances[str(container.id) or str(id(editor))] = editor
    return editor


mount_lightup = run_lightup
run = run_lightup


def dispose_lightup(app_id='lightup-app'):
    editor = _instances.pop(app_id, None)
    if editor:
        editor.dispose()
