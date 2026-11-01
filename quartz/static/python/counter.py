"""Quartz + Pyodide：每點一下按鈕，計數 +1。"""
from js import document  # pyright: ignore[reportMissingImports]
from pyodide.ffi import create_proxy  # pyright: ignore[reportMissingImports]


TEMPLATE = """
<div class="counter-card">
  <div class="counter-description">PYTHON TOOL · CLICK COUNTER</div>
  <div class="counter-main">
    <span class="counter-label">目前計數</span>
    <output data-role="count" aria-live="polite">0</output>
  </div>
  <button type="button" data-action="increment">＋1</button>
</div>
"""


class CounterApp:
    def __init__(self, container_id):
        self.container = document.getElementById(container_id)
        self.container.innerHTML = TEMPLATE
        self.count = 0
        self.output = self.container.querySelector('[data-role="count"]')
        self.button = self.container.querySelector('[data-action="increment"]')
        self.click_proxy = create_proxy(self.increment)
        self.button.addEventListener('click', self.click_proxy)

    def increment(self, event):
        self.count += 1
        self.output.textContent = str(self.count)

    def destroy(self):
        self.button.removeEventListener('click', self.click_proxy)
        self.click_proxy.destroy()
        self.container.innerHTML = ''


_instances = {}


def mount(container_id='counter-app'):
    """找到容器才掛載；重複掛載時先清理舊監聽器。"""
    unmount(container_id)
    if document.querySelectorAll(f'#{container_id}').length == 0:
        return None
    app = CounterApp(container_id)
    _instances[container_id] = app
    return app


def unmount(container_id='counter-app'):
    app = _instances.pop(container_id, None)
    if app is not None:
        app.destroy()
