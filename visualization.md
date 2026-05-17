● 项目可视化方案

  基于对现有代码的全面分析，我已理解项目的完整结构和各模块职责。以下是针对词法分析、语法分析和AST图像三个维度的可视化方案。

  ---
  一、整体架构

  在当前 main.py 的 Tkinter GUI 基础上，将右侧输出面板升级为多标签页布局（Notebook），包含三个可视化视图：

  ┌─────────────────────────────────────────────────┐
  │  类Rust词法和语法分析工具                         │
  ├──────────────────────┬──────────────────────────┤
  │                      │ [词法分析] [语法分析] [AST] │
  │  源代码输入          ├──────────────────────────┤
  │  (ScrolledText)      │                          │
  │                      │  可视化输出区域            │
  │                      │  (Canvas / Treeview)      │
  │                      │                          │
  ├──────────────────────┴──────────────────────────┤
  │ [词法分析]  [语法分析]  [清空结果]                │
  │ 状态栏: 完成 / 错误信息                           │
  └─────────────────────────────────────────────────┘

  ---
  二、词法分析可视化

  目标：将词法分析结果以直观、结构化的方式呈现，区分不同的 Token 类型。

  方案 A：着色 Token 流（主方案）

  在 Canvas 上绘制源码行，用不同颜色高亮每个 Token，鼠标悬停显示详细信息。

  颜色映射方案：

  | Token 类型                            | 颜色           | 示例        |
  |-------------------------------------|--------------|-----------|
  | 关键字 (fn, let, if, while, return...) | #569CD6 (蓝色) | fn main   |
  | 标识符 (ID)                            | 黑色           | main      |
  | 数字字面量                               | #B5CEA8 (绿色) | 10        |
  | 运算符 (+, -, =, ==...)                | #D4D4D4 (浅灰) | =         |
  | 定界符 ({, }, (, ), ;...)              | #FFD700 (金色) | {         |
  | 类型 (i32)                            | #4EC9B0 (蓝绿) | i32       |
  | 错误 Token                            | 红色背景高亮       | % (未定义符号) |

  交互方式：
  fn main() -> i32 {          ← 源码逐行渲染
  ├─ fn  [关键字]  (1,1)
  ├─ main [标识符] (1,4)
  ├─ ->  [箭头]    (1,9)
  ├─ i32  [类型]    (1,12)
  └─ {    [左大括号] (1,16)
  - 点击某个 Token → 在底部信息栏显示 类型: 关键字 | 值: fn | 位置: (1,1)
  - 右侧显示 Token 表格（Treeview 控件）：列 = 序号 | Token类型 | 值 | 行 | 列

  方案 B：Token 表格 + 统计（备选，与 A 并存）

  在树形表格显示的基础上，增加统计信息区域：
  === 词法分析统计 ===
  总 Token 数: 23
  关键字: 5 | 标识符: 7 | 数字: 3 | 运算符: 4 | 定界符: 4
  错误: 0
  分析耗时: 0.002s

  ---
  三、语法分析可视化

  目标：展示语法分析的结果——即语法结构（语法树/层次结构）。

  现有 visualization.py 中的三种文本输出已经可以作为基础，但需要将其图形化。

  方案：交互式语法树（Canvas 绘图）

  将 format_syntax_structure() 输出的缩进结构渲染为可展开/折叠的树形图。

  渲染方式：
  Program
  └── FunctionDecl: main
      ├── ParameterList
      │   └── Param: x
      │       └── Type: i32
      ├── ReturnType
      │   └── Type: i32
      └── Block
          ├── VarDeclStmt: x
          │   ├── Type: i32
          │   └── Init: NumberLiteral(10)
          ├── AssignStmt
          │   ├── LValue: y
          │   └── BinaryExpr: +
          │       ├── LValue: x
          │       └── NumberLiteral(20)
          └── IfStmt
              ├── BinaryExpr: >
              │   ├── LValue: y
              │   └── NumberLiteral(10)
              ├── Block (then)
              │   └── ReturnStmt
              │       └── NumberLiteral(1)
              └── Block (else)
                  └── ReturnStmt
                      └── NumberLiteral(0)

  交互设计：
  - 每个节点渲染为圆角矩形卡片，内部显示节点类型
  - 叶子节点（如 NumberLiteral、LValue）显示具体值
  - 点击节点 → 高亮并显示详细信息
  - 线条连接父子节点（Bezier 曲线）
  - 支持水平滚动（大 AST）和缩放（鼠标滚轮）

  节点卡片样式：
  ┌──────────────┐
  │  VarDeclStmt  │  ← 浅蓝背景
  │  name = "x"   │  ← 次要属性
  │  type = "i32" │
  └──────┬───────┘
         │
  ┌──────┴───────┐
  │ NumberLiteral │
  │ value = 10    │
  └──────────────┘

  颜色分类：
  - 声明节点（FunctionDecl, VarDeclStmt）→ 浅蓝 #D6EAF8
  - 语句节点（IfStmt, WhileStmt, ReturnStmt）→ 浅绿 #D5F5E3
  - 表达式节点（BinaryExpr, NumberLiteral）→ 浅黄 #FEF9E7
  - 程序/块节点（Program, Block）→ 浅紫 #E8DAEF

  ---
  四、AST 图像可视化

  目标：将抽象语法树绘制为纯图形化的树状图，类似于 Graphviz 的输出效果，但使用 Tkinter Canvas 原生实现。

  核心算法

  布局算法 — Reingold-Tilford 分层树布局：

  步骤:
  1. 后序遍历计算每个节点的子树宽度和水平位置
  2. 同级节点间距 = NODE_GAP（40px）
  3. 相邻子树不重叠（冲突检测 + 偏移调整）
  4. 垂直间距 = LEVEL_GAP（80px）
  5. 绘制贝塞尔曲线连接父子节点

  节点绘制：
          ┌──────────────────────┐
          │    FunctionDecl       │  ← 节点标题
          │    name: "main"       │  ← 属性行
          │    return: "i32"      │
          └──────────┬───────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
   ┌───┴───┐   ┌────┴────┐   ┌───┴───┐
   │ Param │   │  Type   │   │ Block │
   │ x:i32 │   │  i32    │   │  ...  │
   └───────┘   └─────────┘   └───────┘

  交互功能

  | 功能    | 实现方式                             |
  |-------|----------------------------------|
  | 平移    | 鼠标拖拽 Canvas                      |
  | 缩放    | Ctrl + 滚轮（0.5x ~ 2.0x）           |
  | 展开/折叠 | 点击节点折叠其子树，适合大 AST                |
  | 节点详情  | 双击节点弹出详情窗口                       |
  | 导出    | 保存为 PostScript（Canvas 原生支持 .eps） |
  | 搜索    | Ctrl+F 搜索节点名，自动定位高亮              |

  小 AST 适配（非缩放模式）

  对于较小的 AST（如单个函数），使用自适应布局自动居中，自动计算窗口尺寸，直接填满视图。

  ---
  五、具体代码实现结构

  建议新建 visualizer_gui.py 模块，包含以下类：

  visualizer_gui.py
  ├── TokenViewer(ttk.Frame)         # 词法分析可视化
  │   ├── _render_colored_tokens()   # 着色 Token 渲染
  │   ├── _render_token_table()      # Token 表格
  │   └── _render_stats()            # 统计信息
  │
  ├── SyntaxTreeViewer(ttk.Frame)    # 语法树可视化
  │   ├── _build_tree()              # 从 AST 构建树数据
  │   ├── _draw_tree()               # Canvas 绘制
  │   └── _on_node_click()           # 交互处理
  │
  ├── ASTGraphViewer(Canvas)         # AST 图像可视化
  │   ├── layout_tree()              # Reingold-Tilford 布局
  │   ├── draw_nodes()               # 绘制节点卡片
  │   ├── draw_edges()               # 绘制连接线
  │   ├── zoom_to_fit()              # 自适应缩放
  │   └── export_image()             # 导出为 EPS
  │
  └── TreeLayoutEngine               # 树布局引擎
      ├── compute_positions()        # 计算节点位置
      ├── resolve_conflicts()        # 解决子树重叠
      └── contour()                  # 子树轮廓计算

  对 main.py 的改动：
  - 将输出区域从单 ScrolledText 升级为 ttk.Notebook + 三个标签页
  - 按钮点击后切换到对应标签页
  - 词法分析结果显示在 TokenViewer 标签页
  - 语法分析结果显示在 SyntaxTreeViewer 标签页
  - AST 图像显示在 ASTGraphViewer 标签页

  ---
  六、实施步骤（推荐顺序）

  | 步骤  | 内容                                    | 预计工作量 |
  |-----|---------------------------------------|-------|
  | 1   | 改造 main.py，添加 Notebook 多标签布局          | 1h    |
  | 2   | 实现 TokenViewer（着色 Token + 表格）         | 2h    |
  | 3   | 实现 SyntaxTreeViewer（树形缩进 + Canvas 绘制） | 3h    |
  | 4   | 实现 TreeLayoutEngine（布局算法）             | 3h    |
  | 5   | 实现 ASTGraphViewer（节点/边绘制 + 交互）        | 4h    |
  | 6   | 集成测试 + 边界情况处理（空程序、错误恢复）               | 1h    |

  总预估：14h

  ---
  七、设计要点说明

  1. 纯标准库：所有可视化全部基于 tkinter.Canvas，不引入任何第三方依赖，符合项目现有的 requirements.txt 约束。
  2. 渐进式渲染：对于深度较大的 AST（如嵌套 if/while），采用分层渲染策略，默认只展开前 3 层，用户可手动展开更深节点。
  3. 错误友好：当词法/语法错误时，在对应视图上高亮错误位置，并提供清晰的错误信息提示，而非直接清空输出。
  4. 性能：对于中等规模 AST（~200 节点），Canvas 绘制应在 100ms 内完成。如超过此规模，可考虑分块渲染优化。
