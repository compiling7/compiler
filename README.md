# 类Rust词法和语法分析工具

一个基于Python实现的类Rust语言词法和语法分析工具，支持可视化AST输出。

## 功能特性

### 词法分析

- 支持关键字: `fn`, `let`, `mut`, `if`, `else`, `while`, `return`, `i32`, `for`, `in`, `loop`, `break`, `continue`
- 支持标识符: `(字母|_)(字母|数字|_)*`
- 支持数值常量
- 支持运算符: `+`, `-`, `*`, `/`, `==`, `>`, `>=`, `<`, `<=`, `!=`,  `&`
- 支持特殊符号:`->`,.,..
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

## 项目结构

```
compiler/
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
```

## 运行方式

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

## 语言规范

### 词法规则

| 类型   | 规则                                                                       |
| ------ | -------------------------------------------------------------------------- |
| 关键字 | i32, let, if, else, while, return, mut, fn, for, in, loop, break, continue |
| 标识符 | (字母\|_)(字母\|数字\|_)*                                                |
| 数值   | 数字(数字)*                                                                |
| 赋值号 | =                                                                          |
| 算符   | +, -, *, /, ==, >, >=, <, <=, !=, &, ->                                    |
| 界符   | (, ), {, }, [, ]                                                           |
| 分隔符 | ;, :, ,                                                                    |
| 注释   | // ... \n, /* ... */                                                       |

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
