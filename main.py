"""Compiler Frontend Visualization System

Academic Minimal + VSCode IDE + Apple Human Interface Design hybrid style.
5-panel layout: Top Toolbar | Left Source | Center Notebook | Right Info | Bottom Status
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

from lexer import Lexer
from parser import Parser
from visualizer_gui import (
    TokenViewer, SyntaxTreeViewer, ASTGraphViewer, ErrorDisplay, InfoPanel,
    ParserTracer, ParserProcessViewer,
    LIGHT,
    SPACING, FONT_TEXT, FONT_CODE, FONT_DISPLAY, RADIUS,
)

# ═══════════════════════════════════════════════
# CompilerUI — Main Application
# ═══════════════════════════════════════════════
class CompilerUI:
    """Main application with 5-panel layout"""

    def __init__(self, root):
        self.root = root
        self.root.title("类Rust 编译器前端可视化系统")
        self.root.geometry("1500x900")
        self.root.minsize(1200, 700)

        self.current_ast = None

        # ── ttk style ──
        self._init_style()

        # ── Root container ──
        root_bg = LIGHT["bg_primary"]
        self.root.configure(bg=root_bg)

        # ── Top Toolbar ──
        self._build_toolbar()

        # ── Main Content (PanedWindow: left | center | right) ──
        self._build_main_content()

        # ── Bottom Status Bar ──
        self._build_status_bar()

        # ── Initial sample code ──
        self.insert_sample_code()
        self._last_errors = []

    # ─────────────────────────────────────────
    # Style initialization
    # ─────────────────────────────────────────
    def _init_style(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        # Notebook tab style
        style.configure("Apple.TNotebook.Tab",
                        font=(FONT_TEXT, 11),
                        padding=[12, 5],
                        borderwidth=0,
                        focuscolor="none")
        style.layout("Apple.TNotebook.Tab",
                     [("Notebook.tab", {"sticky": "nswe",
                                        "children":
                                         [("Notebook.padding", {"side": "top",
                                                                "children":
                                                                 [("Notebook.label",
                                                                   {"side": "top"})]})]})])
        # Thin notebook for info panel
        style.configure("Info.TNotebook.Tab",
                        font=(FONT_TEXT, 9),
                        padding=[8, 3],
                        borderwidth=0,
                        focuscolor="none")

    # ─────────────────────────────────────────
    # Top Toolbar
    # ─────────────────────────────────────────
    def _build_toolbar(self):
        th = LIGHT
        toolbar = tk.Frame(self.root, bg=th["bg_secondary"],
                           highlightbackground=th["border_light"],
                           highlightthickness=0, bd=0)
        toolbar.pack(fill=tk.X, padx=0, pady=(0, 1))

        inner = tk.Frame(toolbar, bg=th["bg_secondary"])
        inner.pack(fill=tk.X, padx=SPACING["md"], pady=(SPACING["xs"], SPACING["xs"]))

        # App title
        tk.Label(
            inner, text="  Rust 编译器前端",
            font=(FONT_DISPLAY, 13, "bold"),
            fg=th["text_primary"], bg=th["bg_secondary"]
        ).pack(side=tk.LEFT, padx=(0, SPACING["lg"]))

        # Separator
        ttk.Separator(inner, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=SPACING["xs"], pady=2)

        # Toolbar buttons
        self._toolbar_btn(inner, "📂 打开文件", self._open_file).pack(
            side=tk.LEFT, padx=SPACING["xxs"])
        self._toolbar_btn(inner, "🔍 词法分析", self.do_lexer).pack(
            side=tk.LEFT, padx=SPACING["xxs"])
        self._toolbar_btn(inner, "🌳 语法分析", self.do_parser).pack(
            side=tk.LEFT, padx=SPACING["xxs"])

        ttk.Separator(inner, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=SPACING["sm"], pady=2)

        self._toolbar_btn(inner, "🗑 清空", self.clear_all).pack(
            side=tk.LEFT, padx=SPACING["xxs"])
        self._toolbar_btn(inner, "💾 导出", self._export_all).pack(
            side=tk.LEFT, padx=SPACING["xxs"])

        ttk.Separator(inner, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=SPACING["sm"], pady=2)

    def _toolbar_btn(self, parent, text, cmd):
        """Lightweight rounded toolbar button"""
        th = LIGHT
        return tk.Button(
            parent, text=text, command=cmd,
            font=(FONT_TEXT, 11),
            fg=th["text_primary"], bg=th["bg_tertiary"],
            activeforeground=th["accent_blue"], activebackground=th["bg_hover"],
            relief=tk.FLAT, bd=0,
            padx=10, pady=4,
            cursor="hand2", highlightthickness=0
        )

    # ─────────────────────────────────────────
    # Main Content (PanedWindow)
    # ─────────────────────────────────────────
    def _build_main_content(self):
        th = LIGHT

        # Use PanedWindow for resizable panels
        self.pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                                   bg=th["bg_primary"],
                                   sashwidth=4, sashrelief=tk.FLAT,
                                   sashpad=0)
        self.pane.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"],
                       pady=(0, SPACING["xs"]))

        # ── Left Panel: Source Code Editor ──
        left_card = tk.Frame(self.pane, bg=th["card_bg"],
                             highlightbackground=th["border_light"],
                             highlightthickness=1, bd=0)
        self.pane.add(left_card, minsize=300, width=420)

        # Header
        header = tk.Frame(left_card, bg=th["card_bg"])
        header.pack(fill=tk.X, padx=SPACING["md"], pady=(SPACING["md"], 0))
        tk.Label(
            header, text="源代码", font=(FONT_TEXT, 12, "bold"),
            fg=th["text_primary"], bg=th["card_bg"], anchor=tk.W
        ).pack(side=tk.LEFT)

        # Editor
        self.input_text = scrolledtext.ScrolledText(
            left_card, width=44, height=30,
            font=(FONT_CODE, 12), wrap=tk.NONE,
            bg=th["code_bg"], fg=th["text_primary"],
            insertbackground=th["text_primary"],
            relief=tk.FLAT, bd=0,
            highlightthickness=0,
            padx=SPACING["sm"], pady=SPACING["sm"]
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=SPACING["sm"],
                             pady=(SPACING["sm"], SPACING["md"]))

        # ── Center Panel: Notebook ──
        center_outer = tk.Frame(self.pane, bg=th["card_bg"],
                                highlightbackground=th["border_light"],
                                highlightthickness=1, bd=0)
        self.pane.add(center_outer, minsize=400, width=700)

        self.notebook = ttk.Notebook(center_outer, style="Apple.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Token Viewer
        self.token_viewer = TokenViewer(self.notebook, on_token_select=self._on_token_selected)
        self.notebook.add(self.token_viewer, text="  Token 查看  ")

        # Tab 2: Syntax Tree
        self.syntax_viewer = SyntaxTreeViewer(self.notebook, on_node_select=self._on_node_selected)
        self.notebook.add(self.syntax_viewer, text="  语法树  ")

        # Tab 3: Parser Process Viewer
        self.parser_process_viewer = ParserProcessViewer(self.notebook,
                                                         on_node_select=self._on_node_selected)
        self.notebook.add(self.parser_process_viewer, text="  语法分析过程  ")

        # Tab 4: AST Graph
        self.ast_viewer = ASTGraphViewer(self.notebook, on_node_select=self._on_node_selected)
        self.notebook.add(self.ast_viewer, text="  AST 视图  ")

        # Tab 5: Error Viewer
        self.error_display = ErrorDisplay(self.notebook)
        self.notebook.add(self.error_display, text="  消息  ")

        # ── Right Panel: Info Panel ──
        right_outer = tk.Frame(self.pane, bg=th["card_bg"],
                               highlightbackground=th["border_light"],
                               highlightthickness=1, bd=0)
        self.pane.add(right_outer, minsize=240, width=300)

        self.info_panel = InfoPanel(right_outer)
        self.info_panel.pack(fill=tk.BOTH, expand=True)

    # ─────────────────────────────────────────
    # Bottom Status Bar
    # ─────────────────────────────────────────
    def _build_status_bar(self):
        th = LIGHT
        status_frame = tk.Frame(self.root, bg=th["bg_secondary"],
                                highlightbackground=th["border_light"],
                                highlightthickness=1, bd=0)
        status_frame.pack(fill=tk.X)

        inner = tk.Frame(status_frame, bg=th["bg_secondary"])
        inner.pack(fill=tk.X, padx=SPACING["md"], pady=SPACING["xxs"])

        self.status_label = tk.Label(
            inner, text="就绪 · 输入代码后点击词法分析或语法分析",
            anchor=tk.W, font=(FONT_TEXT, 10),
            fg=th["text_muted"], bg=th["bg_secondary"]
        )
        self.status_label.pack(fill=tk.X, side=tk.LEFT)

        self.line_col_label = tk.Label(
            inner, text="行 1, 列 1",
            font=(FONT_TEXT, 10),
            fg=th["text_muted"], bg=th["bg_secondary"]
        )
        self.line_col_label.pack(side=tk.RIGHT, padx=(SPACING["md"], 0))

        # Track cursor position
        self.input_text.bind("<KeyRelease>", self._update_cursor_pos)
        self.input_text.bind("<ButtonRelease-1>", self._update_cursor_pos)

    # ─────────────────────────────────────────
    # Event handlers
    # ─────────────────────────────────────────
    def _on_token_selected(self, info):
        if info:
            self.info_panel.show_token_detail(info)

    def _on_node_selected(self, info):
        if info and "ast_node" in info:
            self.info_panel.show_node_properties(info["ast_node"])

    def _update_cursor_pos(self, event=None):
        try:
            pos = self.input_text.index(tk.INSERT)
            line, col = pos.split(".")
            self.line_col_label.config(text=f"行 {line}, 列 {int(col) + 1}")
        except:
            pass

    # ─────────────────────────────────────────
    # Core actions
    # ─────────────────────────────────────────
    def get_source(self):
        source = self.input_text.get("1.0", tk.END).strip()
        if not source:
            messagebox.showwarning("提示", "请输入源代码")
            self.set_status("就绪 · 请输入源代码")
            return None
        return source

    def set_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def insert_sample_code(self):
        sample = """fn main() -> i32 {
    let x: i32 = 10;
    let mut y: i32 = 5;
    y = x + 20;
    if y > 10 {
        return 1;
    } else {
        return 0;
    }
}"""
        self.input_text.insert("1.0", sample)

    def clear_all(self):
        self.token_viewer.clear()
        self.syntax_viewer.clear()
        self.ast_viewer.clear()
        self.error_display.clear()
        self.parser_process_viewer.clear()
        self.info_panel.clear_all()
        self._last_errors = []
        self.current_ast = None
        self.set_status("已清空")

    # ── Lexical Analysis ──
    def do_lexer(self):
        self.clear_all()
        self.set_status("正在进行词法分析…")
        self.notebook.select(0)

        source = self.get_source()
        if source is None:
            return

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            error_tokens = [t for t in tokens if t.type == "ERROR"]

            self.token_viewer.display(source, tokens)

            if error_tokens:
                errors = [f"行 {t.line}, 列 {t.column}: {t.value}" for t in error_tokens]
                self._last_errors = errors
                self.error_display.show_errors(errors, "词法错误")
                self.set_status(f"词法分析完成 · 发现 {len(error_tokens)} 个错误")
            else:
                display_count = len([t for t in tokens if t.type != "EOF"])
                self.set_status(f"词法分析完成 · 共 {display_count} 个 Token")
                self.error_display.show_message(
                    f"词法分析成功，共识别 {display_count} 个 Token（不含EOF）\n未发现词法错误。",
                    "词法分析成功"
                )
        except Exception as e:
            self._last_errors = [str(e)]
            self.error_display.show_errors([str(e)], "词法分析异常")
            self.set_status("词法分析失败")
            messagebox.showerror("错误", f"词法分析错误:\n{str(e)}")

    # ── Syntax Analysis ──
    def do_parser(self):
        self.clear_all()
        self.set_status("正在进行语法分析…")

        source = self.get_source()
        if source is None:
            return

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            error_tokens = [t for t in tokens if t.type == "ERROR"]
            if error_tokens:
                errors = [f"行 {t.line}, 列 {t.column}: {t.value}" for t in error_tokens]
                self._last_errors = errors
                self.token_viewer.display(source, tokens)
                self.error_display.show_errors(errors, "词法错误 (阻止语法分析)")
                self.set_status("语法分析失败 — 存在词法错误")
                self.notebook.select(0)
                messagebox.showerror("词法错误", "存在词法错误，无法进行语法分析")
                return

            tracer = ParserTracer()
            parser = Parser(source, tracer=tracer)
            ast, errors = parser.parse()

            # Display parser trace in Parser Process Viewer
            self.parser_process_viewer.display_trace(tracer)

            if errors:
                self._last_errors = errors
                self.token_viewer.display(source, tokens)
                self.error_display.show_errors(errors, "语法错误")
                self.set_status("语法分析失败")
                self.notebook.select(3)
                messagebox.showerror("语法错误", "语法分析失败:\n" + "\n".join(errors))
                return

            # Success — display everything
            self.current_ast = ast
            self.token_viewer.display(source, tokens)
            self.syntax_viewer.display(ast)
            self.ast_viewer.display(ast)

            # Update info panel
            self.info_panel.show_symbol_table(ast)
            self.info_panel.show_statistics(ast)

            self.error_display.show_message(
                "语法分析成功完成。\n\n查看语法结构：请点击「语法树」标签页\n查看可视化 AST：请点击「AST 视图」标签页\n查看语法分析过程：请点击「语法分析过程」标签页\n右侧面板可查看符号表与节点统计",
                "语法分析成功"
            )
            self.notebook.select(1)
            self.set_status("语法分析完成 — 成功 ✓")

        except Exception as e:
            self._last_errors = [str(e)]
            self.error_display.show_errors([str(e)], "语法分析异常")
            # If tracer was created, still show partial trace
            if 'tracer' in locals():
                self.parser_process_viewer.display_trace(tracer)
            self.set_status("语法分析失败")
            self.notebook.select(3)
            messagebox.showerror("错误", f"语法分析错误:\n{str(e)}")

    # ── Open file ──
    def _open_file(self):
        path = filedialog.askopenfilename(
            title="打开 Rust 源代码文件",
            filetypes=[
                ("Rust 源文件", "*.rs"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.set_status(f"已打开: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败:\n{str(e)}")

    # ── Export ──
    def _export_all(self):
        """Export current view as text"""
        from tkinter import filedialog as fd

        # Get current tab
        current_tab = self.notebook.index(self.notebook.select())

        if current_tab == 0:
            # Token export
            path = fd.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="导出 Token 序列"
            )
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("Token 序列\n")
                        f.write("=" * 60 + "\n")
                        f.write(f"{'序号':>4}  {'类型':<12}  {'值':<20}  {'行':<4}  {'列':<4}\n")
                        f.write("-" * 60 + "\n")
                        display_tokens = [t for t in self.token_viewer.tokens if t.type != "EOF"]
                        for i, t in enumerate(display_tokens, 1):
                            f.write(f"{i:>4}  {t.type:<12}  {t.value:<20}  {t.line:<4}  {t.column:<4}\n")
                    self.set_status(f"已导出: {os.path.basename(path)}")
                except Exception as e:
                    messagebox.showerror("错误", f"导出失败:\n{str(e)}")
        elif current_tab in (1, 2) and self.current_ast:
            # Export AST info
            path = fd.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="导出 AST 信息"
            )
            if path:
                try:
                    from visualization import format_ast
                    ast_str = format_ast(self.current_ast)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("AST (抽象语法树)\n")
                        f.write("=" * 60 + "\n\n")
                        f.write(ast_str)
                    self.set_status(f"已导出: {os.path.basename(path)}")
                except Exception as e:
                    messagebox.showerror("错误", f"导出失败:\n{str(e)}")
        else:
            messagebox.showinfo("提示", "当前标签页无可导出的内容")


def main():
    root = tk.Tk()
    app = CompilerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
