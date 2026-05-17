"""GUI visualization for Rust-like language — Academic Minimal + VSCode + Apple HIG

Academic Minimal + VSCode IDE + Apple Human Interface Design hybrid style.
Light-gray background, 16px rounded corners, Inter font stack, clean structure.
"""

import sys
import tkinter as tk
from tkinter import ttk, font as tkfont

from ast import *
from token_types import *

# ═══════════════════════════════════════════════
# Design Tokens
# ═══════════════════════════════════════════════

# ── Light theme ──
LIGHT = {
    "bg_primary": "#f8f9fa",
    "bg_secondary": "#ffffff",
    "bg_tertiary": "#f0f1f3",
    "bg_hover": "#e8eaed",
    "bg_selected": "#e2e8f0",
    "text_primary": "#1a1a2e",
    "text_secondary": "#5f6368",
    "text_muted": "#9aa0a6",
    "text_inverse": "#ffffff",
    "border_light": "#e2e5e9",
    "border_normal": "#cfd3d8",
    "accent_blue": "#2962ff",
    "accent_blue_hover": "#1a56db",
    "accent_green": "#0f9d58",
    "accent_red": "#d93025",
    "accent_yellow": "#f9ab00",
    "accent_purple": "#7c4dff",
    "shadow": "#d4d6d9",
    "code_bg": "#fafbfc",
    "card_bg": "#ffffff",
}


# ── Platform-safe font families ──
if sys.platform == "win32":
    _UI_FONT = "Segoe UI"
    _CODE_FONT = "Consolas"
elif sys.platform == "darwin":
    _UI_FONT = "Inter, Helvetica Neue"
    _CODE_FONT = "SF Mono, Menlo"
else:
    _UI_FONT = "sans-serif"
    _CODE_FONT = "monospace"

FONT_DISPLAY = _UI_FONT
FONT_TEXT = _UI_FONT
FONT_CODE = _CODE_FONT

SPACING = {"xxs": 4, "xs": 8, "sm": 12, "md": 16, "lg": 24, "xl": 32, "xxl": 48}
RADIUS = 16  # 16px border radius — unified

# ─────────────────────────────────────────────
# Token Colors — VSCode-inspired syntax palette
# ─────────────────────────────────────────────
TOKEN_COLORS_LIGHT = {
    "FN": "#2962ff", "LET": "#2962ff", "IF": "#7c4dff", "ELSE": "#7c4dff",
    "WHILE": "#7c4dff", "RETURN": "#7c4dff", "MUT": "#2962ff",
    "I32": "#0f9d58", "FOR": "#7c4dff", "IN": "#2962ff",
    "LOOP": "#7c4dff", "BREAK": "#7c4dff", "CONTINUE": "#7c4dff",
    "ID": "#1a1a2e", "NUM": "#e65100",
    "EOF": "#9aa0a6", "ERROR": "#d93025",
    "=": "#5f6368", "+": "#5f6368", "-": "#5f6368",
    "*": "#5f6368", "/": "#5f6368", "==": "#5f6368",
    ">": "#5f6368", ">=": "#5f6368", "<": "#5f6368",
    "<=": "#5f6368", "!=": "#5f6368",
    "(": "#5f6368", ")": "#5f6368", "{": "#5f6368", "}": "#5f6368",
    "[": "#5f6368", "]": "#5f6368", ";": "#5f6368",
    ":": "#5f6368", ",": "#5f6368",
    "->": "#5f6368", "&": "#5f6368",
    ".": "#5f6368", "..": "#5f6368", "..=": "#5f6368",
    "#": "#9aa0a6",
}


# ─────────────────────────────────────────────
# AST Node Colors — by category (Academic color)
# ─────────────────────────────────────────────
NODE_COLORS_LIGHT = {
    # Declaration nodes — blue
    "Program":        {"bg": "#e8eaf6", "border": "#9fa8da", "text": "#1a237e"},
    "FunctionDecl":   {"bg": "#e3f2fd", "border": "#90caf9", "text": "#0d47a1"},
    "Param":          {"bg": "#e3f2fd", "border": "#90caf9", "text": "#0d47a1"},
    "VarDeclStmt":    {"bg": "#e3f2fd", "border": "#90caf9", "text": "#0d47a1"},
    "AssignStmt":     {"bg": "#e3f2fd", "border": "#90caf9", "text": "#0d47a1"},
    # Statement nodes — green
    "Block":          {"bg": "#e8f5e9", "border": "#a5d6a7", "text": "#1b5e20"},
    "ReturnStmt":     {"bg": "#e8f5e9", "border": "#a5d6a7", "text": "#1b5e20"},
    "ExprStmt":       {"bg": "#e8f5e9", "border": "#a5d6a7", "text": "#1b5e20"},
    "EmptyStmt":      {"bg": "#f1f8e9", "border": "#c5e1a5", "text": "#33691e"},
    # Control flow — purple
    "IfStmt":         {"bg": "#f3e5f5", "border": "#ce93d8", "text": "#4a148c"},
    "WhileStmt":      {"bg": "#f3e5f5", "border": "#ce93d8", "text": "#4a148c"},
    "ForStmt":        {"bg": "#f3e5f5", "border": "#ce93d8", "text": "#4a148c"},
    # Expression nodes — amber/yellow
    "BinaryExpr":     {"bg": "#fff8e1", "border": "#ffd54f", "text": "#e65100"},
    "LValue":         {"bg": "#fff8e1", "border": "#ffd54f", "text": "#e65100"},
    "NumberLiteral":  {"bg": "#fff8e1", "border": "#ffd54f", "text": "#e65100"},
    "FuncCall":       {"bg": "#fff8e1", "border": "#ffd54f", "text": "#e65100"},
    "UnaryMinus":     {"bg": "#fff8e1", "border": "#ffd54f", "text": "#e65100"},
    "Range":          {"bg": "#fff8e1", "border": "#ffd54f", "text": "#e65100"},
    "ArrayAccess":    {"bg": "#fff8e1", "border": "#ffd54f", "text": "#e65100"},
    # Array types — indigo
    "ArrayType":      {"bg": "#ede7f6", "border": "#b39ddb", "text": "#311b92"},
    "ArrayLiteral":   {"bg": "#ede7f6", "border": "#b39ddb", "text": "#311b92"},
    # Type nodes — gray
    "Type":           {"bg": "#eceff1", "border": "#b0bec5", "text": "#37474f"},
}

DEFAULT_NODE_COLOR_LIGHT = {"bg": "#f5f5f5", "border": "#c8c8c8", "text": "#333333"}

TOKEN_TYPE_LABELS = {
    "FN": "fn", "LET": "let", "IF": "if", "ELSE": "else",
    "WHILE": "while", "RETURN": "return", "MUT": "mut",
    "I32": "i32", "FOR": "for", "IN": "in",
    "LOOP": "loop", "BREAK": "break", "CONTINUE": "continue",
    "ID": "标识符", "NUM": "数字",
    "EOF": "结束", "ERROR": "错误",
    "=": "=", "+": "+", "-": "-",
    "*": "*", "/": "/", "==": "==",
    ">": ">", ">=": ">=", "<": "<",
    "<=": "<=", "!=": "!=",
    "(": "(", ")": ")", "{": "{", "}": "}",
    "[": "[", "]": "]", ";": ";",
    ":": ":", ",": ",",
    "->": "->", "&": "&",
    ".": ".", "..": "..", "..=": "..=",
    "#": "#",
}

TOKEN_CATEGORY_ORDER = ["关键字", "标识符", "数字", "运算符", "分隔符", "类型", "错误", "结束", "其他"]

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def get_token_category(token_type):
    return TOKEN_TYPE_LABELS.get(token_type, "其他")


def get_token_colors():
    return TOKEN_COLORS_LIGHT


def get_node_colors(node):
    name = node.node_name if isinstance(node, ASTNode) else node.__class__.__name__
    palette = NODE_COLORS_LIGHT
    default = DEFAULT_NODE_COLOR_LIGHT
    return palette.get(name, default)


def get_theme():
    return LIGHT


def get_node_title(node):
    if isinstance(node, FunctionDeclNode):
        return f"Function: {node.name}"
    elif isinstance(node, VarDeclStmtNode):
        mut = "mut " if node.is_mutable else ""
        return f"let {mut}{node.name}"
    elif isinstance(node, ParamNode):
        mut = "mut " if node.is_mutable else ""
        return f"{mut}{node.name}"
    elif isinstance(node, TypeNode):
        return f"Type: {node.type_name}"
    elif isinstance(node, ArrayTypeNode):
        return f"[{node.element_type.type_name}; {node.size}]"
    elif isinstance(node, BinaryExprNode):
        return f"Binary: {node.op}"
    elif isinstance(node, NumberLiteralNode):
        return f"{node.value}"
    elif isinstance(node, LValueNode):
        return node.name
    elif isinstance(node, FuncCallNode):
        return f"{node.name}()"
    elif isinstance(node, BlockStmtNode):
        return f"Block ({len(node.statements)})"
    elif isinstance(node, ReturnStmtNode):
        return "return"
    elif isinstance(node, IfStmtNode):
        return "if/else" if node.else_block else "if"
    elif isinstance(node, WhileStmtNode):
        return "while"
    elif isinstance(node, ForStmtNode):
        return f"for {node.var_name}"
    elif isinstance(node, RangeNode):
        return ".."
    elif isinstance(node, AssignStmtNode):
        return "="
    elif isinstance(node, ExprStmtNode):
        return "ExprStmt"
    elif isinstance(node, UnaryMinusNode):
        return "-"
    elif isinstance(node, EmptyStmtNode):
        return ";"
    elif isinstance(node, ProgramNode):
        return f"Program ({len(node.declarations)})"
    elif isinstance(node, ArrayLiteralNode):
        return f"[{len(node.elements)}]"
    elif isinstance(node, ArrayAccessNode):
        return "[]"
    else:
        return node.node_name if isinstance(node, ASTNode) else node.__class__.__name__


def get_node_subtitle(node):
    if isinstance(node, FunctionDeclNode):
        ret = node.return_type.type_name if node.return_type else "void"
        return f"-> {ret}"
    elif isinstance(node, VarDeclStmtNode):
        parts = []
        if node.var_type:
            parts.append(f": {node.var_type.type_name}")
        if node.init_expr:
            parts.append("= …")
        return " ".join(parts)
    elif isinstance(node, ParamNode):
        return node.param_type.type_name if node.param_type else ""
    elif isinstance(node, BinaryExprNode):
        return node.op
    elif isinstance(node, NumberLiteralNode):
        return ""
    elif isinstance(node, LValueNode):
        return ""
    elif isinstance(node, FuncCallNode):
        return f"{len(node.args)} args"
    elif isinstance(node, BlockStmtNode):
        return ""
    elif isinstance(node, IfStmtNode):
        return "else" if node.else_block else ""
    elif isinstance(node, ReturnStmtNode):
        return "" if node.expr else "(void)"
    elif isinstance(node, TypeNode):
        return node.type_name
    elif isinstance(node, ArrayTypeNode):
        return f"{node.element_type.type_name} x {node.size}"
    elif isinstance(node, ForStmtNode):
        mut = "mut " if node.is_mutable else ""
        return f"{mut}{node.var_name} in …"
    elif isinstance(node, RangeNode):
        return ""
    elif isinstance(node, ArrayLiteralNode):
        return f"{len(node.elements)} elem"
    elif isinstance(node, ArrayAccessNode):
        return ""
    return ""


