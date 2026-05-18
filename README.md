<<<<<<< HEAD
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
=======
# 类Rust词法和语法分析工具

一个基于Python实现的类Rust语言词法和语法分析工具，支持可视化AST输出。

## 功能特性

### 词法分析

- 支持关键字: `fn`, `let`, `mut`, `if`, `else`, `while`, `return`, `i32`, `for`, `in`, `loop`, `break`, `continue`
- 支持标识符: `(字母|_)(字母|数字|_)*`
- 支持数值常量
- 支持运算符: `+`, `-`, `*`, `/`, `==`, `>`, `>=`, `<`, `<=`, `!=`,  `&`
- 支持特殊符号:`->`,`.`,`..`
- 支持界符: `( ) { } [ ]` 和分隔符 `; : ,`
- 支持单行注释 `//` 和多行注释 `/* */`
- 结束符: `#`

### 语法分析

- 程序结构: 函数声明序列
- 函数声明: 支持参数列表、返回值类型、函数体
- 变量声明: 支持可变变量 (`let mut`)
- 赋值语句
- 选择结构: `if ... else`
- 循环结构: `while`
- 表达式: 算术运算、比较运算、函数调用

### AST可视化

- 语法结构输出
- 抽象语法树树形输出
>>>>>>> 661b9812f96a549b4a6fa1c00d5cf185523dd921

## 项目结构

```
compiler/
<<<<<<< HEAD
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
=======
├── token_types.py    # Token类型定义
├── lexer.py          # 词法分析器
├── ast.py            # AST节点定义
├── parser.py         # 语法分析器（递归下降）
├── visualization.py  # AST可视化
├── main.py           # Tkinter图形界面
├── test.py           # 测试脚本
├── requirements.txt  # 依赖说明
├── README.md         # 本文件
└── testcases/
    ├── test1.rs      # 测试用例1: 基本语法
    ├── test2.rs      # 测试用例2: 条件与循环
    └── error.rs      # 测试用例3: 错误示例
>>>>>>> 661b9812f96a549b4a6fa1c00d5cf185523dd921
```

## 运行方式

<<<<<<< HEAD
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
=======
```bash
python main.py
```

## 使用方法

1. 在左侧输入框输入类Rust源代码
2. 点击「词法分析」查看Token序列
3. 点击「语法分析」查看语法结构和AST树
4. 点击「清空结果」清空输出区域

## 测试用例说明

- `test1.rs`: 基本函数声明、变量声明、赋值、函数调用
- `test2.rs`: 条件语句(if)、循环语句(while)、复杂表达式
- `error.rs`: 包含语法错误的代码，用于测试错误处理
>>>>>>> 661b9812f96a549b4a6fa1c00d5cf185523dd921

## 语言规范

### 词法规则

| 类型   | 规则                                                                       |
| ------ | -------------------------------------------------------------------------- |
| 关键字 | i32, let, if, else, while, return, mut, fn, for, in, loop, break, continue |
| 标识符 | (字母\|_)(字母\|数字\|_)*                                                |
| 数值   | 数字(数字)*                                                                |
| 赋值号 | =                                                                          |
<<<<<<< HEAD
| 算符   | +, -, *, /, ==, >, >=, <, <=, !=, &, ->, ., .., ..=                       |
=======
| 算符   | +, -, *, /, ==, >, >=, <, <=, !=, &, ->                                    |
>>>>>>> 661b9812f96a549b4a6fa1c00d5cf185523dd921
| 界符   | (, ), {, }, [, ]                                                           |
| 分隔符 | ;, :, ,                                                                    |
| 注释   | // ... \n, /* ... */                                                       |

<<<<<<< HEAD
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
=======
### 语法规则 (摘要)

```
Program        -> Declaration串
Declaration    -> FunctionDecl
FunctionDecl   -> fn ID ( ParamList ) (-> Type)? Block
ParamList      -> ε | Param (, Param)*
Param          -> mut? ID : Type
Statement      -> ; | return Expr; | let mut? ID (: Type)? (= Expr)? ; |
                 ID = Expr ; | if Expr Block (else Block)? | while Expr Block
Expr           -> AdditiveExpr (CompOp AdditiveExpr)*
AdditiveExpr   -> Term ((+|-) Term)*
Term           -> Factor ((*|/) Factor)*
Factor         -> NUM | ID | ID ( ArgList ) | ( Expr ) | - Factor
```

## 技术实现

- **词法分析器**: 状态机驱动的词法分析器，支持贪婪匹配
- **语法分析器**: 递归下降Parser，自顶向下分析
- **AST节点**: 面向对象的AST节点设计，支持树形遍历
- **可视化**: 自定义格式化输出，清晰展示语法结构
>>>>>>> 661b9812f96a549b4a6fa1c00d5cf185523dd921
