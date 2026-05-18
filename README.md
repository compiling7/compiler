# CompilerLab - 类Rust编译器前端可视化

一个基于Python实现的类Rust语言编译器前端，支持词法分析、语法分析、语义分析、IR生成和汇编代码生成，并提供现代化的桌面可视化界面。

## 功能特性

### 编译器管道 (5阶段)

| 阶段 | 输入 → 输出 | 实现 |
|------|-------------|------|
| **Lexer** | 源代码 → Token序列 | `lexer.py` |
| **Parser** | Token序列 → AST | `parser.py` (递归下降) |
| **Semantic** | AST → 符号表 + 语义检查 | `semantic.py` |
| **IR** | AST → 三地址码(四元组) | `ir_generator.py` |
| **Assembly** | IR → x86-64 NASM汇编 | `assembly_generator.py` |

### 可视化界面 (7个视图)

- **Editor**: 代码编辑器 + 输出预览
- **Lexer**: Token流表格 (类型/值/行列)
- **Parser**: 语法分析追踪过程
- **AST**: 交互式树形可视化 (D3.js)
- **IR**: 三地址码四元组表格
- **Assembly**: NASM汇编代码语法高亮
- **Issues**: 错误列表 + 符号表

## 项目结构

```
compiler/
├── compiler_ast.py       # AST节点定义
├── token_types.py        # Token类型定义
├── lexer.py              # 词法分析器
├── parser.py             # 语法分析器 (递归下降)
├── semantic.py           # 语义分析器
├── ir_generator.py       # IR中间代码生成器
├── assembly_generator.py # x86-64 NASM汇编生成器
├── visualization.py      # AST文本可视化
│
├── web_app.py            # Flask后端API
├── templates/
│   └── index.html        # 前端界面 (TailwindCSS + D3.js)
├── main_app.py           # PyWebView桌面入口
│
├── CompilerLab.spec      # PyInstaller打包配置
├── build.py              # 打包脚本
├── requirements.txt      # 依赖
├── README.md             # 本文件
└── testcases/
    ├── test1.rs          # 测试用例: 基本语法
    ├── test2.rs          # 测试用例: 条件与循环
    └── error1.rs         # 测试用例: 错误示例
```

## 运行方式

### 开发模式 (浏览器)

```bash
# 1. 安装依赖
pip install flask

# 2. 启动Web服务
python web_app.py

# 3. 打开浏览器访问
# http://127.0.0.1:5000
```

### 桌面应用模式 (原生窗口)

```bash
# 1. 安装依赖
pip install flask pywebview

# 2. 启动桌面应用
python main_app.py
```

### 打包为独立可执行文件

```bash
# 1. 安装PyInstaller
pip install pyinstaller

# 2. 打包
python build.py

# 3. 输出在 dist/CompilerLab.exe (Windows) 或 dist/CompilerLab (Linux/macOS)
```

## 技术栈

- **后端**: Python + Flask (REST API)
- **前端**: HTML + TailwindCSS + Material Symbols + D3.js
- **桌面壳**: PyWebView (系统原生WebView)
- **打包**: PyInstaller

## 语言规范

### 词法规则

| 类型   | 规则                                                                       |
| ------ | -------------------------------------------------------------------------- |
| 关键字 | i32, let, if, else, while, return, mut, fn, for, in, loop, break, continue |
| 标识符 | (字母\|_)(字母\|数字\|_)*                                                |
| 数值   | 数字(数字)*                                                                |
| 赋值号 | =                                                                          |
| 算符   | +, -, *, /, ==, >, >=, <, <=, !=, &, ->, ., .., ..=                       |
| 界符   | (, ), {, }, [, ]                                                           |
| 分隔符 | ;, :, ,                                                                    |
| 注释   | // ... \n, /* ... */                                                       |

### 语法规则

```
program        = fn_decl*
fn_decl        = "fn" ID "(" params ")" ("->" type)? block
params         = param ("," param)* | ε
param          = "mut"? ID ":" type
block          = "{" stmt* "}"
stmt           = let_stmt | return_stmt | if_stmt | while_stmt | for_stmt | assign_stmt | expr_stmt |
empty_stmt
let_stmt       = "let" "mut"? ID (":" type)? ("=" expr)? ";"
if_stmt        = "if" expr block ("else" (block | if_stmt))?
while_stmt     = "while" expr block
for_stmt       = "for" ID "in" expr block
expr           = additive (comp_op additive)*
additive       = term (("+" | "-") term)*
term           = factor (("*" | "/") factor)*
factor         = NUM | ID | ID "(" args ")" | "(" expr ")" | "[" list "]" | "-" factor
type           = "i32" | "[" type ";" NUM "]"
```

## 编译管道示例

输入:
```rust
fn main() -> i32 {
    let x: i32 = 10;
    let mut y: i32 = 5;
    y = x + 20;
    if y > 10 {
        return 1;
    } else {
        return 0;
    }
}
```

输出 (Token流):
```
Token(FN, 'fn', 1, 1)  Token(ID, 'main', 1, 4)  Token('(', '(', 1, 8)  ...
```

输出 (IR四元组):
```
(func, main, _, _)
(=, 10, _, t0)       (assign, t0, _, x)
(=, 5, _, t1)        (assign, t1, _, y)
(+, x, 20, t2)       (assign, t2, _, y)
(>, y, 10, t3)       (if_false, t3, _, L0)
...
```

输出 (x86-64汇编):
```asm
default rel
global main

section .text
main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov rax, 10
    mov [rbp-8], rax
    ...
```