def get_ast_children(node):
    children = []
    if isinstance(node, ProgramNode):
        children = node.declarations
    elif isinstance(node, FunctionDeclNode):
        if node.params:
            children.append(node.params)
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
    elif isinstance(node, ForStmtNode):
        if isinstance(node.iterable, RangeNode):
            children = [node.iterable.start, node.iterable.end]
        else:
            children.append(node.iterable)
        children.append(node.body)
    elif isinstance(node, RangeNode):
        children = [node.start, node.end]
    elif isinstance(node, BinaryExprNode):
        children = [node.left, node.right]
    elif isinstance(node, FuncCallNode):
        children = node.args
    elif isinstance(node, UnaryMinusNode):
        if node.expr:
            children.append(node.expr)
    elif isinstance(node, ArrayLiteralNode):
        children = node.elements
    elif isinstance(node, ArrayAccessNode):
        children = [node.array, node.index]
    return children


def get_node_ast_type_name(node):
    """Get human-readable AST type for info panel"""
    mapping = {
        ProgramNode: "Program (ProgramNode)",
        FunctionDeclNode: "Function Declaration (FunctionDeclNode)",
        ParamNode: "Parameter (ParamNode)",
        TypeNode: "Type (TypeNode)",
        ArrayTypeNode: "Array Type (ArrayTypeNode)",
        BlockStmtNode: "Block (BlockStmtNode)",
        EmptyStmtNode: "Empty Statement (EmptyStmtNode)",
        ReturnStmtNode: "Return Statement (ReturnStmtNode)",
        VarDeclStmtNode: "Variable Declaration (VarDeclStmtNode)",
        AssignStmtNode: "Assignment (AssignStmtNode)",
        ExprStmtNode: "Expression Statement (ExprStmtNode)",
        IfStmtNode: "If Statement (IfStmtNode)",
        WhileStmtNode: "While Loop (WhileStmtNode)",
        ForStmtNode: "For Loop (ForStmtNode)",
        RangeNode: "Range (RangeNode)",
        BinaryExprNode: "Binary Expression (BinaryExprNode)",
        LValueNode: "LValue (LValueNode)",
        NumberLiteralNode: "Number Literal (NumberLiteralNode)",
        FuncCallNode: "Function Call (FuncCallNode)",
        UnaryMinusNode: "Unary Minus (UnaryMinusNode)",
        ArrayLiteralNode: "Array Literal (ArrayLiteralNode)",
        ArrayAccessNode: "Array Access (ArrayAccessNode)",
    }
    for cls, name in mapping.items():
        if isinstance(node, cls):
            return name
    return node.node_name if isinstance(node, ASTNode) else node.__class__.__name__


def get_node_properties(node):
    """Extract key-value properties from an AST node for the info panel"""
    props = []
    if isinstance(node, ProgramNode):
        props.append(("Declarations", str(len(node.declarations))))
    elif isinstance(node, FunctionDeclNode):
        props.append(("Name", node.name))
        props.append(("Params", str(len(node.params)) if node.params else "0"))
        props.append(("Return Type", node.return_type.type_name if node.return_type else "void"))
    elif isinstance(node, ParamNode):
        props.append(("Name", node.name))
        props.append(("Mutable", str(node.is_mutable)))
        props.append(("Type", node.param_type.type_name if node.param_type else ""))
    elif isinstance(node, VarDeclStmtNode):
        props.append(("Name", node.name))
        props.append(("Mutable", str(node.is_mutable)))
        if node.var_type:
            props.append(("Type", node.var_type.type_name))
        props.append(("Has Init", "Yes" if node.init_expr else "No"))
    elif isinstance(node, AssignStmtNode):
        props.append(("Target", node.left.name if hasattr(node.left, 'name') else "?"))
    elif isinstance(node, BinaryExprNode):
        props.append(("Operator", node.op))
    elif isinstance(node, NumberLiteralNode):
        props.append(("Value", str(node.value)))
    elif isinstance(node, LValueNode):
        props.append(("Name", node.name))
    elif isinstance(node, FuncCallNode):
        props.append(("Name", node.name))
        props.append(("Arguments", str(len(node.args))))
    elif isinstance(node, IfStmtNode):
        props.append(("Has Else", "Yes" if node.else_block else "No"))
    elif isinstance(node, WhileStmtNode):
        pass
    elif isinstance(node, ForStmtNode):
        props.append(("Variable", node.var_name))
        props.append(("Mutable", str(node.is_mutable)))
    elif isinstance(node, ReturnStmtNode):
        props.append(("Has Value", "Yes" if node.expr else "No"))
    elif isinstance(node, ArrayTypeNode):
        props.append(("Element", node.element_type.type_name))
        props.append(("Size", str(node.size)))
    elif isinstance(node, ArrayLiteralNode):
        props.append(("Elements", str(len(node.elements))))
    elif isinstance(node, ArrayAccessNode):
        pass
    return props


# ─────────────────────────────────────────────
# Rounded rect helper (16px radius by default)
# ─────────────────────────────────────────────
def _create_rounded_rect(canvas, x1, y1, x2, y2, radius=RADIUS, **kwargs):
    r = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    pts = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


# ─────────────────────────────────────────────
# Layout tree data structures
# ─────────────────────────────────────────────
class LayoutNode:
    def __init__(self, ast_node, children=None, title="", subtitle="", colors=None):
        self.ast_node = ast_node
        self.children = children or []
        self.title = title
        self.subtitle = subtitle
        self.colors = colors or DEFAULT_NODE_COLOR_LIGHT
        self.x = 0
        self.y = 0
        self.width = 120
        self.height = 52
        self.mod = 0
        self.contour = None
        self.collapsed = False
        self.canvas_ids = []


def build_layout_tree(ast_root):
    if ast_root is None:
        return None
    title = get_node_title(ast_root)
    subtitle = get_node_subtitle(ast_root)
    colors = get_node_colors(ast_root)
    raw_children = get_ast_children(ast_root)
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


def count_ast_nodes(node):
    """Count total nodes in the AST (for statistics)"""
    if node is None:
        return 0
    count = 1
    for child in get_ast_children(node):
        count += count_ast_nodes(child)
    return count


def collect_symbols(node, symbols=None, depth=0):
    """Collect variable/function declarations for symbol table"""
    if symbols is None:
        symbols = []
    if isinstance(node, ProgramNode):
        for decl in node.declarations:
            collect_symbols(decl, symbols, depth)
    elif isinstance(node, FunctionDeclNode):
        symbols.append({
            "type": "Function",
            "name": node.name,
            "detail": f"-> {node.return_type.type_name if node.return_type else 'void'}"
        })
        # Collect parameters
        if node.params:
            for p in node.params:
                collect_symbols(p, symbols, depth + 1)
        if node.body:
            collect_symbols(node.body, symbols, depth + 1)
    elif isinstance(node, VarDeclStmtNode):
        symbols.append({
            "type": "Variable",
            "name": node.name,
            "detail": f"{'mut ' if node.is_mutable else ''}: {node.var_type.type_name if node.var_type else 'inferred'}"
        })
    elif isinstance(node, ParamNode):
        symbols.append({
            "type": "Param",
            "name": node.name,
            "detail": f"{'mut ' if node.is_mutable else ''}{node.param_type.type_name if node.param_type else ''}"
        })
    elif isinstance(node, BlockStmtNode):
        for stmt in node.statements:
            collect_symbols(stmt, symbols, depth + 1)
    elif isinstance(node, IfStmtNode):
        collect_symbols(node.then_block, symbols, depth + 1)
        if node.else_block:
            collect_symbols(node.else_block, symbols, depth + 1)
    elif isinstance(node, WhileStmtNode):
        collect_symbols(node.body, symbols, depth + 1)
    elif isinstance(node, ForStmtNode):
        collect_symbols(node.body, symbols, depth + 1)
    elif isinstance(node, ReturnStmtNode) or isinstance(node, AssignStmtNode) or isinstance(node, ExprStmtNode):
        pass  # Propagate to children via get_ast_children
    return symbols


def count_node_types(node, counts=None):
    """Count nodes by type (for statistics)"""
    if counts is None:
        counts = {}
    if node is None:
        return counts
    name = node.node_name if isinstance(node, ASTNode) else node.__class__.__name__
    counts[name] = counts.get(name, 0) + 1
    for child in get_ast_children(node):
        count_node_types(child, counts)
    return counts


def get_ast_depth(node, depth=0):
    """Calculate max depth of AST"""
    if node is None:
        return depth
    children = get_ast_children(node)
    if not children:
        return depth + 1
    return max(get_ast_depth(c, depth + 1) for c in children)


