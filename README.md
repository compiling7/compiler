# CompilerLab - 类Rust编译器前端可视化

一个基于 Python 的类 Rust 语言编译器前端与可视化平台，覆盖词法分析、语法分析、语义分析、IR 生成、汇编生成和运行结果展示。

## 功能特性

### 编译器管道 (5阶段)

| 阶段 | 输入 → 输出 | 实现 |
|------|-------------|------|
| **Lexer** | 源代码 → Token 列表 | `lexer.py` |
| **Parser** | Token 列表 → AST | `parser.py` (递归下降) |
| **Semantic** | AST → 符号表 + 语义检查 | `semantic.py` |
| **IR** | AST → 三地址码（四元组） | `ir_generator.py` |
| **Assembly** | IR → x86-64 NASM 汇编 | `assembly_generator.py` |

### Web 可视化界面 (7个视图)

- **Editor**: 代码编辑器 + 统计面板 + 符号表
- **Lexer**: 代码高亮 + Token 列表 + 详细 Token 信息
- **Parser**: 语法分析树 + 解析跟踪日志
- **LR**: 解析过程逐步可视化 (播放 / 暂停 / 步进 / 调速)
- **AST**: D3.js 交互式抽象语法树
- **Semantic**: 语义符号表与诊断结果
- **IR**: 四元组中间代码展示

### 其它特性

- 支持 `fn`、`let`、`mut`、`if/else`、`while`、`for`、`loop`、`break`、`continue`
- 支持函数声明/调用、数组类型、数组元素访问、返回值类型检查
- 支持语义错误定位与统一错误码
- 后端接口支持单阶段调用与全流水线调用
- 支持生成 NASM 汇编并尝试本机汇编/链接运行（若环境可用）

## 项目结构

```
compiler/
├── compiler_ast.py       # AST 节点定义
├── token_types.py        # Token 类型定义
├── lexer.py              # 词法分析器
├── parser.py             # 递归下降语法分析器
├── semantic.py           # 语义分析器与符号表
├── ir_generator.py       # 四元组 IR 生成器
├── assembly_generator.py # x86-64 NASM 汇编生成器
├── visualization.py      # AST 文本可视化工具
├── web_app.py            # Flask 后端 API
├── main_app.py           # PyWebView 桌面入口
├── templates/
│   └── index.html        # 前端界面 (TailwindCSS + D3.js)
├── CompilerLab.spec      # PyInstaller 打包配置
├── build.py              # 打包脚本
├── requirements.txt      # Python 依赖
├── README.md             # 本文件
└── testcases/            # 测试用例
```

## 后端 API

- `GET /` — 返回前端 `index.html`
- `POST /api/lex` — 词法分析
- `POST /api/parse` — 语法分析
- `POST /api/semantic` — 语义分析
- `POST /api/ir` — IR 生成
- `POST /api/asm` — 汇编生成
- `POST /api/asmrun` — 汇编、链接、运行（依赖本机工具链）
- `POST /api/pipeline` — 全流水线执行（Lexer → Parser → Semantic → IR → Assembly）
- `POST /api/download` — 下载文本内容（桌面模式保存文件）

## 运行方式

### 开发模式（浏览器）

```bash
pip install flask
python web_app.py
```

然后打开浏览器访问:

```text
http://127.0.0.1:5000
```

### 桌面应用模式（原生窗口）

```bash
pip install flask pywebview
python main_app.py
```

### 打包为独立可执行文件

```bash
pip install pyinstaller
python build.py
```

最终输出位于 `dist/CompilerLab.exe`（Windows）或 `dist/CompilerLab`（Linux/macOS）。

## 语言特性

支持的语法包括：

- 函数定义与参数列表
- `let` / `let mut` 变量声明
- `i32` 基本类型与数组类型 `[T; N]`
- 表达式、算术运算、比较运算
- `if/else`、`while`、`for`、`loop`
- `break` / `continue`
- `return` 带/不带表达式
- 函数调用与参数类型检查
- 数组访问与赋值

语义检查包括：

- 作用域与变量重影
- 未声明变量 / 未初始化变量
- 不可变变量修改
- 类型不匹配
- 函数参数个数与类型匹配
- 返回类型一致性
- 循环上下文的 `break` / `continue`

## 核心实现说明

- `lexer.py` 负责将源代码拆成 Token。支持关键字、标识符、数字、运算符、分隔符和注释。
- `parser.py` 使用递归下降法构建 AST，并支持可视化跟踪器 `ParserTracer`。
- `semantic.py` 实现符号表、作用域栈、参数重影、类型检查与语义错误码。
- `ir_generator.py` 生成类型安全的 `Quadruple` IR，支持临时变量、标签、函数调用与数组操作。
- `assembly_generator.py` 将四元组翻译为 NASM x86-64 代码，自动分配栈帧并支持 `receive_param`、`array_get`、`array_set` 等指令。
- `templates/index.html` 提供现代化的交互界面，内置 D3.js 和 TailwindCSS。
- `main_app.py` 使用 PyWebView 打开本地 Flask 页面，提供本地文件保存功能。

## 测试用例

- `testcases/` 目录现已按章节拆分为 `*_valid.rs` 和 `*_error.rs` 测试文件。
- `test_ir_pipeline.py` 用于回归测试 Lexer / Parser / Semantic / IR / Assembly 流水线。

## 依赖

- `flask`
- `pywebview`（可选，桌面模式）
- `pyinstaller`（可选，打包）

## 备注

- 如果项目目录中包含 `compiler_tools/`，后端会自动把该目录加入 `PATH`，以便发现 `nasm.exe`、`golink.exe` 等工具。
- `api/asmrun` 依赖本机 `nasm` 与链接器（`golink`、`gcc` 或 `clang`）。
- 前端可通过 `api/pipeline` 执行完整编译流水线并获取语法树、符号表、四元组、汇编等数据。
