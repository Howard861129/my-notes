# ==================================================
# Python 網頁程式入口
# ==================================================

from js import document  # pyright: ignore[reportMissingImports]

from gui_test import start_gui
from lightup import run_lightup
from tree_editor import mount, unmount
from counter import mount as mount_counter, unmount as unmount_counter


def element_exists(element_id):
    """
    檢查 HTML 元素是否存在。
    """
    return document.querySelectorAll(
        f"#{element_id}"
    ).length > 0


def main():
    """
    整個 Python 網頁程式的啟動入口。
    """

    if element_exists("gui-test-app"):
        start_gui()

    if element_exists("lightup-app"):
        run_lightup()

    if element_exists("tree-editor-app"):
        mount("tree-editor-app")
    else:
        unmount("tree-editor-app")

    if element_exists("counter-app"):
        mount_counter("counter-app")
    else:
        unmount_counter("counter-app")


if __name__ == "__main__":
    main()