# ═══════════════════════════════════════════════
# TokenViewer — Lexical Analysis Tab
# ═══════════════════════════════════════════════
class TokenViewer(ttk.Frame):
    """Token viewer with colored syntax highlighting and token table"""

    def __init__(self, parent, on_token_select=None):
        super().__init__(parent)
        self.tokens = []
        self.source = ""
        self.on_token_select = on_token_select
        self.code_rects = []

        th = get_theme()

        # ── Source code display ──
        code_header = tk.Frame(self, bg=th["bg_primary"])
        code_header.pack(fill=tk.X, padx=SPACING["md"], pady=(SPACING["md"], 0))

        tk.Label(
            code_header, text="Token 着色", font=(FONT_TEXT, 12, "bold"),
            fg=th["text_primary"], bg=th["bg_primary"], anchor=tk.W
        ).pack(fill=tk.X, pady=(0, SPACING["xs"]))

        code_container = tk.Frame(self, bg=th["card_bg"],
                                  highlightbackground=th["border_light"],
                                  highlightthickness=1, bd=0)
        code_container.pack(fill=tk.X, padx=SPACING["md"], pady=(0, SPACING["xs"]))

        self.code_canvas = tk.Canvas(code_container, bg=th["code_bg"], height=180,
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

        # ── Token table ──
        table_section = tk.Frame(self, bg=th["bg_primary"])
        table_section.pack(fill=tk.X, padx=SPACING["md"], pady=(SPACING["xs"], 0))

        tk.Label(
            table_section, text="Token 序列", font=(FONT_TEXT, 12, "bold"),
            fg=th["text_primary"], bg=th["bg_primary"]
        ).pack(anchor=tk.W)

        table_frame = tk.Frame(self, bg=th["card_bg"],
                               highlightbackground=th["border_light"],
                               highlightthickness=1, bd=0)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"],
                         pady=(SPACING["xs"], SPACING["md"]))

        columns = ("序号", "Token类型", "分类", "值", "行", "列")
        style = ttk.Style()
        style.configure("Token.Treeview", font=(FONT_TEXT, 11), rowheight=26,
                        borderwidth=0)
        style.configure("Token.Treeview.Heading", font=(FONT_TEXT, 10, "bold"),
                        borderwidth=0)

        self.token_tree = ttk.Treeview(table_frame, columns=columns,
                                       show="headings", height=8,
                                       style="Token.Treeview")
        for col in columns:
            self.token_tree.heading(col, text=col)
            if col in ("序号", "行", "列"):
                self.token_tree.column(col, width=50, anchor=tk.CENTER)
            elif col == "Token类型":
                self.token_tree.column(col, width=90, anchor=tk.CENTER)
            elif col == "分类":
                self.token_tree.column(col, width=60, anchor=tk.CENTER)
            elif col == "值":
                self.token_tree.column(col, width=200)

        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=v_scroll.set)
        self.token_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Info/Stats bar ──
        self.info_label = tk.Label(
            self, text="", font=(FONT_TEXT, 10), fg=th["text_secondary"],
            bg=th["bg_primary"], anchor=tk.W
        )
        self.info_label.pack(fill=tk.X, padx=SPACING["md"], pady=(0, SPACING["xxs"]))

        self.stats_label = tk.Label(
            self, text="就绪", font=(FONT_TEXT, 10), fg=th["text_muted"],
            bg=th["bg_primary"], anchor=tk.W
        )
        self.stats_label.pack(fill=tk.X, padx=SPACING["md"], pady=(0, SPACING["sm"]))

        self.token_tree.bind("<<TreeviewSelect>>", self._on_token_select)

    def display(self, source, tokens):
        self.source = source
        self.tokens = tokens
        self._clear()
        self.update_idletasks()
        self._render_code()
        self._render_table()
        self._render_stats()

    def _clear(self):
        self.code_canvas.delete("all")
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
        self.code_rects = []
        self.info_label.config(text="")

    def _render_code(self):
        canvas = self.code_canvas
        canvas.delete("all")
        th = get_theme()

        if not self.tokens:
            canvas.create_text(14, 20, anchor=tk.W, text="无 Token 数据",
                               font=(FONT_CODE, 11), fill=th["text_muted"])
            return

        display_tokens = [t for t in self.tokens if t.type != TT_EOF]
        if not display_tokens:
            canvas.create_text(14, 20, anchor=tk.W, text="(空)",
                               font=(FONT_CODE, 11), fill=th["text_muted"])
            return

        font = tkfont.Font(family=FONT_CODE.split(",")[0].strip(), size=11)
        line_height = font.metrics("linespace") + 4
        tokens_by_line = {}
        for t in display_tokens:
            tokens_by_line.setdefault(t.line, []).append(t)

        token_colors = get_token_colors()
        x, y = 14, 10
        for line_num in sorted(tokens_by_line.keys()):
            x = 14
            line_tokens = tokens_by_line[line_num]
            for token in line_tokens:
                token_text = token.value
                color = token_colors.get(token.type, th["text_primary"])
                text_width = font.measure(token_text)

                pad_x, pad_y = 3, 1
                rect_id = canvas.create_rectangle(
                    x - pad_x, y - pad_y,
                    x + text_width + pad_x, y + line_height + pad_y,
                    outline="", fill="", tags="bg"
                )
                text_id = canvas.create_text(
                    x, y, anchor=tk.NW, text=token_text,
                    font=font, fill=color, tags="token"
                )
                self.code_rects.append((rect_id, text_id, token))

                canvas.tag_bind(text_id, "<Enter>",
                                lambda e, t=token, r=rect_id: self._on_token_hover(t, r))
                canvas.tag_bind(text_id, "<Leave>",
                                lambda e, r=rect_id: self._on_token_leave(r))
                x += text_width + 8
            y += line_height + 6

        bbox = canvas.bbox("all")
        if bbox:
            canvas.configure(scrollregion=bbox)

    def _on_token_hover(self, token, rect_id):
        th = get_theme()
        self.code_canvas.itemconfig(rect_id, fill=th["bg_hover"])
        info = f"类型: {token.type}  |  值: '{token.value}'  |  位置: 第{token.line}行, 第{token.column}列"
        self.info_label.config(text=info)
        if self.on_token_select:
            self.on_token_select({
                "type": "token",
                "token_type": token.type,
                "value": token.value,
                "line": token.line,
                "column": token.column,
            })

    def _on_token_leave(self, rect_id):
        self.code_canvas.itemconfig(rect_id, fill="")

    def _render_table(self):
        tree = self.token_tree
        display_tokens = [t for t in self.tokens if t.type != TT_EOF]
        for i, token in enumerate(display_tokens, 1):
            category = get_token_category(token.type)
            tree.insert("", tk.END, values=(
                i, token.type, category, token.value, token.line, token.column
            ))

    def _render_stats(self):
        display_tokens = [t for t in self.tokens if t.type != TT_EOF]
        error_tokens = [t for t in self.tokens if t.type == TT_ERROR]
        categories = {}
        for t in display_tokens:
            cat = get_token_category(t.type)
            categories[cat] = categories.get(cat, 0) + 1

        parts = [f"共 {len(display_tokens)} 个 Token"]
        for cat in TOKEN_CATEGORY_ORDER:
            if cat in categories:
                parts.append(f"{cat}: {categories[cat]}")
        if error_tokens:
            parts.append(f"错误: {len(error_tokens)}")

        self.stats_label.config(text="  |  ".join(parts))

    def _on_token_select(self, event):
        selection = self.token_tree.selection()
        if selection:
            values = self.token_tree.item(selection[0], "values")
            if values:
                self.info_label.config(
                    text=f"序号: {values[0]}  |  类型: {values[1]}  |  分类: {values[2]}  |  "
                         f"值: '{values[3]}'  |  位置: 第{values[4]}行, 第{values[5]}列"
                )
                if self.on_token_select:
                    self.on_token_select({
                        "type": "token",
                        "token_type": values[1],
                        "value": values[3],
                        "line": values[4],
                        "column": values[5],
                    })

    def clear(self):
        self._clear()
        self.stats_label.config(text="就绪")


# ═══════════════════════════════════════════════
# Syntax Tree builder — enriched CST-like display
# ═══════════════════════════════════════════════

SYNTAX_PREFIX = {
    "Program": "📋", "FunctionDecl": "ƒ", "Param": "▸",
    "Type": "◎", "ArrayType": "▦",
    "Block": "{}", "EmptyStmt": "∅",
    "ReturnStmt": "↩", "VarDeclStmt": "□", "AssignStmt": "←",
    "ExprStmt": "◆",
    "IfStmt": "◇", "WhileStmt": "⟳", "ForStmt": "∀", "Range": "…",
    "BinaryExpr": "⊕", "LValue": "○", "NumberLiteral": "#",
    "FuncCall": "→", "UnaryMinus": "⊖",
    "ArrayLiteral": "[]", "ArrayAccess": "⌿",
}


def _get_syntax_label(node, depth=0):
    """Generate a detailed, human-readable syntax tree label for an AST node"""
    node_name = node.node_name if isinstance(node, ASTNode) else node.__class__.__name__
    prefix = SYNTAX_PREFIX.get(node_name, "?")

    if isinstance(node, ProgramNode):
        return f"{prefix} Program", f"{len(node.declarations)} 个声明", "declaration list"
    elif isinstance(node, FunctionDeclNode):
        ret = node.return_type.type_name if node.return_type else "void"
        detail = f"-> {ret}, {len(node.params)} 个参数"
        rule = "fn ID ( Params? ) -> Type Block"
        return f"{prefix} {node.name}", detail, rule
    elif isinstance(node, ParamNode):
        mut = "mut " if node.is_mutable else ""
        t = node.param_type.type_name if node.param_type else "?"
        rule = "mut? ID : Type"
        return f"{prefix} {mut}{node.name}", f": {t}", rule
    elif isinstance(node, TypeNode):
        return f"{prefix} {node.type_name}", "类型注解", "Type"
    elif isinstance(node, ArrayTypeNode):
        rule = "[ Type ; NUM ]"
        return f"{prefix} [{node.element_type.type_name}; {node.size}]", "数组类型", rule
    elif isinstance(node, BlockStmtNode):
        rule = "{ Stmt* }"
        return f"{prefix} Block", f"{len(node.statements)} 条语句", rule
    elif isinstance(node, EmptyStmtNode):
        return f"{prefix} EmptyStmt", "空语句", ";"
    elif isinstance(node, ReturnStmtNode):
        rule = "return Expr? ;"
        has = "有返回值" if node.expr else "无返回值"
        return f"{prefix} return", has, rule
    elif isinstance(node, VarDeclStmtNode):
        mut = "mut " if node.is_mutable else ""
        t = f": {node.var_type.type_name}" if node.var_type else ""
        init = " = Expr" if node.init_expr else ""
        rule = f"let mut? ID {t}{init} ;"
        detail = f"{'mut ' if node.is_mutable else ''}{node.name}{t}"
        if node.init_expr:
            detail += " = …"
        return f"{prefix} let {mut}{node.name}", detail, rule
    elif isinstance(node, AssignStmtNode):
        target = node.left.name if hasattr(node.left, 'name') else "?"
        rule = "LValue = Expr ;"
        return f"{prefix} {target} = …", f"赋值给 {target}", rule
    elif isinstance(node, ExprStmtNode):
        return f"{prefix} ExprStmt", "表达式语句", "Expr ;"
    elif isinstance(node, IfStmtNode):
        rule = "if Expr Block (else Block)?"
        suffix = " / else" if node.else_block else ""
        return f"{prefix} if{suffix}", "条件分支", rule
    elif isinstance(node, WhileStmtNode):
        rule = "while Expr Block"
        return f"{prefix} while", "循环", rule
    elif isinstance(node, ForStmtNode):
        mut = "mut " if node.is_mutable else ""
        rule = f"for mut? ID in Range Block"
        return f"{prefix} for {mut}{node.var_name}", f"for 循环", rule
    elif isinstance(node, RangeNode):
        rule = "Expr .. Expr"
        return f"{prefix} ..", "范围", rule
    elif isinstance(node, BinaryExprNode):
        rule = f"Expr {node.op} Expr"
        return f"{prefix} {node.op}", "二元运算", rule
    elif isinstance(node, LValueNode):
        return f"{prefix} {node.name}", "左值 / 变量引用", "ID"
    elif isinstance(node, NumberLiteralNode):
        return f"{prefix} {node.value}", "整数字面量", "NUM"
    elif isinstance(node, FuncCallNode):
        rule = f"ID ( Expr* )"
        return f"{prefix} {node.name}()", f"{len(node.args)} 个参数", rule
    elif isinstance(node, UnaryMinusNode):
        rule = "- Expr"
        return f"{prefix} -", "一元负号", rule
    elif isinstance(node, ArrayLiteralNode):
        rule = "[ Expr* ]"
        return f"{prefix} [{len(node.elements)}]", f"数组字面量 ({len(node.elements)} 个元素)", rule
    elif isinstance(node, ArrayAccessNode):
        rule = "Expr [ Expr ]"
        return f"{prefix} []", "数组访问", rule
    return f"{prefix} {node_name}", "", ""


def _build_syntax_children(node):
    """Get children for syntax tree display (same as get_ast_children)"""
    return get_ast_children(node)


