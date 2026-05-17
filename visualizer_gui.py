"""GUI visualization for Rust-like language lexer, parser and AST"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import math

from ast import *
from token_types import *


# ─────────────────────────────────────────────
# Color scheme
# ─────────────────────────────────────────────
TOKEN_COLORS = {
    "FN": "#569CD6",
    "LET": "#569CD6",
    "IF": "#569CD6",
    "ELSE": "#569CD6",
    "WHILE": "#569CD6",
    "RETURN": "#569CD6",
    "MUT": "#569CD6",
    "I32": "#4EC9B0",
    "FOR": "#569CD6",
    "IN": "#569CD6",
    "LOOP": "#569CD6",
    "BREAK": "#569CD6",
    "CONTINUE": "#569CD6",
    "ID": "#000000",
    "NUM": "#B5CEA8",
    "EOF": "#888888",
    "ERROR": "#FF0000",
    "=": "#D4D4D4",
    "+": "#D4D4D4",
    "-": "#D4D4D4",
    "*": "#D4D4D4",
    "/": "#D4D4D4",
    "==": "#D4D4D4",
    ">": "#D4D4D4",
    ">=": "#D4D4D4",
    "<": "#D4D4D4",
    "<=": "#D4D4D4",
    "!=": "#D4D4D4",
    "(": "#FFD700",
    ")": "#FFD700",
    "{": "#FFD700",
    "}": "#FFD700",
    "[": "#FFD700",
    "]": "#FFD700",
    ";": "#FFD700",
    ":": "#FFD700",
    ",": "#FFD700",
    "->": "#D4D4D4",
    "&": "#D4D4D4",
    ".": "#D4D4D4",
    "..": "#D4D4D4",
    "..=": "#D4D4D4",
    "#": "#888888",
}

NODE_COLORS = {
    "Program": {"bg": "#E8DAEF", "border": "#9B59B6"},
    "FunctionDecl": {"bg": "#D6EAF8", "border": "#2980B9"},
    "Param": {"bg": "#D6EAF8", "border": "#2980B9"},
    "Type": {"bg": "#F0F0F0", "border": "#95A5A6"},
    "Block": {"bg": "#E8DAEF", "border": "#9B59B6"},
    "EmptyStmt": {"bg": "#F0F0F0", "border": "#95A5A6"},
    "ReturnStmt": {"bg": "#D5F5E3", "border": "#27AE60"},
    "VarDeclStmt": {"bg": "#D6EAF8", "border": "#2980B9"},
    "AssignStmt": {"bg": "#D6EAF8", "border": "#2980B9"},
    "ExprStmt": {"bg": "#D6EAF8", "border": "#2980B9"},
    "IfStmt": {"bg": "#D5F5E3", "border": "#27AE60"},
    "WhileStmt": {"bg": "#D5F5E3", "border": "#27AE60"},
    "BinaryExpr": {"bg": "#FEF9E7", "border": "#F39C12"},
    "LValue": {"bg": "#FEF9E7", "border": "#F39C12"},
    "NumberLiteral": {"bg": "#FEF9E7", "border": "#F39C12"},
    "FuncCall": {"bg": "#FEF9E7", "border": "#F39C12"},
    "UnaryMinus": {"bg": "#FEF9E7", "border": "#F39C12"},
}

DEFAULT_NODE_COLOR = {"bg": "#F0F0F0", "border": "#95A5A6"}

TOKEN_TYPE_LABELS = {
    "FN": "关键字", "LET": "关键字", "IF": "关键字", "ELSE": "关键字",
    "WHILE": "关键字", "RETURN": "关键字", "MUT": "关键字",
    "I32": "类型", "FOR": "关键字", "IN": "关键字",
    "LOOP": "关键字", "BREAK": "关键字", "CONTINUE": "关键字",
    "ID": "标识符", "NUM": "数字",
    "EOF": "结束符", "ERROR": "错误",
    "=": "运算符", "+": "运算符", "-": "运算符",
    "*": "运算符", "/": "运算符", "==": "运算符",
    ">": "运算符", ">=": "运算符", "<": "运算符",
    "<=": "运算符", "!=": "运算符",
    "(": "定界符", ")": "定界符", "{": "定界符", "}": "定界符",
    "[": "定界符", "]": "定界符", ";": "定界符",
    ":": "定界符", ",": "定界符",
    "->": "箭头", "&": "运算符",
    ".": "运算符", "..": "运算符", "..=": "运算符",
    "#": "特殊符号",
}


def get_token_category(token_type):
    """Get human-readable token category"""
    return TOKEN_TYPE_LABELS.get(token_type, "其他")


def get_node_colors(node):
    """Get background and border colors for an AST node"""
    name = node.node_name
    return NODE_COLORS.get(name, DEFAULT_NODE_COLOR)


def get_node_title(node):
    """Get display title for an AST node"""
    if isinstance(node, FunctionDeclNode):
        return f"FunctionDecl: {node.name}"
    elif isinstance(node, VarDeclStmtNode):
        mut = "mut " if node.is_mutable else ""
        return f"let {mut}{node.name}"
    elif isinstance(node, ParamNode):
        return f"Param: {node.name}"
    elif isinstance(node, TypeNode):
        return f"Type: {node.type_name}"
    elif isinstance(node, BinaryExprNode):
        return f"BinaryExpr: {node.op}"
    elif isinstance(node, NumberLiteralNode):
        return f"Number: {node.value}"
    elif isinstance(node, LValueNode):
        return f"LValue: {node.name}"
    elif isinstance(node, FuncCallNode):
        return f"FuncCall: {node.name}()"
    elif isinstance(node, BlockStmtNode):
        return f"Block ({len(node.statements)} stmts)"
    elif isinstance(node, ReturnStmtNode):
        return "ReturnStmt"
    elif isinstance(node, IfStmtNode):
        return "IfStmt"
    elif isinstance(node, WhileStmtNode):
        return "WhileStmt"
    elif isinstance(node, AssignStmtNode):
        return "AssignStmt"
    elif isinstance(node, ExprStmtNode):
        return "ExprStmt"
    elif isinstance(node, UnaryMinusNode):
        return "UnaryMinus"
    elif isinstance(node, EmptyStmtNode):
        return "EmptyStmt"
    elif isinstance(node, ProgramNode):
        return f"Program ({len(node.declarations)} decls)"
    else:
        return node.node_name


def get_node_subtitle(node):
    """Get subtitle text for more detail"""
    if isinstance(node, FunctionDeclNode):
        ret = node.return_type.type_name if node.return_type else "void"
        return f"-> {ret}"
    elif isinstance(node, VarDeclStmtNode):
        parts = []
        if node.var_type:
            parts.append(f": {node.var_type.type_name}")
        if node.init_expr:
            parts.append("= ...")
        return " ".join(parts)
    elif isinstance(node, BinaryExprNode):
        return f"operator: '{node.op}'"
    elif isinstance(node, NumberLiteralNode):
        return f"value: {node.value}"
    elif isinstance(node, LValueNode):
        return f"name: '{node.name}'"
    elif isinstance(node, FuncCallNode):
        return f"args: {len(node.args)}"
    elif isinstance(node, BlockStmtNode):
        return ""
    elif isinstance(node, IfStmtNode):
        return "else" if node.else_block else ""
    elif isinstance(node, ReturnStmtNode):
        return "" if node.expr else "(void)"
    elif isinstance(node, TypeNode):
        return node.type_name
    return ""


def get_ast_children(node):
    """Get children of an AST node for tree traversal"""
    children = []
    if isinstance(node, ProgramNode):
        children = node.declarations
    elif isinstance(node, FunctionDeclNode):
        if node.params:
            children.append(node.params)  # list -> special handling
        if node.return_type:
            children.append(node.return_type)
        if node.body:
            children.append(node.body)
    elif isinstance(node, ParamNode):
        if node.param_type:
            children.append(node.param_type)
    elif isinstance(node, BlockStmtNode):
        children = node.statements
    elif isinstance(node, ReturnStmtNode):
        if node.expr:
            children.append(node.expr)
    elif isinstance(node, VarDeclStmtNode):
        if node.var_type:
            children.append(node.var_type)
        if node.init_expr:
            children.append(node.init_expr)
    elif isinstance(node, AssignStmtNode):
        children = [node.left, node.value]
    elif isinstance(node, ExprStmtNode):
        if node.expr:
            children.append(node.expr)
    elif isinstance(node, IfStmtNode):
        children.append(node.condition)
        children.append(node.then_block)
        if node.else_block:
            children.append(node.else_block)
    elif isinstance(node, WhileStmtNode):
        children = [node.condition, node.body]
    elif isinstance(node, BinaryExprNode):
        children = [node.left, node.right]
    elif isinstance(node, FuncCallNode):
        children = node.args
    elif isinstance(node, UnaryMinusNode):
        if node.expr:
            children.append(node.expr)
    return children


# ─────────────────────────────────────────────
# TokenViewer - Lexical Analysis Tab
# ─────────────────────────────────────────────

class TokenViewer(ttk.Frame):
    """Visual panel for lexical analysis results"""

    def __init__(self, parent):
        super().__init__(parent)
        self.tokens = []
        self.source = ""

        # Top: source code with colored tokens (with scrollbars)
        code_container = tk.Frame(self, bg="white", highlightthickness=1,
                                   highlightbackground="#ccc")
        code_container.pack(fill=tk.X, padx=5, pady=(5, 2))

        self.code_canvas = tk.Canvas(code_container, bg="white", height=180,
                                      highlightthickness=0)
        code_v_scroll = ttk.Scrollbar(code_container, orient=tk.VERTICAL,
                                       command=self.code_canvas.yview)
        code_h_scroll = ttk.Scrollbar(code_container, orient=tk.HORIZONTAL,
                                       command=self.code_canvas.xview)
        self.code_canvas.configure(yscrollcommand=code_v_scroll.set,
                                    xscrollcommand=code_h_scroll.set)

        self.code_canvas.grid(row=0, column=0, sticky="nsew")
        code_v_scroll.grid(row=0, column=1, sticky="ns")
        code_h_scroll.grid(row=1, column=0, sticky="ew")
        code_container.grid_rowconfigure(0, weight=1)
        code_container.grid_columnconfigure(0, weight=1)

        # Token table area
        table_label = ttk.Label(self, text="Token 序列", font=("Arial", 10, "bold"))
        table_label.pack(anchor=tk.W, padx=5, pady=(5, 2))

        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Treeview for token table
        columns = ("序号", "Token类型", "分类", "值", "行", "列")
        self.token_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                        height=8)
        for col in columns:
            self.token_tree.heading(col, text=col)
            if col in ("序号", "行", "列"):
                self.token_tree.column(col, width=50, anchor=tk.CENTER)
            elif col == "Token类型":
                self.token_tree.column(col, width=80, anchor=tk.CENTER)
            elif col == "分类":
                self.token_tree.column(col, width=60, anchor=tk.CENTER)
            elif col == "值":
                self.token_tree.column(col, width=150)

        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=v_scroll.set)
        self.token_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom: stats
        self.stats_label = ttk.Label(self, text="就绪", font=("Arial", 9))
        self.stats_label.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Info bar for selected token
        self.info_label = ttk.Label(self, text="", font=("Consolas", 9), foreground="#555")
        self.info_label.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.token_tree.bind("<<TreeviewSelect>>", self._on_token_select)
        self.code_rects = []  # (rect_id, text_id, token) tuples

    def display(self, source, tokens):
        """Display token visualization"""
        self.source = source
        self.tokens = tokens
        self._clear()
        self.update_idletasks()  # Ensure proper layout before rendering
        self._render_code()
        self._render_table()
        self._render_stats()

    def _clear(self):
        """Clear all displayed content"""
        self.code_canvas.delete("all")
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
        self.code_rects = []
        self.info_label.config(text="")

    def _render_code(self):
        """Render source code with colored tokens on canvas"""
        canvas = self.code_canvas
        canvas.delete("all")

        if not self.tokens:
            canvas.create_text(10, 20, anchor=tk.W, text="无 Token 数据",
                               font=("Consolas", 10), fill="#999")
            return

        # We need to render tokens in source order (excluding EOF)
        display_tokens = [t for t in self.tokens if t.type != TT_EOF]

        if not display_tokens:
            canvas.create_text(10, 20, anchor=tk.W, text="(空)",
                               font=("Consolas", 10), fill="#999")
            return

        font = tkfont.Font(family="Consolas", size=11)
        line_height = font.metrics("linespace") + 4
        char_width = font.measure("0")

        x, y = 10, 10
        max_width = canvas.winfo_width() - 20
        if max_width < 100:
            max_width = 600

        # Group tokens by line for display
        tokens_by_line = {}
        for t in display_tokens:
            tokens_by_line.setdefault(t.line, []).append(t)

        for line_num in sorted(tokens_by_line.keys()):
            x = 10
            line_tokens = tokens_by_line[line_num]

            for token in line_tokens:
                token_text = token.value
                color = TOKEN_COLORS.get(token.type, "#000000")

                # Draw token background highlight
                text_width = font.measure(token_text)
                text_id = canvas.create_text(x, y, anchor=tk.NW, text=token_text,
                                              font=font, fill=color, tags="token")

                # Draw rounded rect behind text
                pad_x = 2
                pad_y = 1
                rect_id = canvas.create_rectangle(
                    x - pad_x, y - pad_y,
                    x + text_width + pad_x, y + line_height + pad_y,
                    outline="", fill="", tags="bg"
                )

                self.code_rects.append((rect_id, text_id, token))

                # Bind hover events
                canvas.tag_bind(text_id, "<Enter>",
                                lambda e, t=token, r=rect_id: self._on_token_hover(t, r))
                canvas.tag_bind(text_id, "<Leave>",
                                lambda e, r=rect_id: self._on_token_leave(r))

                x += text_width + 8

            y += line_height + 6

        # Update canvas scroll region
        bbox = canvas.bbox("all")
        if bbox:
            canvas.configure(scrollregion=bbox)

    def _on_token_hover(self, token, rect_id):
        """Handle token hover - highlight background"""
        self.code_canvas.itemconfig(rect_id, fill="#E8E8E8")
        self.info_label.config(
            text=f"类型: {token.type}  |  值: '{token.value}'  |  位置: 第{token.line}行, 第{token.column}列"
        )

    def _on_token_leave(self, rect_id):
        """Handle token leave - remove highlight"""
        self.code_canvas.itemconfig(rect_id, fill="")

    def _render_table(self):
        """Render token table"""
        tree = self.token_tree
        display_tokens = [t for t in self.tokens if t.type != TT_EOF]
        for i, token in enumerate(display_tokens, 1):
            category = get_token_category(token.type)
            tree.insert("", tk.END, values=(
                i, token.type, category, token.value, token.line, token.column
            ))

    def _render_stats(self):
        """Render token statistics"""
        display_tokens = [t for t in self.tokens if t.type != TT_EOF]
        error_tokens = [t for t in self.tokens if t.type == TT_ERROR]

        # Count by category
        categories = {}
        for t in display_tokens:
            cat = get_token_category(t.type)
            categories[cat] = categories.get(cat, 0) + 1

        stats_parts = [f"总 Token 数: {len(display_tokens)}"]
        for cat, count in sorted(categories.items()):
            stats_parts.append(f"{cat}: {count}")

        if error_tokens:
            stats_parts.append(f"错误: {len(error_tokens)} ⚠")

        self.stats_label.config(text="  |  ".join(stats_parts))

    def _on_token_select(self, event):
        """Handle token table selection"""
        selection = self.token_tree.selection()
        if selection:
            values = self.token_tree.item(selection[0], "values")
            if values:
                self.info_label.config(
                    text=f"序号: {values[0]}  |  类型: {values[1]}  |  分类: {values[2]}  |  "
                         f"值: '{values[3]}'  |  位置: 第{values[4]}行, 第{values[5]}列"
                )

    def clear(self):
        """Clear the view"""
        self._clear()
        self.stats_label.config(text="就绪")


# ─────────────────────────────────────────────
# Tree-level data structures for syntax/AST views
# ─────────────────────────────────────────────

class LayoutNode:
    """Node in the layout tree for visualization"""
    def __init__(self, ast_node, children=None, title="", subtitle="", colors=None):
        self.ast_node = ast_node
        self.children = children or []
        self.title = title
        self.subtitle = subtitle
        self.colors = colors or DEFAULT_NODE_COLOR
        self.x = 0          # computed center x
        self.y = 0          # computed center y
        self.width = 120    # node width
        self.height = 50    # node height
        self.mod = 0        # modifier for children
        self.contour = None # contour cache
        self.collapsed = False
        self.canvas_id = None


def build_layout_tree(ast_root):
    """Convert AST to a layout tree for canvas rendering"""
    if ast_root is None:
        return None

    title = get_node_title(ast_root)
    subtitle = get_node_subtitle(ast_root)
    colors = get_node_colors(ast_root)

    raw_children = get_ast_children(ast_root)

    # Flatten list children (e.g. params that are a list)
    flat_children = []
    for child in raw_children:
        if isinstance(child, list):
            for c in child:
                if isinstance(c, ASTNode):
                    flat_children.append(c)
        elif isinstance(child, ASTNode):
            flat_children.append(child)

    child_nodes = []
    for child in flat_children:
        layout_child = build_layout_tree(child)
        if layout_child:
            child_nodes.append(layout_child)

    return LayoutNode(ast_root, child_nodes, title, subtitle, colors)


# ─────────────────────────────────────────────
# SyntaxTreeViewer - Syntax Analysis Tab
# ─────────────────────────────────────────────

class SyntaxTreeViewer(ttk.Frame):
    """Interactive syntax tree visualization"""

    NODE_WIDTH = 140
    NODE_HEIGHT = 40
    H_GAP = 20
    V_GAP = 60

    def __init__(self, parent):
        super().__init__(parent)

        # Canvas with scrollbars
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white",
                                 xscrollcommand=self.h_scroll.set,
                                 yscrollcommand=self.v_scroll.set)
        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Status
        self.status_label = ttk.Label(self, text="就绪", font=("Arial", 9))
        self.status_label.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<Button-4>", self._on_zoom_linux_up)
        self.canvas.bind("<Button-5>", self._on_zoom_linux_down)

        self._drag_start = None
        self._scale = 1.0
        self.root_node = None
        self.selected_id = None

    def display(self, ast_root):
        """Display the syntax tree"""
        self.canvas.delete("all")
        self.root_node = None

        if ast_root is None:
            self.canvas.create_text(10, 20, anchor=tk.W, text="无 AST 可显示",
                                    font=("Consolas", 10), fill="#999")
            self.status_label.config(text="无 AST")
            return

        self.update_idletasks()  # Ensure proper layout before rendering
        self.root_node = build_layout_tree(ast_root)
        self._layout()
        self._draw()
        self._fit_to_view()
        self.status_label.config(text="语法树已显示 | 拖拽平移 | 滚轮缩放")

    def _layout(self):
        """Compute tree layout using simple centered tree algorithm"""
        if not self.root_node:
            return

        # First pass: calculate subtree widths
        self._calc_width(self.root_node, 0)

        # Second pass: calculate positions (centered)
        total_width = self.root_node.width
        self._calc_positions(self.root_node, -total_width / 2, 0)

    def _calc_width(self, node, depth):
        """Calculate width of each subtree (post-order)"""
        node.y = depth * (self.NODE_HEIGHT + self.V_GAP)

        if not node.children or node.collapsed:
            node.width = self.NODE_WIDTH + self.H_GAP
            return node.width

        total_width = 0
        for child in node.children:
            self._calc_width(child, depth + 1)
            total_width += child.width

        node.width = max(self.NODE_WIDTH + self.H_GAP, total_width)
        return node.width

    def _calc_positions(self, node, x_offset, parent_x):
        """Calculate x positions (pre-order, centered)"""
        if not node.children or node.collapsed:
            node.x = x_offset + node.width / 2
            return

        # Distribute children
        child_x = x_offset
        for child in node.children:
            self._calc_positions(child, child_x, node.x)
            child_x += child.width

        # Center parent over children
        first = node.children[0]
        last = node.children[-1]
        node.x = (first.x + last.x) / 2

    def _draw(self):
        """Draw the tree on canvas"""
        if not self.root_node:
            return
        self._draw_node(self.root_node)

    def _draw_node(self, node):
        """Recursively draw a node and its children"""
        c = self.canvas
        x, y = node.x, node.y
        w, h = self.NODE_WIDTH, self.NODE_HEIGHT

        # Draw connection to parent if not root
        # (connections are drawn from child up to parent)

        # Draw node rectangle
        colors = node.colors
        rect = c.create_rectangle(
            x - w / 2, y, x + w / 2, y + h,
            fill=colors["bg"], outline=colors["border"], width=2,
            tags="node"
        )

        # Draw title text
        title_font = tkfont.Font(family="Arial", size=9, weight="bold")
        c.create_text(x, y + h / 2 - 6, text=node.title, font=title_font,
                       fill="#333", tags="node")

        # Draw subtitle (if any)
        if node.subtitle:
            sub_font = tkfont.Font(family="Arial", size=8)
            c.create_text(x, y + h / 2 + 10, text=node.subtitle, font=sub_font,
                           fill="#666", tags="node")

        node.canvas_id = rect

        # Store node data with rect
        c.itemconfig(rect, tags=("node", f"node_{id(node)}"))

        # Draw children
        if node.children and not node.collapsed:
            for child in node.children:
                self._draw_node(child)

            # Draw edges (after children so they're on top)
            for child in node.children:
                cx, cy = child.x, child.y
                c.create_line(x, y + h, cx, cy, fill="#666", width=1.5,
                               tags="edge")

        # Bind click
        c.tag_bind(rect, "<Button-1>", lambda e, n=node: self._on_node_click(n))
        c.tag_bind(f"node_{id(node)}", "<Button-1>", lambda e, n=node: self._on_node_click(n))

    def _on_node_click(self, node):
        """Handle node click - show details"""
        self.selected_id = id(node)
        info = f"节点: {node.title}"
        if node.subtitle:
            info += f" | {node.subtitle}"
        if isinstance(node.ast_node, (NumberLiteralNode,)):
            info += f" | 值: {node.ast_node.value}"
        elif isinstance(node.ast_node, LValueNode):
            info += f" | 变量: {node.ast_node.name}"
        elif isinstance(node.ast_node, FunctionDeclNode):
            info += f" | 参数: {len(node.ast_node.params)}"
        self.status_label.config(text=info)

    def _on_press(self, event):
        """Start drag"""
        self._drag_start = (event.x, event.y)

    def _on_drag(self, event):
        """Handle canvas drag (pan)"""
        if self._drag_start:
            dx = event.x - self._drag_start[0]
            dy = event.y - self._drag_start[1]
            self.canvas.xview_scroll(int(-dx), tk.UNITS)
            self.canvas.yview_scroll(int(-dy), tk.UNITS)
            self._drag_start = (event.x, event.y)

    def _on_zoom(self, event):
        """Zoom with mouse wheel"""
        # Adjust scale factor (disabled for simplicity in syntax tree)
        pass

    def _on_zoom_linux_up(self, event):
        pass

    def _on_zoom_linux_down(self, event):
        pass

    def _fit_to_view(self):
        """Fit tree to view"""
        if not self.root_node:
            return
        bbox = self.canvas.bbox("all")
        if bbox:
            padding = 40
            expanded_bbox = (
                bbox[0] - padding, bbox[1] - padding,
                bbox[2] + padding, bbox[3] + padding
            )
            self.canvas.configure(scrollregion=expanded_bbox)

    def clear(self):
        """Clear the view"""
        self.canvas.delete("all")
        self.root_node = None
        self.status_label.config(text="就绪")


# ─────────────────────────────────────────────
# ASTGraphViewer - AST Image Tab
# ─────────────────────────────────────────────

class ASTGraphViewer(ttk.Frame):
    """Graphical AST tree visualization with advanced layout"""

    # Layout constants
    NODE_MIN_WIDTH = 130
    NODE_HEIGHT = 60
    H_GAP = 30
    V_GAP = 80
    PAD_LEFT = 20
    PAD_TOP = 20

    def __init__(self, parent):
        super().__init__(parent)

        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(toolbar, text="适合窗口", command=self._fit_to_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="放大", command=self._zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="缩小", command=self._zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="重置", command=self._reset_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="导出EPS", command=self._export_eps).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.collapse_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(toolbar, text="折叠模式", variable=self.collapse_mode,
                         command=self._toggle_collapse_mode).pack(side=tk.LEFT, padx=2)

        # Canvas with scrollbars
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white",
                                 xscrollcommand=self.h_scroll.set,
                                 yscrollcommand=self.v_scroll.set,
                                 highlightthickness=0)
        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Status bar
        self.status_label = ttk.Label(self, text="就绪", font=("Arial", 9))
        self.status_label.pack(fill=tk.X, padx=5, pady=(0, 5))

        # State
        self.root_node = None
        self._scale = 1.0
        self._drag_start = None
        self._selected_node = None
        self._collapse_mode = False
        self._node_map = {}  # id -> LayoutNode
        self._edge_ids = []
        self._node_rect_ids = {}

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel_up)
        self.canvas.bind("<Button-5>", self._on_mousewheel_down)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def display(self, ast_root):
        """Display the AST as a graphical tree"""
        self.canvas.delete("all")
        self._node_map = {}
        self._edge_ids = []
        self._node_rect_ids = {}
        self.root_node = None
        self._selected_node = None
        self._scale = 1.0

        if ast_root is None:
            self.canvas.create_text(20, 20, anchor=tk.W, text="无 AST 可显示",
                                    font=("Consolas", 12), fill="#999")
            self.status_label.config(text="无 AST")
            return

        self.update_idletasks()  # Ensure proper layout before rendering
        self.root_node = build_layout_tree(ast_root)
        self._build_node_map(self.root_node)
        self._layout_tree()
        self._draw_tree()
        self._fit_to_view()
        self.status_label.config(text="AST 图像已显示 | 滚轮缩放 | 拖拽平移 | 点击节点查看详情")

    def _build_node_map(self, node):
        """Build a map of node ids for quick lookup"""
        self._node_map[id(node)] = node
        for child in node.children:
            self._build_node_map(child)

    def _layout_tree(self):
        """Advanced tree layout algorithm"""
        if not self.root_node:
            return

        # Calculate text-based node dimensions first
        self._calc_node_sizes(self.root_node)

        # First pass: compute subtree widths (post-order)
        self._calc_subtree_width(self.root_node, 0)

        # Second pass: assign positions (pre-order)
        total_w = self.root_node.subtree_width
        self._assign_positions(self.root_node, -total_w / 2)

    def _calc_node_sizes(self, node):
        """Calculate node dimensions based on text content"""
        font_title = tkfont.Font(family="Arial", size=10, weight="bold")
        font_sub = tkfont.Font(family="Arial", size=9)

        title_w = font_title.measure(node.title)
        sub_w = font_sub.measure(node.subtitle) if node.subtitle else 0

        text_w = max(title_w, sub_w)
        node.width = max(self.NODE_MIN_WIDTH, text_w + 24)
        node.height = self.NODE_HEIGHT

    def _calc_subtree_width(self, node, depth):
        """Post-order: compute subtree width and y position"""
        node.y = depth * (self.NODE_HEIGHT + self.V_GAP) + self.PAD_TOP

        if not node.children or node.collapsed:
            node.subtree_width = node.width + self.H_GAP
            return node.subtree_width

        total_w = 0
        for child in node.children:
            self._calc_subtree_width(child, depth + 1)
            total_w += child.subtree_width

        node.subtree_width = max(node.width + self.H_GAP, total_w)
        return node.subtree_width

    def _assign_positions(self, node, x_start):
        """Pre-order: assign x positions, centering parent over children"""
        if not node.children or node.collapsed:
            node.x = x_start + node.subtree_width / 2
            return

        child_x = x_start
        for child in node.children:
            self._assign_positions(child, child_x)
            child_x += child.subtree_width

        # Center parent over children
        first = node.children[0]
        last = node.children[-1]
        node.x = (first.x + last.x) / 2

    def _draw_tree(self):
        """Draw the complete tree"""
        if not self.root_node:
            return

        # Draw edges first (behind nodes)
        self._draw_edges(self.root_node)

        # Draw nodes
        self._draw_node_rect(self.root_node)

    def _draw_edges(self, node):
        """Draw edges from node to its children"""
        if not node.children or node.collapsed:
            return

        x1, y1 = node.x, node.y + node.height
        colors = node.colors

        for child in node.children:
            x2, y2 = child.x, child.y

            # Draw bezier-like curve (quadratic)
            cy = (y1 + y2) / 2
            edge_id = self.canvas.create_line(
                x1, y1, x1, cy, x2, cy, x2, y2,
                fill="#999", width=2, smooth=True,
                tags="edge"
            )
            self._edge_ids.append(edge_id)

            # Recursively draw child edges
            self._draw_edges(child)

    def _draw_node_rect(self, node):
        """Draw a node with rounded-rectangle appearance"""
        c = self.canvas
        x, y, w, h = node.x, node.y, node.width, node.height
        colors = node.colors

        # Shadow
        shadow = c.create_rectangle(
            x - w / 2 + 3, y + 3, x + w / 2 + 3, y + h + 3,
            fill="#ddd", outline="", tags="node_shadow"
        )

        # Main rectangle
        rect_id = c.create_rectangle(
            x - w / 2, y, x + w / 2, y + h,
            fill=colors["bg"], outline=colors["border"], width=2,
            tags="node"
        )

        # Title text
        title_font = tkfont.Font(family="Arial", size=10, weight="bold")
        c.create_text(x, y + h / 2 - 8, text=node.title, font=title_font,
                       fill="#333", tags="node")

        # Subtitle text
        if node.subtitle:
            sub_font = tkfont.Font(family="Arial", size=9)
            c.create_text(x, y + h / 2 + 12, text=node.subtitle, font=sub_font,
                           fill="#666", tags="node")

        # Collapse indicator
        if node.children:
            self._draw_collapse_indicator(node)

        node.canvas_id = rect_id
        self._node_rect_ids[id(node)] = rect_id

        # Bind click event
        c.tag_bind(rect_id, "<Button-1>", lambda e, n=node: self._on_node_click(n))

        # Recursively draw children
        if node.children and not node.collapsed:
            for child in node.children:
                self._draw_node_rect(child)

    def _draw_collapse_indicator(self, node):
        """Draw +/- indicator for collapsible nodes"""
        c = self.canvas
        x, y = node.x + node.width / 2 - 10, node.y + 5
        r = 6
        fill = "#999" if not node.collapsed else "#aaa"
        c.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="#666", tags="node")
        c.create_text(x, y, text="−" if not node.collapsed else "+",
                       fill="white", font=("Arial", 8, "bold"), tags="node")

    def _on_node_click(self, node):
        """Handle node click"""
        if self.collapse_mode.get():
            # Toggle collapse
            node.collapsed = not node.collapsed
            self.canvas.delete("all")
            self._node_map = {}
            self._edge_ids = []
            self._node_rect_ids = {}
            self._build_node_map(self.root_node)
            self._layout_tree()
            self._draw_tree()
            self._fit_scrollregion()
            status = "折叠" if node.collapsed else "展开"
            self.status_label.config(text=f"{status}: {node.title}")
        else:
            # Select node
            self._selected_node = node

            # Highlight selected
            for nid, rid in self._node_rect_ids.items():
                n = self._node_map.get(nid)
                if n:
                    colors = n.colors
                    if n is node:
                        self.canvas.itemconfig(rid, outline="#E74C3C", width=3)
                    else:
                        self.canvas.itemconfig(rid, outline=colors["border"], width=2)

            # Show info
            info = f"选中: {node.title}"
            if node.subtitle:
                info += f" | {node.subtitle}"
            self.status_label.config(text=info)

    def _toggle_collapse_mode(self):
        """Toggle collapse mode on/off"""
        self._collapse_mode = self.collapse_mode.get()
        mode = "折叠" if self._collapse_mode else "选择"
        self.status_label.config(text=f"{mode}模式 | 点击节点进行{mode}")

    def _on_press(self, event):
        """Start dragging"""
        self._drag_start = (event.x, event.y)

    def _on_drag(self, event):
        """Handle drag (pan)"""
        if self._drag_start:
            dx = event.x - self._drag_start[0]
            dy = event.y - self._drag_start[1]
            self.canvas.xview_scroll(int(-dx), tk.UNITS)
            self.canvas.yview_scroll(int(-dy), tk.UNITS)
            self._drag_start = (event.x, event.y)

    def _on_release(self, event):
        """End drag"""
        self._drag_start = None

    def _on_mousewheel(self, event):
        """Zoom with mouse wheel (Windows/macOS)"""
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self._apply_zoom(scale_factor, event.x, event.y)

    def _on_mousewheel_up(self, event):
        """Zoom in (Linux)"""
        self._apply_zoom(1.1, event.x, event.y)

    def _on_mousewheel_down(self, event):
        """Zoom out (Linux)"""
        self._apply_zoom(0.9, event.x, event.y)

    def _apply_zoom(self, factor, x, y):
        """Apply zoom centered on mouse position"""
        self._scale *= factor
        self._scale = max(0.3, min(3.0, self._scale))

        # Get current view
        bbox = self.canvas.bbox("all")
        if not bbox:
            return

        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2

        self.canvas.scale("all", cx, cy, factor, factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _fit_scrollregion(self):
        """Update scrollregion to encompass all items with padding"""
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        padding = 40
        expanded = (
            bbox[0] - padding, bbox[1] - padding,
            bbox[2] + padding, bbox[3] + padding
        )
        self.canvas.configure(scrollregion=expanded)

    def _fit_to_view(self):
        """Fit tree to the visible area (redraw and auto-scale)"""
        if self.root_node is None:
            return

        # Save collapse states
        collapsed_ids = set()
        def collect_collapsed(node):
            if node.collapsed:
                collapsed_ids.add(id(node.ast_node))
            for child in node.children:
                collect_collapsed(child)
        collect_collapsed(self.root_node)

        # Redraw at scale 1.0
        self.canvas.delete("all")
        self._node_map = {}
        self._edge_ids = []
        self._node_rect_ids = {}
        self._scale = 1.0
        self._build_node_map(self.root_node)
        self._layout_tree()

        def restore_collapsed(node):
            if id(node.ast_node) in collapsed_ids:
                node.collapsed = True
            for child in node.children:
                restore_collapsed(child)
        restore_collapsed(self.root_node)

        self._draw_tree()
        self._fit_scrollregion()
        self.status_label.config(text="已适配窗口")

    def _zoom_in(self):
        """Zoom in button"""
        self._apply_zoom(1.2, 400, 300)

    def _zoom_out(self):
        """Zoom out button"""
        self._apply_zoom(0.8, 400, 300)

    def _reset_view(self):
        """Reset view to fit (redraw at scale 1.0)"""
        self._fit_to_view()
        self.status_label.config(text="视图已重置")

    def _on_canvas_resize(self, event):
        """Handle canvas resize"""
        pass

    def _export_eps(self):
        """Export canvas to EPS file"""
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".eps",
            filetypes=[("EPS files", "*.eps"), ("All files", "*.*")]
        )
        if path:
            try:
                self.canvas.postscript(file=path, colormode="color")
                self.status_label.config(text=f"已导出: {path}")
            except Exception as e:
                self.status_label.config(text=f"导出失败: {e}")

    def clear(self):
        """Clear the view"""
        self.canvas.delete("all")
        self.root_node = None
        self._node_map = {}
        self._edge_ids = []
        self._node_rect_ids = {}
        self._selected_node = None
        self.status_label.config(text="就绪")


# ─────────────────────────────────────────────
# ErrorDisplay - Error tab content
# ─────────────────────────────────────────────

class ErrorDisplay(ttk.Frame):
    """Display errors in a formatted way"""

    def __init__(self, parent):
        super().__init__(parent)

        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10),
                             bg="#FFF5F5", fg="#C0392B", state=tk.DISABLED,
                             relief=tk.FLAT)
        v_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=v_scroll.set)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def show_errors(self, errors, title="错误信息"):
        """Display error messages"""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        self.text.insert(tk.END, f"⚠ {title}\n", "title")
        self.text.insert(tk.END, "=" * 50 + "\n\n")

        self.text.tag_config("title", font=("Arial", 12, "bold"), foreground="#C0392B")
        self.text.tag_config("error", foreground="#C0392B")
        self.text.tag_config("index", foreground="#888")

        for i, err in enumerate(errors, 1):
            self.text.insert(tk.END, f"[{i}] ", "index")
            self.text.insert(tk.END, f"{err}\n\n", "error")

        self.text.config(state=tk.DISABLED)

    def show_message(self, message, title="信息"):
        """Display a success/info message"""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        self.text.insert(tk.END, f"✓ {title}\n", "title")
        self.text.insert(tk.END, "=" * 50 + "\n\n")
        self.text.insert(tk.END, f"{message}\n")

        self.text.tag_config("title", font=("Arial", 12, "bold"), foreground="#27AE60")

        self.text.config(state=tk.DISABLED)

    def clear(self):
        """Clear the display"""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.config(state=tk.DISABLED)
