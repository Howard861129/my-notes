---
title: 功能測試頁面
tags:
  - test
---

$n$維超立方體圖(hypercube graph)定義為

$$
Q_n=(V,E)
$$

其中

$$
V=\{0,1\}^n. 
$$

也就是每個頂點都是

$$
x=(x_1,x_2,…,x_n),\quad x_i∈\{0,1\}
$$

$$
\{x,y\}∈E \iff d_H​(x,y)=1
$$
測試

將日文所有漢字的部分用模板顯示，例如<ruby>漢字<rt>かんじ</rt></ruby>

``` text
web_test
├── static
│   └── style.css
├── templates
│   └── index.html
└── app.py
```

### `app.py`

``` python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```