# ═══════════════════════════════════════════════
# SyntaxTreeViewer — Collapsible Tree (CST style)
# ═══════════════════════════════════════════════
class SyntaxTreeViewer(ttk.Frame):
    """Syntax tree viewer showing CST-style enriched tree in a Treeview widget.

    Displays each AST node with:
      - A prefix icon indicating node category
      - Node name and key identifiers
      - Detail / attribute column
      - Grammar production rule column
    This makes explicit which grammar rules the parser applied.
    """

    def __init__(self, parent, on_node_select=None):
        super().__init__(parent)
        self.on_node_select = on_node_select
        self.ast_root = None
        self._tree_id_to_ast = {}  # treeview item ID -> ast_node
        th = get_theme()

        # Toolbar
        toolbar = tk.Frame(self, bg=th["bg_secondary"])
        toolbar.pack(fill=tk.X, padx=SPACING["sm"], pady=(SPACING["xs"], 0))

        self._tool_btn(toolbar, "展开全部", self._expand_all).pack(side=tk.LEFT, padx=1)
        self._tool_btn(toolbar, "折叠全部", self._collapse_all).pack(side=tk.LEFT, padx=1)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=SPACING["sm"], pady=4)

        self.status_label = tk.Label(
            toolbar, text="就绪", font=(FONT_TEXT, 11), fg=th["text_secondary"],
            bg=th["bg_secondary"], anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING["sm"]))

        # Tree frame
        tree_frame = tk.Frame(self, bg=th["card_bg"],
                              highlightbackground=th["border_light"],
                              highlightthickness=1, bd=0)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"],
                        pady=(SPACING["xs"], SPACING["md"]))

        # Columns: Node | Detail | Grammar Rule
        columns = ("节点", "属性", "文法规则")
        style = ttk.Style()
        style.configure("Syntax.Treeview", font=(FONT_TEXT, 11), rowheight=26,
                        borderwidth=0)
        style.configure("Syntax.Treeview.Heading", font=(FONT_TEXT, 10, "bold"),
                        borderwidth=0)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings",
                                 style="Syntax.Treeview")
        self.tree.heading("#0", text="语法节点")
        self.tree.column("#0", width=280, minwidth=200)
        self.tree.heading("节点", text="节点")
        self.tree.column("节点", width=80, minwidth=60, anchor=tk.W)
        self.tree.heading("属性", text="属性")
        self.tree.column("属性", width=160, minwidth=100, anchor=tk.W)
        self.tree.heading("文法规则", text="文法规则")
        self.tree.column("文法规则", width=220, minwidth=160, anchor=tk.W)

        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _tool_btn(self, parent, text, cmd):
        th = get_theme()
        return tk.Button(
            parent, text=text, command=cmd,
            font=(FONT_TEXT, 11), fg=th["accent_blue"], bg=th["bg_secondary"],
            activeforeground=th["accent_blue_hover"], activebackground=th["bg_hover"],
            relief=tk.FLAT, bd=0, padx=8, pady=2,
            cursor="hand2", highlightthickness=0
        )

    def display(self, ast_root):
        """Populate the tree view from an AST root"""
        self.ast_root = ast_root
        self._tree_id_to_ast = {}
        for item in self.tree.get_children():
            self.tree.delete(item)

        if ast_root is None:
            self.status_label.config(text="无 AST 可显示")
            return

        self.update_idletasks()
        self._populate_tree("", ast_root)
        self.status_label.config(text="点击节点查看详情 · 展开/折叠查看语法结构")

    def _populate_tree(self, parent_id, node):
        """Recursively populate the Treeview with syntax tree nodes"""
        label, detail, rule = _get_syntax_label(node)

        # Get node name for the second column
        node_name = node.node_name if isinstance(node, ASTNode) else node.__class__.__name__

        # Insert into tree
        item_id = self.tree.insert(
            parent_id, tk.END,
            text=label,
            values=(node_name, detail, rule),
            open=True
        )
        self._tree_id_to_ast[item_id] = node

        # Recurse children
        children = _build_syntax_children(node)
        for child in children:
            if isinstance(child, ASTNode):
                self._populate_tree(item_id, child)
            elif isinstance(child, list):
                for c in child:
                    if isinstance(c, ASTNode):
                        self._populate_tree(item_id, c)

        return item_id

    def _on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        ast_node = self._tree_id_to_ast.get(item_id)
        if ast_node is None:
            return

        # Get display values
        values = self.tree.item(item_id, "values")
        label = self.tree.item(item_id, "text")
        info = label
        if values and values[1]:
            info += f" · {values[1]}"
        self.status_label.config(text=info)

        if self.on_node_select and ast_node:
            self.on_node_select({
                "type": "syntax_node",
                "title": label,
                "subtitle": values[1] if values else "",
                "ast_node": ast_node,
            })

    def _expand_all(self):
        """Expand all nodes in the tree"""
        for item in self._tree_id_to_ast:
            try:
                self.tree.item(item, open=True)
            except:
                pass

    def _collapse_all(self):
        """Collapse all nodes in the tree (keep root open)"""
        root_children = self.tree.get_children()
        for root_child in root_children:
            self._collapse_recursive(root_child)

    def _collapse_recursive(self, item_id):
        children = self.tree.get_children(item_id)
        for child in children:
            self._collapse_recursive(child)
        try:
            self.tree.item(item_id, open=False)
        except:
            pass

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._tree_id_to_ast = {}
        self.ast_root = None
        self.status_label.config(text="就绪")


