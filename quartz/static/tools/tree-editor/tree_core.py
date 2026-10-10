"""純 Python 轉換核心。不依賴瀏覽器，可 import 或用 CLI 執行。
演算法：掃描每行，維護各層縮排的堆疊；輸出以深度優先遍歷組合分支。
時間 O(輸入字元數 + 輸出字元數)，最多 2000 節點、100 層。
"""
from dataclasses import dataclass, field
import re

@dataclass
class Node:
    name: str
    children: list = field(default_factory=list)

def _lines(text):
    if len(text) > 200_000:
        raise ValueError('內容超過 200,000 字元。')
    lines = [(i, line.rstrip()) for i, line in enumerate(text.splitlines(), 1) if line.strip()]
    if len(lines) > 2000:
        raise ValueError('最多支援 2000 個項目。')
    return lines

def _add(roots, stack, depth, name, line):
    if depth > 100:
        raise ValueError(f'第 {line} 行：最多支援 100 層。')
    if depth > len(stack):
        raise ValueError(f'第 {line} 行：缺少上一層項目。')
    node = Node(name)
    del stack[depth:]
    (stack[-1].children if stack else roots).append(node)
    stack.append(node)

def parse_markdown(text):
    roots, stack, indents = [], [], []
    for line_no, raw in _lines(text):
        raw = raw.expandtabs(2)
        m = re.fullmatch(r'( *)(?:[+*-])\s+(.+)', raw)
        if not m:
            raise ValueError(f'第 {line_no} 行：請使用「+ 名稱」或「- 名稱」。')
        indent, name = len(m[1]), m[2]
        if not indents:
            if indent:
                raise ValueError(f'第 {line_no} 行：第一個項目不可縮排。')
            indents.append(0)
        elif indent > indents[-1]:
            indents.append(indent)
        else:
            while indents and indent < indents[-1]:
                indents.pop()
            if not indents or indent != indents[-1]:
                raise ValueError(f'第 {line_no} 行：縮排沒有對齊既有層級。')
        _add(roots, stack, len(indents)-1, name, line_no)
    return roots

def parse_tree(text):
    roots, stack = [], []
    for line_no, raw in _lines(text):
        # 接受本工具的 Unicode 樹狀線，以及常見的 |-- / `-- ASCII 寫法。
        pos = 0
        while raw[pos:pos+4] in ('│   ', '    ', '|   '):
            pos += 4
        branch = raw[pos:pos+4]
        if branch in ('├── ', '└── ', '|-- ', '`-- ', '+-- '):
            name, depth = raw[pos+4:], pos//4+1
            if not name.strip():
                raise ValueError(f'第 {line_no} 行：名稱不可空白。')
        elif pos == 0:
            name, depth = raw, 0
        else:
            raise ValueError(f'第 {line_no} 行：請使用完整分支「├── 」或「└── 」。')
        _add(roots, stack, depth, name, line_no)
    return roots

def render_markdown(roots):
    lines = []
    def walk(nodes, depth):
        for node in nodes:
            lines.append('  '*depth + '+ ' + node.name)
            walk(node.children, depth+1)
    walk(roots, 0)
    return '\n'.join(lines)

def render_tree(roots):
    lines = []
    def walk(nodes, prefix):
        for i, node in enumerate(nodes):
            last = i == len(nodes)-1
            lines.append(prefix + ('└── ' if last else '├── ') + node.name)
            walk(node.children, prefix + ('    ' if last else '│   '))
    for root in roots:
        lines.append(root.name)
        walk(root.children, '')
    return '\n'.join(lines)

def markdown_to_tree(text):
    return render_tree(parse_markdown(text))

def tree_to_markdown(text):
    return render_markdown(parse_tree(text))

if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser(description='Markdown 清單 ↔ 樹狀文字')
    parser.add_argument('mode', choices=['tree', 'markdown'])
    args = parser.parse_args()
    try:
        print((markdown_to_tree if args.mode == 'tree' else tree_to_markdown)(sys.stdin.read()))
    except ValueError as error:
        parser.exit(2, str(error)+'\n')