# ═══════════════════════════════════════════════
# ASTGraphViewer — Full interactive AST tree
# ═══════════════════════════════════════════════
class ASTGraphViewer(ttk.Frame):
    """Interactive AST visualization with Apple-style rounded cards, zoom/pan/collapse/search"""

    NODE_MIN_WIDTH = 120
    NODE_HEIGHT = 52
    H_GAP = 24
    V_GAP = 72
    PAD_LEFT = 20
    PAD_TOP = 20

    def __init__(self, parent, on_node_select=None):
        super().__init__(parent)
        self.on_node_select = on_node_select
        th = get_theme()

        # ── Toolbar ──
        toolbar = tk.Frame(self, bg=th["bg_secondary"])
        toolbar.pack(fill=tk.X, padx=SPACING["sm"], pady=(SPACING["xs"], 0))

        self._tool_btn(toolbar, "适合窗口", self._fit_to_view).pack(side=tk.LEFT, padx=1)
        self._tool_btn(toolbar, "放大", self._zoom_in).pack(side=tk.LEFT, padx=1)
        self._tool_btn(toolbar, "缩小", self._zoom_out).pack(side=tk.LEFT, padx=1)
        self._tool_btn(toolbar, "重置", self._reset_view).pack(side=tk.LEFT, padx=1)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=SPACING["sm"], pady=4)

        self.collapse_mode = tk.BooleanVar(value=False)
        tk.Checkbutton(
            toolbar, text="折叠模式", variable=self.collapse_mode,
            command=self._toggle_collapse_mode,
            font=(FONT_TEXT, 11), fg=th["text_primary"], bg=th["bg_secondary"],
            activebackground=th["bg_secondary"], selectcolor=th["bg_secondary"],
            relief=tk.FLAT, bd=0, cursor="hand2", highlightthickness=0
        ).pack(side=tk.LEFT, padx=4)

        self._tool_btn(toolbar, "导出 EPS", self._export_eps).pack(side=tk.LEFT, padx=1)

        # ── Search bar ──
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=SPACING["sm"], pady=4)

        tk.Label(toolbar, text="搜索:", font=(FONT_TEXT, 11),
                 fg=th["text_secondary"], bg=th["bg_secondary"]).pack(side=tk.LEFT, padx=2)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._do_search())
        self.search_entry = tk.Entry(
            toolbar, textvariable=self.search_var, font=(FONT_TEXT, 11),
            width=14, relief=tk.FLAT, bd=0,
            highlightbackground=th["border_light"], highlightthickness=1,
            bg=th["card_bg"], fg=th["text_primary"],
            insertbackground=th["text_primary"]
        )
        self.search_entry.pack(side=tk.LEFT, padx=2, pady=2)
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        self.search_count_label = tk.Label(
            toolbar, text="", font=(FONT_TEXT, 10),
            fg=th["text_muted"], bg=th["bg_secondary"]
        )
        self.search_count_label.pack(side=tk.LEFT, padx=4)

        self.status_label = tk.Label(
            toolbar, text="就绪", font=(FONT_TEXT, 11), fg=th["text_secondary"],
            bg=th["bg_secondary"], anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(SPACING["sm"], 0))

        # ── Canvas ──
        self.canvas_frame = tk.Frame(self, bg=th["card_bg"],
                                     highlightbackground=th["border_light"],
                                     highlightthickness=1, bd=0)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"],
                               pady=(SPACING["xs"], SPACING["md"]))

        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)

        self.canvas = tk.Canvas(self.canvas_frame, bg=th["bg_secondary"],
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

        # State
        self.root_node = None
        self._scale = 1.0
        self._drag_start = None
        self._selected_node = None
        self._collapse_mode = False
        self._node_map = {}
        self._edge_ids = []
        self._node_rect_ids = {}
        self._node_shadow_ids = {}
        self._all_nodes_list = []
        self._search_results = []
        self._search_index = 0

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel_up)
        self.canvas.bind("<Button-5>", self._on_mousewheel_down)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _tool_btn(self, parent, text, cmd):
        th = get_theme()
        return tk.Button(
            parent, text=text, command=cmd,
            font=(FONT_TEXT, 11), fg=th["accent_blue"], bg=th["bg_secondary"],
            activeforeground=th["accent_blue_hover"], activebackground=th["bg_hover"],
            relief=tk.FLAT, bd=0, padx=6, pady=2,
            cursor="hand2", highlightthickness=0
        )

    def _redraw(self):
        """Redraw keeping collapsed state"""
        if self.root_node is None:
            return
        collapsed_ids = set()
        def collect_collapsed(node):
            if node.collapsed:
                collapsed_ids.add(id(node.ast_node))
            for child in node.children:
                collect_collapsed(child)
        collect_collapsed(self.root_node)

        self.canvas.delete("all")
        self._node_map = {}
        self._edge_ids = []
        self._node_rect_ids = {}
        self._node_shadow_ids = {}
        self._all_nodes_list = []
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

    def display(self, ast_root):
        self.canvas.delete("all")
        self._node_map = {}
        self._edge_ids = []
        self._node_rect_ids = {}
        self._node_shadow_ids = {}
        self._all_nodes_list = []
        self.root_node = None
        self._selected_node = None
        self._scale = 1.0
        self._search_results = []
        self._search_index = 0
        self.search_count_label.config(text="")

        if ast_root is None:
            th = get_theme()
            self.canvas.create_text(20, 20, anchor=tk.W, text="无 AST 可显示",
                                    font=(FONT_TEXT, 12), fill=th["text_muted"])
            self.status_label.config(text="无 AST")
            return

        self.update_idletasks()
        self.root_node = build_layout_tree(ast_root)
        self._build_node_map(self.root_node)
        self._layout_tree()
        self._draw_tree()
        self._fit_to_view()
        self.status_label.config(text="滚轮缩放 · 拖拽平移 · 点击选中 · 折叠模式 · 搜索节点")

    def _build_node_map(self, node):
        self._node_map[id(node)] = node
        self._all_nodes_list.append(node)
        for child in node.children:
            self._build_node_map(child)

    def _layout_tree(self):
        if not self.root_node:
            return
        self._calc_node_sizes(self.root_node)
        self._calc_subtree_width(self.root_node, 0)
        total_w = self.root_node.subtree_width
        self._assign_positions(self.root_node, -total_w / 2)

    def _calc_node_sizes(self, node):
        font_title = tkfont.Font(family=FONT_TEXT, size=10, weight="bold")
        font_sub = tkfont.Font(family=FONT_TEXT, size=9)
        title_w = font_title.measure(node.title)
        sub_w = font_sub.measure(node.subtitle) if node.subtitle else 0
        text_w = max(title_w, sub_w)
        node.width = max(self.NODE_MIN_WIDTH, text_w + 24)
        node.height = self.NODE_HEIGHT

    def _calc_subtree_width(self, node, depth):
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
        if not node.children or node.collapsed:
            node.x = x_start + node.subtree_width / 2
            return
        child_x = x_start
        for child in node.children:
            self._assign_positions(child, child_x)
            child_x += child.subtree_width
        first = node.children[0]
        last = node.children[-1]
        node.x = (first.x + last.x) / 2

    def _draw_tree(self):
        if not self.root_node:
            return
        self._draw_edges(self.root_node)
        self._draw_node_rect(self.root_node)

    def _draw_edges(self, node):
        if not node.children or node.collapsed:
            return
        x1, y1 = node.x, node.y + node.height
        for child in node.children:
            x2, y2 = child.x, child.y
            mid_y = (y1 + y2) / 2
            eid = self.canvas.create_line(
                x1, y1, x1, mid_y, x2, mid_y, x2, y2,
                fill="#b0b0c0", width=1.5, smooth=True, tags="edge"
            )
            self._edge_ids.append(eid)
            self._draw_edges(child)

    def _draw_node_rect(self, node):
        c = self.canvas
        x, y, w, h = node.x, node.y, node.width, node.height
        colors = node.colors

        # Shadow
        sid = _create_rounded_rect(
            c, x - w / 2 + 2, y + 2, x + w / 2 + 2, y + h + 2,
            radius=8, fill="#e0e0e4", outline="", tags="shadow"
        )
        self._node_shadow_ids[id(node)] = sid

        # Rounded rect card (16px)
        rect_id = _create_rounded_rect(
            c, x - w / 2, y, x + w / 2, y + h,
            radius=RADIUS, fill=colors["bg"], outline=colors["border"],
            width=1.5, tags="node"
        )

        title_font = tkfont.Font(family=FONT_TEXT, size=10, weight="bold")
        c.create_text(x, y + h / 2 - 6, text=node.title, font=title_font,
                       fill=colors.get("text", "#1a1a2e"), tags="node")

        if node.subtitle:
            sub_font = tkfont.Font(family=FONT_TEXT, size=9)
            c.create_text(x, y + h / 2 + 11, text=node.subtitle, font=sub_font,
                           fill="#5f6368", tags="node")

        # Collapse indicator
        if node.children:
            self._draw_collapse_indicator(node)

        node.canvas_ids.append(rect_id)
        self._node_rect_ids[id(node)] = rect_id

        c.tag_bind(rect_id, "<Button-1>", lambda e, n=node: self._on_node_click(n))

        if node.children and not node.collapsed:
            for child in node.children:
                self._draw_node_rect(child)

    def _draw_collapse_indicator(self, node):
        c = self.canvas
        x, y = node.x + node.width / 2 - 10, node.y + 6
        r = 6
        fill = "#b0b0c0" if not node.collapsed else "#808090"
        c.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="", tags="node")
        c.create_text(x, y, text="−" if not node.collapsed else "+",
                       fill="#ffffff", font=(FONT_TEXT, 9, "bold"), tags="node")

    def _on_node_click(self, node):
        if self.collapse_mode.get():
            node.collapsed = not node.collapsed
            self._redraw_keeping_collapsed()
            status = "折叠" if node.collapsed else "展开"
            self.status_label.config(text=f"{status}: {node.title}")
        else:
            # Selection highlighting
            self._selected_node = node
            for nid, rid in self._node_rect_ids.items():
                n = self._node_map.get(nid)
                if n:
                    clr = n.colors
                    if n is node:
                        self.canvas.itemconfig(rid, outline="#2962ff", width=2.5)
                    else:
                        self.canvas.itemconfig(rid, outline=clr["border"], width=1.5)
            info = node.title
            if node.subtitle:
                info += f" · {node.subtitle}"
            self.status_label.config(text=info)
            if self.on_node_select:
                self.on_node_select({
                    "type": "ast_node",
                    "title": node.title,
                    "subtitle": node.subtitle,
                    "ast_node": node.ast_node,
                })

    def _redraw_keeping_collapsed(self):
        if self.root_node is None:
            return
        collapsed_ids = set()
        def collect_collapsed(node):
            if node.collapsed:
                collapsed_ids.add(id(node.ast_node))
            for child in node.children:
                collect_collapsed(child)
        collect_collapsed(self.root_node)

        self.canvas.delete("all")
        self._node_map = {}
        self._edge_ids = []
        self._node_rect_ids = {}
        self._node_shadow_ids = {}
        self._all_nodes_list = []
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

    def _do_search(self):
        query = self.search_var.get().strip().lower()
        # Reset highlighting
        for nid, rid in self._node_rect_ids.items():
            n = self._node_map.get(nid)
            if n:
                clr = n.colors
                outline = "#2962ff" if n is self._selected_node else clr["border"]
                width = 2.5 if n is self._selected_node else 1.5
                self.canvas.itemconfig(rid, outline=outline, width=width)

        if not query:
            self._search_results = []
            self._search_index = 0
            self.search_count_label.config(text="")
            return

        self._search_results = [
            n for n in self._all_nodes_list
            if query in n.title.lower() or (n.subtitle and query in n.subtitle.lower())
        ]
        self._search_index = 0

        if self._search_results:
            for n in self._search_results:
                nid = id(n)
                if nid in self._node_rect_ids:
                    self.canvas.itemconfig(self._node_rect_ids[nid],
                                           outline="#f9ab00", width=3)
            # Focus first result
            first = self._search_results[0]
            bbox = self.canvas.bbox(self._node_rect_ids.get(id(first), 0))
            if bbox:
                self.canvas.see(self._node_rect_ids[id(first)])
            self.search_count_label.config(
                text=f"找到 {len(self._search_results)} 个"
            )
        else:
            self.search_count_label.config(text="无匹配")

    def _toggle_collapse_mode(self):
        self._collapse_mode = self.collapse_mode.get()
        mode = "折叠" if self._collapse_mode else "选择"
        self.status_label.config(text=f"{mode}模式 · 点击节点进行{mode}")

    def _on_press(self, event):
        self._drag_start = (event.x, event.y)

    def _on_drag(self, event):
        if self._drag_start:
            dx = event.x - self._drag_start[0]
            dy = event.y - self._drag_start[1]
            self.canvas.xview_scroll(int(-dx), tk.UNITS)
            self.canvas.yview_scroll(int(-dy), tk.UNITS)
            self._drag_start = (event.x, event.y)

    def _on_release(self, event):
        self._drag_start = None

    def _on_mousewheel(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self._apply_zoom(factor, event.x, event.y)

    def _on_mousewheel_up(self, event):
        self._apply_zoom(1.1, event.x, event.y)

    def _on_mousewheel_down(self, event):
        self._apply_zoom(0.9, event.x, event.y)

    def _apply_zoom(self, factor, x, y):
        self._scale *= factor
        self._scale = max(0.3, min(3.0, self._scale))
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        self.canvas.scale("all", cx, cy, factor, factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _fit_scrollregion(self):
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        padding = 40
        self.canvas.configure(scrollregion=(
            bbox[0] - padding, bbox[1] - padding,
            bbox[2] + padding, bbox[3] + padding
        ))

    def _fit_to_view(self):
        if self.root_node is None:
            return
        self._redraw_keeping_collapsed()
        self.status_label.config(text="已适配窗口")

    def _zoom_in(self):
        self._apply_zoom(1.2, 400, 300)

    def _zoom_out(self):
        self._apply_zoom(0.8, 400, 300)

    def _reset_view(self):
        self._fit_to_view()
        self.status_label.config(text="视图已重置")

    def _on_canvas_resize(self, event):
        pass

    def _export_eps(self):
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
        self.canvas.delete("all")
        self.root_node = None
        self._node_map = {}
        self._edge_ids = []
        self._node_rect_ids = {}
        self._node_shadow_ids = {}
        self._all_nodes_list = []
        self._selected_node = None
        self._search_results = []
        self._search_index = 0
        self.search_count_label.config(text="")
        self.status_label.config(text="就绪")


# ═══════════════════════════════════════════════
# ErrorDisplay — Card-based messages
# ═══════════════════════════════════════════════
class ErrorDisplay(ttk.Frame):
    """Display errors/warnings/success as styled cards"""

    def __init__(self, parent):
        super().__init__(parent)
        th = get_theme()

        main = tk.Frame(self, bg=th["card_bg"], highlightbackground=th["border_light"],
                        highlightthickness=1, bd=0)
        main.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"],
                  pady=SPACING["md"])

        self.text = tk.Text(
            main, wrap=tk.WORD, font=(FONT_TEXT, 12),
            bg=th["card_bg"], fg=th["text_primary"], relief=tk.FLAT, bd=0,
            padx=SPACING["lg"], pady=SPACING["lg"]
        )
        v_scroll = ttk.Scrollbar(main, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=v_scroll.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _make_card(self, start_line, text, fg_color, bg_color, border_color):
        """Create a card-like block using Text tags"""
        end_line = start_line + 1
        self.text.tag_add("card_bg", f"{start_line}.0", f"{end_line}.0")
        self.text.tag_config("card_bg", background=bg_color, lmargin1=16, lmargin2=16,
                             rmargin=16, spacing1=8, spacing3=8,
                             borderwidth=0)
        # Draw a left border using a character
        self.text.insert(f"{start_line}.0", "  ")
        # Create border effect with a colored tag
        self.text.tag_add("card_border", f"{start_line}.0", f"{end_line}.0")
        self.text.tag_config("card_border", borderwidth=0)

    def show_errors(self, errors, title="错误信息"):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        th = get_theme()

        # Title
        self.text.tag_config("title_err", font=(FONT_TEXT, 14, "bold"),
                             foreground="#d93025", spacing1=8, spacing3=8)
        self.text.insert(tk.END, f"{title}\n", "title_err")

        for i, err in enumerate(errors[:50], 1):
            # Error card — red
            self.text.tag_config(f"err_card_{i}", font=(FONT_TEXT, 11),
                                 foreground="#d93025",
                                 background="#fce8e6",
                                 lmargin1=20, lmargin2=20,
                                 rmargin=12, spacing1=8, spacing3=8,
                                 relief=tk.RAISED, borderwidth=1)
            self.text.insert(tk.END, f"  [{i}]  {err}\n\n", f"err_card_{i}")

        if len(errors) > 50:
            self.text.tag_config("more", font=(FONT_TEXT, 10),
                                 foreground=th["text_muted"], spacing1=4)
            self.text.insert(tk.END, f"… 还有 {len(errors) - 50} 条错误\n", "more")

        self.text.config(state=tk.DISABLED)

    def show_warnings(self, warnings, title="警告信息"):
        """Show warning cards (yellow)"""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        self.text.tag_config("title_warn", font=(FONT_TEXT, 14, "bold"),
                             foreground="#f9ab00", spacing1=8, spacing3=8)
        self.text.insert(tk.END, f"{title}\n", "title_warn")

        for i, warn in enumerate(warnings[:50], 1):
            self.text.tag_config(f"warn_card_{i}", font=(FONT_TEXT, 11),
                                 foreground="#e65100",
                                 background="#fef7e0",
                                 lmargin1=20, lmargin2=20,
                                 rmargin=12, spacing1=8, spacing3=8,
                                 relief=tk.RAISED, borderwidth=1)
            self.text.insert(tk.END, f"  [{i}]  {warn}\n\n", f"warn_card_{i}")

        self.text.config(state=tk.DISABLED)

    def show_message(self, message, title="信息"):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        th = get_theme()

        # Green success title
        self.text.tag_config("title_ok", font=(FONT_TEXT, 14, "bold"),
                             foreground="#0f9d58", spacing1=8, spacing3=8)
        self.text.insert(tk.END, f"{title}\n", "title_ok")

        # Green success card
        self.text.tag_config("body_ok", font=(FONT_TEXT, 11),
                             foreground="#1b5e20",
                             background="#e6f4ea",
                             lmargin1=20, lmargin2=20,
                             rmargin=12, spacing1=8, spacing3=8,
                             relief=tk.RAISED, borderwidth=1)
        self.text.insert(tk.END, f"  {message}\n", "body_ok")

        self.text.config(state=tk.DISABLED)

    def clear(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.config(state=tk.DISABLED)


# ═══════════════════════════════════════════════
# InfoPanel — Right-side information panel
# ═══════════════════════════════════════════════
class InfoPanel(tk.Frame):
    """Right-side panel with tabs: Properties, Token Detail, Symbol Table, Stats"""

    def __init__(self, parent):
        super().__init__(parent)
        th = get_theme()

        self.configure(bg=th["bg_primary"])

        # Internal notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: AST Properties
        self.prop_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.prop_frame, text="  节点属性  ")
        self._build_properties_tab()

        # Tab 2: Token Details
        self.token_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.token_frame, text="  Token 详情  ")
        self._build_token_detail_tab()

        # Tab 3: Symbol Table
        self.symbol_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.symbol_frame, text="  符号表  ")
        self._build_symbol_table_tab()

        # Tab 4: Statistics
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="  节点统计  ")
        self._build_stats_tab()

    def _build_properties_tab(self):
        th = get_theme()
        frame = tk.Frame(self.prop_frame, bg=th["bg_primary"])
        frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"], pady=SPACING["sm"])

        self.prop_title = tk.Label(
            frame, text="选择节点以查看属性", font=(FONT_TEXT, 11, "bold"),
            fg=th["text_primary"], bg=th["bg_primary"], anchor=tk.W, wraplength=220
        )
        self.prop_title.pack(fill=tk.X, pady=(0, SPACING["xs"]))

        self.prop_type_label = tk.Label(
            frame, text="", font=(FONT_TEXT, 10),
            fg=th["accent_blue"], bg=th["bg_primary"], anchor=tk.W, wraplength=220
        )
        self.prop_type_label.pack(fill=tk.X)

        self.prop_sep = tk.Frame(frame, bg=th["border_light"], height=1)
        self.prop_sep.pack(fill=tk.X, pady=SPACING["xs"])

        self.prop_text = tk.Text(
            frame, font=(FONT_CODE, 10), wrap=tk.WORD,
            bg=th["bg_tertiary"], fg=th["text_primary"],
            relief=tk.FLAT, bd=0, height=20,
            padx=SPACING["xs"], pady=SPACING["xs"]
        )
        prop_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.prop_text.yview)
        self.prop_text.configure(yscrollcommand=prop_scroll.set)
        self.prop_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prop_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_token_detail_tab(self):
        th = get_theme()
        frame = tk.Frame(self.token_frame, bg=th["bg_primary"])
        frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"], pady=SPACING["sm"])

        self.token_detail_title = tk.Label(
            frame, text="悬停或点击 Token 查看详情", font=(FONT_TEXT, 11, "bold"),
            fg=th["text_primary"], bg=th["bg_primary"], anchor=tk.W, wraplength=220
        )
        self.token_detail_title.pack(fill=tk.X, pady=(0, SPACING["xs"]))

        self.token_sep = tk.Frame(frame, bg=th["border_light"], height=1)
        self.token_sep.pack(fill=tk.X, pady=SPACING["xs"])

        self.token_detail_text = tk.Text(
            frame, font=(FONT_CODE, 10), wrap=tk.WORD,
            bg=th["bg_tertiary"], fg=th["text_primary"],
            relief=tk.FLAT, bd=0, height=15,
            padx=SPACING["xs"], pady=SPACING["xs"]
        )
        tk_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.token_detail_text.yview)
        self.token_detail_text.configure(yscrollcommand=tk_scroll.set)
        self.token_detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_symbol_table_tab(self):
        th = get_theme()
        frame = tk.Frame(self.symbol_frame, bg=th["bg_primary"])
        frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"], pady=SPACING["sm"])

        self.sym_title = tk.Label(
            frame, text="运行语法分析后显示符号表", font=(FONT_TEXT, 11, "bold"),
            fg=th["text_primary"], bg=th["bg_primary"], anchor=tk.W, wraplength=220
        )
        self.sym_title.pack(fill=tk.X, pady=(0, SPACING["xs"]))

        self.sym_sep = tk.Frame(frame, bg=th["border_light"], height=1)
        self.sym_sep.pack(fill=tk.X, pady=SPACING["xs"])

        columns = ("名称", "类型", "详情")
        style = ttk.Style()
        style.configure("Sym.Treeview", font=(FONT_TEXT, 10), rowheight=22, borderwidth=0)
        style.configure("Sym.Treeview.Heading", font=(FONT_TEXT, 9, "bold"), borderwidth=0)

        self.sym_tree = ttk.Treeview(frame, columns=columns, show="headings",
                                     height=12, style="Sym.Treeview")
        for col in columns:
            self.sym_tree.heading(col, text=col)
            self.sym_tree.column(col, width=70, anchor=tk.W)

        sym_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.sym_tree.yview)
        self.sym_tree.configure(yscrollcommand=sym_scroll.set)
        self.sym_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sym_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_stats_tab(self):
        th = get_theme()
        frame = tk.Frame(self.stats_frame, bg=th["bg_primary"])
        frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"], pady=SPACING["sm"])

        self.stats_title = tk.Label(
            frame, text="AST 节点统计", font=(FONT_TEXT, 11, "bold"),
            fg=th["text_primary"], bg=th["bg_primary"], anchor=tk.W
        )
        self.stats_title.pack(fill=tk.X, pady=(0, SPACING["xs"]))

        self.stats_sep = tk.Frame(frame, bg=th["border_light"], height=1)
        self.stats_sep.pack(fill=tk.X, pady=SPACING["xs"])

        self.stats_text = tk.Text(
            frame, font=(FONT_CODE, 10), wrap=tk.WORD,
            bg=th["bg_tertiary"], fg=th["text_primary"],
            relief=tk.FLAT, bd=0, height=20,
            padx=SPACING["xs"], pady=SPACING["xs"]
        )
        st_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=st_scroll.set)
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        st_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # ── Public API ──

    def show_node_properties(self, ast_node):
        """Show properties of an AST node in the properties tab"""
        th = get_theme()
        self.prop_text.config(state=tk.NORMAL)
        self.prop_text.delete("1.0", tk.END)

        if ast_node is None:
            self.prop_text.insert(tk.END, "无节点信息")
            self.prop_text.config(state=tk.DISABLED)
            return

        node_name = get_node_ast_type_name(ast_node)
        self.prop_title.config(text=get_node_title(ast_node))
        self.prop_type_label.config(text=node_name)

        props = get_node_properties(ast_node)
        if props:
            self.prop_text.tag_config("prop_key", font=(FONT_TEXT, 9, "bold"),
                                      foreground=th["text_secondary"])
            self.prop_text.tag_config("prop_val", font=(FONT_TEXT, 10),
                                      foreground=th["text_primary"])
            for key, val in props:
                self.prop_text.insert(tk.END, f"{key}: ", "prop_key")
                self.prop_text.insert(tk.END, f"{val}\n", "prop_val")
        else:
            self.prop_text.insert(tk.END, "(无详细属性)")

        self.prop_text.config(state=tk.DISABLED)

    def show_token_detail(self, info):
        """Show token detail info"""
        th = get_theme()
        self.token_detail_text.config(state=tk.NORMAL)
        self.token_detail_text.delete("1.0", tk.END)

        if info is None:
            self.token_detail_text.insert(tk.END, "悬停或点击 Token 查看详情")
            self.token_detail_text.config(state=tk.DISABLED)
            return

        self.token_detail_title.config(text=f"Token: {info.get('value', '')}")

        self.token_detail_text.tag_config("tk_key", font=(FONT_TEXT, 9, "bold"),
                                          foreground=th["text_secondary"])
        self.token_detail_text.tag_config("tk_val", font=(FONT_TEXT, 10),
                                          foreground=th["text_primary"])

        for key, val in info.items():
            if key != "type":
                self.token_detail_text.insert(tk.END, f"{key}: ", "tk_key")
                self.token_detail_text.insert(tk.END, f"{val}\n", "tk_val")

        self.token_detail_text.config(state=tk.DISABLED)

    def show_symbol_table(self, ast_root):
        """Populate symbol table from AST"""
        for item in self.sym_tree.get_children():
            self.sym_tree.delete(item)

        if ast_root is None:
            self.sym_title.config(text="无 AST 数据")
            return

        symbols = collect_symbols(ast_root)
        self.sym_title.config(text=f"符号表 ({len(symbols)} 项)")

        for sym in symbols:
            self.sym_tree.insert("", tk.END, values=(
                sym["name"], sym["type"], sym["detail"]
            ))

    def show_statistics(self, ast_root):
        """Show AST statistics"""
        th = get_theme()
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)

        if ast_root is None:
            self.stats_text.insert(tk.END, "无 AST 数据")
            self.stats_text.config(state=tk.DISABLED)
            return

        total = count_ast_nodes(ast_root)
        depth = get_ast_depth(ast_root)
        type_counts = count_node_types(ast_root)

        self.stats_title.config(text=f"AST 统计 · {total} 节点")

        # Color tags
        self.stats_text.tag_config("stat_header", font=(FONT_TEXT, 10, "bold"),
                                   foreground=th["text_primary"])
        self.stats_text.tag_config("stat_key", font=(FONT_TEXT, 10),
                                   foreground=th["text_secondary"])
        self.stats_text.tag_config("stat_val", font=(FONT_TEXT, 10, "bold"),
                                   foreground=th["accent_blue"])
        self.stats_text.tag_config("stat_lbl", font=(FONT_TEXT, 10),
                                   foreground=th["text_primary"])

        self.stats_text.insert(tk.END, "总览\n", "stat_header")
        self.stats_text.insert(tk.END, f"节点总数: ", "stat_key")
        self.stats_text.insert(tk.END, f"{total}\n", "stat_val")
        self.stats_text.insert(tk.END, f"最大深度: ", "stat_key")
        self.stats_text.insert(tk.END, f"{depth}\n\n", "stat_val")

        self.stats_text.insert(tk.END, "节点类型分布\n", "stat_header")
        # Sort by count descending
        sorted_types = sorted(type_counts.items(), key=lambda x: -x[1])
        for name, count in sorted_types:
            self.stats_text.insert(tk.END, f"{name}: ", "stat_lbl")
            self.stats_text.insert(tk.END, f"{count}\n", "stat_val")

        self.stats_text.config(state=tk.DISABLED)

    def clear_all(self):
        """Clear all info panel contents"""
        self.prop_text.config(state=tk.NORMAL)
        self.prop_text.delete("1.0", tk.END)
        self.prop_text.config(state=tk.DISABLED)
        self.prop_title.config(text="选择节点以查看属性")
        self.prop_type_label.config(text="")

        self.token_detail_text.config(state=tk.NORMAL)
        self.token_detail_text.delete("1.0", tk.END)
        self.token_detail_text.config(state=tk.DISABLED)
        self.token_detail_title.config(text="悬停或点击 Token 查看详情")

        for item in self.sym_tree.get_children():
            self.sym_tree.delete(item)
        self.sym_title.config(text="运行语法分析后显示符号表")

        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.config(state=tk.DISABLED)
        self.stats_title.config(text="AST 节点统计")


# ═══════════════════════════════════════════════
# ParserTracer — Records parser execution trace
# ═══════════════════════════════════════════════

class ParserTraceEvent:
    """A single event recorded during parser execution"""
    def __init__(self, step, event_type, func_name, rule,
                 token_pos, token_info, ast_info, message, stack_snapshot=None):
        self.step = step
        self.type = event_type   # 'begin','end','enter','exit','consume','error'
        self.func_name = func_name
        self.rule = rule
        self.token_pos = token_pos
        self.token_info = token_info
        self.ast_info = ast_info
        self.message = message
        self.stack_snapshot = list(stack_snapshot) if stack_snapshot else []


class ParserTracer:
    """Records parser execution trace for step-by-step process visualization.

    The Parser calls tracer methods at each step. The tracer records events
    that the ParserProcessViewer can step through or display all at once.
    """

    def __init__(self):
        self.events = []
        self._call_stack = []
        self._step = 0
        self.tokens = []
        self.final_ast = None
        self.errors = []
        self.max_depth = 0
        self._consumed_count = 0
        self._nodes_created = set()  # id(node) for unique tracking
        self._node_creation_step = {}  # id(node) -> step_number

    def reset(self):
        """Reset all state for a new parsing session"""
        self.events.clear()
        self._call_stack.clear()
        self._step = 0
        self.tokens = []
        self.final_ast = None
        self.errors = []
        self.max_depth = 0
        self._consumed_count = 0
        self._nodes_created.clear()
        self._node_creation_step.clear()

    def begin(self, tokens):
        """Called when parsing begins"""
        self.reset()
        self.tokens = tokens
        self._record('begin', '', '', 0, '', '', '开始语法分析')

    def enter(self, func_name, rule, token, pos):
        """Called when entering a parse function"""
        self._step += 1
        self._call_stack.append(func_name)
        self.max_depth = max(self.max_depth, len(self._call_stack))
        t_info = f"{token.type}:{token.value}" if token else ""
        self._record('enter', func_name, rule, pos, t_info, '',
                     f'进入 → {func_name}')

    def exit(self, func_name, result, pos):
        """Called when exiting a parse function"""
        self._step += 1
        if self._call_stack and self._call_stack[-1] == func_name:
            self._call_stack.pop()
        ast_info = self._describe_result(result)
        # Track node creation
        if isinstance(result, ASTNode):
            nid = id(result)
            if nid not in self._nodes_created:
                self._nodes_created.add(nid)
                self._node_creation_step[nid] = self._step
        self._record('exit', func_name, '', pos, '', ast_info,
                     f'退出 ← {func_name}')

    def consume(self, token, pos):
        """Called when a token is consumed"""
        self._step += 1
        self._consumed_count += 1
        t_info = f"{token.type}:{token.value}"
        self._record('consume', '', '', pos, t_info, '',
                     f'消费 Token [{token.value}]')

    def error(self, msg, token, pos):
        """Called when a parsing error occurs"""
        self._step += 1
        self.errors.append(msg)
        t_info = f"{token.type}:{token.value}" if token else ""
        self._record('error', '', '', pos, t_info, '', f'错误: {msg}')

    def end(self, ast, errors):
        """Called when parsing ends"""
        self._step += 1
        self.final_ast = ast
        self.errors = errors
        if errors:
            status = f'失败 ({len(errors)} 个错误)'
        else:
            status = '成功 ✓'
        ast_info = ast.node_name if ast else 'None'
        self._record('end', '', '', len(self.tokens) - 1 if self.tokens else 0,
                     '', ast_info, f'语法分析{status}')

    def _record(self, event_type, func_name, rule, token_pos,
                token_info, ast_info, message):
        self.events.append(ParserTraceEvent(
            self._step, event_type, func_name, rule,
            token_pos, token_info, ast_info, message,
            list(self._call_stack)
        ))

    @staticmethod
    def _describe_result(result):
        if result is None:
            return ''
        if isinstance(result, ASTNode):
            return result.node_name
        if isinstance(result, list):
            return f"list[{len(result)}]"
        if isinstance(result, tuple):
            return f"({result[0]}, ...)"
        return str(result)[:30]

    def get_current_stack_at_step(self, step_index):
        """Get the call stack snapshot at a given event index"""
        if 0 <= step_index < len(self.events):
            return self.events[step_index].stack_snapshot
        return []

    def get_rule_at_step(self, step_index):
        """Get the current grammar rule at a given event index"""
        if 0 <= step_index < len(self.events):
            ev = self.events[step_index]
            if ev.rule:
                return ev.rule
            # Walk backward to find the most recent enter with a rule
            for i in range(step_index, -1, -1):
                if self.events[i].rule:
                    return self.events[i].rule
        return ""

    def get_token_pos_at_step(self, step_index):
        """Get the token position at a given event index"""
        if 0 <= step_index < len(self.events):
            # Walk backward from this step to find latest consume/error/enter
            for i in range(step_index, -1, -1):
                ev = self.events[i]
                if ev.type == 'consume':
                    return ev.token_pos + 1  # +1 because consume records pos before increment
                if ev.type == 'error':
                    return ev.token_pos
                if ev.type == 'end':
                    return ev.token_pos
            return 0
        return 0


# ═══════════════════════════════════════════════
# ParserProcessViewer — Step-by-step Parser Visualization
# ═══════════════════════════════════════════════
class ParserProcessViewer(ttk.Frame):
    """Parser process visualization focused on recursive descent call stack.

    Layout:
      TOP:     Step controls
      MIDDLE:  [Call Stack (left) | Grammar Rule (right)]
      BOTTOM:  Stats bar
    """

    def __init__(self, parent, on_node_select=None):
        super().__init__(parent)
        self.on_node_select = on_node_select
        self.tracer = None
        self._current_step = -1
        self._total_steps = 0
        self._auto_play = False
        self._auto_play_id = None
        self._build_widgets()

    # ─────────────────────────────────────────
    # UI Construction
    # ─────────────────────────────────────────
    def _build_widgets(self):
        th = get_theme()

        # ── Top: Header ──
        header = tk.Frame(self, bg=th["bg_primary"])
        header.pack(fill=tk.X, padx=SPACING["md"], pady=(SPACING["md"], 0))

        tk.Label(
            header, text="递归下降分析过程",
            font=(FONT_TEXT, 14, "bold"),
            fg=th["text_primary"], bg=th["bg_primary"], anchor=tk.W
        ).pack(fill=tk.X)

        # ── Step controls ──
        ctrl_frame = tk.Frame(self, bg=th["bg_primary"])
        ctrl_frame.pack(fill=tk.X, padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))

        self.btn_first = self._make_ctrl_btn(ctrl_frame, "⏮ 第一步", self._go_first)
        self.btn_first.pack(side=tk.LEFT, padx=1)

        self.btn_prev = self._make_ctrl_btn(ctrl_frame, "◀ 上一步", self._go_prev)
        self.btn_prev.pack(side=tk.LEFT, padx=1)

        self.step_label = tk.Label(
            ctrl_frame, text="步骤: 0 / 0",
            font=(FONT_TEXT, 11, "bold"),
            fg=th["accent_blue"], bg=th["bg_primary"]
        )
        self.step_label.pack(side=tk.LEFT, padx=SPACING["md"])

        self.btn_next = self._make_ctrl_btn(ctrl_frame, "下一步 ▶", self._go_next)
        self.btn_next.pack(side=tk.LEFT, padx=1)

        self.btn_last = self._make_ctrl_btn(ctrl_frame, "最后一步 ⏭", self._go_last)
        self.btn_last.pack(side=tk.LEFT, padx=1)

        ttk.Separator(ctrl_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=SPACING["sm"], pady=2)

        self.btn_auto = self._make_ctrl_btn(ctrl_frame, "▶ 自动播放", self._toggle_auto)
        self.btn_auto.pack(side=tk.LEFT, padx=1)

        # ── Middle: Call Stack + Grammar Rule ──
        mid_frame = tk.Frame(self, bg=th["bg_primary"])
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING["md"],
                       pady=(0, SPACING["xs"]))

        mid_frame.grid_columnconfigure(0, weight=1, uniform="mid")
        mid_frame.grid_columnconfigure(1, weight=1, uniform="mid")
        mid_frame.grid_rowconfigure(0, weight=1)

        # Left: Call Stack
        stack_card = tk.Frame(mid_frame, bg=th["card_bg"],
                              highlightbackground=th["border_light"],
                              highlightthickness=1, bd=0)
        stack_card.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["xs"]))

        tk.Label(
            stack_card, text="递归调用栈",
            font=(FONT_TEXT, 12, "bold"),
            fg=th["text_primary"], bg=th["card_bg"], anchor=tk.W
        ).pack(fill=tk.X, padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["xxs"]))

        stack_inner = tk.Frame(stack_card, bg=th["card_bg"])
        stack_inner.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"],
                         pady=(0, SPACING["sm"]))

        self.stack_canvas = tk.Canvas(stack_inner, bg=th["card_bg"],
                                      highlightthickness=0)
        stack_v_scroll = ttk.Scrollbar(stack_inner, orient=tk.VERTICAL,
                                       command=self.stack_canvas.yview)
        self.stack_canvas.configure(yscrollcommand=stack_v_scroll.set)
        self.stack_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stack_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Right: Grammar Rule
        rule_card = tk.Frame(mid_frame, bg=th["card_bg"],
                             highlightbackground=th["border_light"],
                             highlightthickness=1, bd=0)
        rule_card.grid(row=0, column=1, sticky="nsew", padx=(SPACING["xs"], 0))

        tk.Label(
            rule_card, text="当前文法规则",
            font=(FONT_TEXT, 12, "bold"),
            fg=th["text_primary"], bg=th["card_bg"], anchor=tk.W
        ).pack(fill=tk.X, padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["xxs"]))

        rule_inner = tk.Frame(rule_card, bg=th["card_bg"])
        rule_inner.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"],
                        pady=(0, SPACING["sm"]))

        self.rule_display = tk.Text(
            rule_inner, font=(FONT_CODE, 11), wrap=tk.WORD,
            bg=th["bg_tertiary"], fg=th["text_primary"],
            relief=tk.FLAT, bd=0,
            padx=SPACING["sm"], pady=SPACING["sm"],
            state=tk.DISABLED
        )
        rule_scroll = ttk.Scrollbar(rule_inner, orient=tk.VERTICAL,
                                    command=self.rule_display.yview)
        self.rule_display.configure(yscrollcommand=rule_scroll.set)
        self.rule_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rule_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Stats bar ──
        stats_frame = tk.Frame(self, bg=th["bg_secondary"],
                               highlightbackground=th["border_light"],
                               highlightthickness=1, bd=0)
        stats_frame.pack(fill=tk.X, side=tk.BOTTOM)

        stats_inner = tk.Frame(stats_frame, bg=th["bg_secondary"])
        stats_inner.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["xxs"])

        self.stats_labels = {}
        stat_items = [
            ("depth",    "深度: 0"),
            ("maxdepth", "最大深度: 0"),
            ("errors",   "错误数: 0"),
        ]
        for i, (key, text) in enumerate(stat_items):
            if i > 0:
                sep = tk.Frame(stats_inner, bg=th["border_light"], width=1)
                sep.pack(side=tk.LEFT, fill=tk.Y, padx=SPACING["sm"], pady=2)
            lbl = tk.Label(
                stats_inner, text=text,
                font=(FONT_TEXT, 10),
                fg=th["text_secondary"], bg=th["bg_secondary"]
            )
            lbl.pack(side=tk.LEFT)
            self.stats_labels[key] = lbl

        # ── Keyboard navigation ──
        self._setup_keyboard_bindings()

    def _setup_keyboard_bindings(self):
        self.configure(takefocus=1)

        def bind_all(w):
            try:
                w.bind("<Left>", lambda e: self._go_prev())
                w.bind("<Right>", lambda e: self._go_next())
                w.bind("<Home>", lambda e: self._go_first())
                w.bind("<End>", lambda e: self._go_last())
                w.bind("<space>", lambda e: self._toggle_auto())
            except:
                pass
            try:
                for c in w.winfo_children():
                    bind_all(c)
            except:
                pass

        self.after(100, lambda: bind_all(self))

    def _make_ctrl_btn(self, parent, text, cmd):
        th = get_theme()
        btn = tk.Button(
            parent, text=text, command=cmd,
            font=(FONT_TEXT, 10),
            fg=th["accent_blue"], bg=th["bg_tertiary"],
            activeforeground=th["accent_blue_hover"],
            activebackground=th["bg_hover"],
            relief=tk.FLAT, bd=0, padx=8, pady=3,
            cursor="hand2", highlightthickness=0
        )
        btn.bind("<Left>", lambda e: self._go_prev())
        btn.bind("<Right>", lambda e: self._go_next())
        return btn

    # ─────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────
    def display_trace(self, tracer):
        self.tracer = tracer
        self._current_step = -1
        self._total_steps = len(tracer.events) - 1 if tracer.events else 0
        self._go_first()

    def clear(self):
        self.tracer = None
        self._current_step = -1
        self._total_steps = 0
        self._stop_auto()
        self.stack_canvas.delete("all")
        self.rule_display.config(state=tk.NORMAL)
        self.rule_display.delete("1.0", tk.END)
        self.rule_display.config(state=tk.DISABLED)
        self.step_label.config(text="步骤: 0 / 0")
        for lbl in self.stats_labels.values():
            lbl.config(text="")

    # ─────────────────────────────────────────
    # Navigation
    # ─────────────────────────────────────────
    def _go_first(self):
        self._current_step = -1
        self._update_display()

    def _go_prev(self):
        if self._current_step > -1:
            self._current_step -= 1
            self._update_display()

    def _go_next(self):
        if self._current_step < self._total_steps:
            self._current_step += 1
            self._update_display()

    def _go_last(self):
        self._current_step = self._total_steps
        self._update_display()

    def _toggle_auto(self):
        if self._auto_play:
            self._stop_auto()
        else:
            self._start_auto()

    def _start_auto(self):
        self._auto_play = True
        self.btn_auto.config(text="⏸ 暂停")
        self._auto_step()

    def _stop_auto(self):
        self._auto_play = False
        self.btn_auto.config(text="▶ 自动播放")
        if self._auto_play_id:
            self.after_cancel(self._auto_play_id)
            self._auto_play_id = None

    def _auto_step(self):
        if not self._auto_play:
            return
        if self._current_step < self._total_steps:
            self._go_next()
            self._auto_play_id = self.after(400, self._auto_step)
        else:
            self._stop_auto()

    # ─────────────────────────────────────────
    # Rendering
    # ─────────────────────────────────────────
    def _is_error_step(self):
        if not self.tracer or self._current_step < 0:
            return False
        step = min(self._current_step, self._total_steps)
        if step < len(self.tracer.events):
            return self.tracer.events[step].type == 'error'
        return False

    def _update_display(self):
        if not self.tracer:
            return
        step = max(0, min(self._current_step, self._total_steps))
        self.step_label.config(text=f"步骤: {step} / {self._total_steps}")
        self._render_call_stack()
        self._render_grammar_rule()
        self._update_stats()

    def _render_call_stack(self):
        """Render the recursive descent call stack"""
        canvas = self.stack_canvas
        canvas.delete("all")
        th = get_theme()

        if not self.tracer or self._current_step < 0:
            canvas.create_text(12, 15, anchor=tk.W, text="等待解析…",
                               font=(FONT_TEXT, 11), fill=th["text_muted"])
            return

        step = min(self._current_step, self._total_steps)
        stack = self.tracer.get_current_stack_at_step(step)

        if not stack:
            canvas.create_text(12, 15, anchor=tk.W, text="(空)",
                               font=(FONT_TEXT, 11), fill=th["text_muted"])
            return

        font = tkfont.Font(family=FONT_TEXT, size=10)
        bold_font = tkfont.Font(family=FONT_TEXT, size=10, weight="bold")
        line_h = font.metrics("linespace") + 8
        x0, y0 = 14, 10

        # We walk the stack and draw a tree structure
        for i, func_name in enumerate(stack):
            y = y0 + i * line_h
            # Tree connector prefix
            indent = 18 * i
            is_last = (i == len(stack) - 1)
            prefix = "└ " if is_last else "├ "
            indent_str = "  " * i

            is_error = is_last and self._is_error_step()
            readable = func_name.replace("parse_", "").replace("_", " ")

            if is_last:
                # Current frame — highlight it
                text_w = font.measure(readable)
                card_w = text_w + 20
                card_h = line_h - 2
                hl_color = "#d93025" if is_error else th["accent_blue"]
                hl_bg = th["bg_selected"]
                canvas.create_rectangle(
                    x0 + indent - 2, y - 1,
                    x0 + indent + card_w, y + card_h,
                    fill=hl_bg, outline=hl_color, width=1.5
                )
                canvas.create_text(
                    x0 + indent + 2, y, anchor=tk.NW,
                    text=indent_str + prefix + readable,
                    font=bold_font, fill=hl_color
                )
            else:
                canvas.create_text(
                    x0 + indent + 2, y, anchor=tk.NW,
                    text=indent_str + prefix + readable,
                    font=font, fill=th["text_secondary"]
                )

        bbox = canvas.bbox("all")
        if bbox:
            canvas.configure(scrollregion=(0, 0, bbox[2] + 20, bbox[3] + 10))
            canvas.yview_moveto(1.0)

    def _render_grammar_rule(self):
        """Render the current grammar rule"""
        self.rule_display.config(state=tk.NORMAL)
        self.rule_display.delete("1.0", tk.END)
        th = get_theme()

        if not self.tracer or self._current_step < 0:
            self.rule_display.insert(tk.END, "等待解析…")
            self.rule_display.config(state=tk.DISABLED)
            return

        step = min(self._current_step, self._total_steps)
        ev = self.tracer.events[step] if step < len(self.tracer.events) else None
        if not ev:
            self.rule_display.insert(tk.END, "—")
            self.rule_display.config(state=tk.DISABLED)
            return

        # Current rule
        rule = self.tracer.get_rule_at_step(step)

        # Current non-terminal — walk back to most recent enter
        nonterminal = ""
        for i in range(step, -1, -1):
            if self.tracer.events[i].type == 'enter':
                nonterminal = self.tracer.events[i].func_name
                break

        # Status
        is_err = (ev.type == 'error')
        if is_err:
            status, sc = "✘ failed", "#d93025"
        elif ev.type == 'exit':
            status, sc = "✔ success", "#0f9d58"
        elif ev.type == 'end':
            status, sc = ("✘ failed", "#d93025") if self.tracer.errors else ("✔ success", "#0f9d58")
        else:
            status, sc = "⋯ parsing", th["text_muted"]

        # Tags
        self.rule_display.tag_config("h1", font=(FONT_TEXT, 11, "bold"),
                                     foreground=th["text_primary"])
        self.rule_display.tag_config("h2", font=(FONT_TEXT, 10, "bold"),
                                     foreground=th["text_secondary"])
        self.rule_display.tag_config("body", font=(FONT_CODE, 10),
                                     foreground=th["text_secondary"])
        self.rule_display.tag_config("status", font=(FONT_TEXT, 11, "bold"),
                                     foreground=sc)
        self.rule_display.tag_config("err", font=(FONT_CODE, 10),
                                     foreground="#d93025")

        # Non-terminal
        if nonterminal:
            readable = nonterminal.replace("parse_", "").replace("_", " ")
            self.rule_display.insert(tk.END, "非终结符\n", "h1")
            self.rule_display.insert(tk.END, f"{readable}\n\n", "body")

        # Production rule
        if rule:
            self.rule_display.insert(tk.END, "产生式\n", "h1")
            self.rule_display.insert(tk.END, f"{rule}\n\n", "body")

        # Status
        self.rule_display.insert(tk.END, "状态\n", "h1")
        self.rule_display.insert(tk.END, f"{status}\n\n", "status")

        # Event description
        self.rule_display.insert(tk.END, "事件\n", "h2")
        self.rule_display.insert(tk.END, f"{ev.message}\n", "body")

        # Error details
        if is_err:
            self.rule_display.insert(tk.END, "\n错误\n", "h1")
            self.rule_display.insert(tk.END, f"{ev.message}\n", "err")

        self.rule_display.config(state=tk.DISABLED)

    def _update_stats(self):
        if not self.tracer or self._current_step < 0:
            return

        step = min(self._current_step, self._total_steps)
        stack = self.tracer.get_current_stack_at_step(step)
        depth = len(stack)

        self.stats_labels["depth"].config(text=f"深度: {depth}")
        self.stats_labels["maxdepth"].config(text=f"最大深度: {self.tracer.max_depth}")
        err_count = len(self.tracer.errors)
        self.stats_labels["errors"].config(text=f"错误数: {err_count}")

        if err_count > 0:
            self.stats_labels["errors"].config(fg="#d93025")
        else:
            self.stats_labels["errors"].config(fg=get_theme()["text_secondary"])
