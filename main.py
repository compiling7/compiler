"""Main UI for Rust-like language lexer, parser and AST visualization"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from lexer import Lexer
from parser import Parser
from visualizer_gui import TokenViewer, SyntaxTreeViewer, ASTGraphViewer, ErrorDisplay


class CompilerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("类Rust词法和语法分析工具")
        self.root.geometry("1300x780")

        # Style
        style = ttk.Style()
        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=[12, 4], font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))

        # Main container
        main_container = tk.Frame(root, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_container, text="类Rust词法和语法分析工具",
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=5)

        # Create paned window for left/right layout
        paned = tk.PanedWindow(main_container, orient=tk.HORIZONTAL,
                                sashrelief=tk.RAISED, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)

        # ── Left panel - Code input ──
        left_frame = tk.Frame(paned)

        input_label = tk.Label(left_frame, text="源代码输入",
                                font=("Arial", 12, "bold"))
        input_label.pack(pady=5)

        self.input_text = scrolledtext.ScrolledText(
            left_frame, width=50, height=30,
            font=("Consolas", 11), wrap=tk.NONE,
            bg="#F8F9FA", fg="#212529",
            insertbackground="#212529",
            relief=tk.FLAT, bd=1
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons below input
        button_frame = tk.Frame(left_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=8, padx=5)

        self.lex_button = tk.Button(
            button_frame, text="词法分析", command=self.do_lexer,
            width=12, height=1,
            bg="#3498DB", fg="white", font=("Arial", 10, "bold"),
            relief=tk.FLAT, cursor="hand2"
        )
        self.lex_button.pack(side=tk.LEFT, padx=3)

        self.parse_button = tk.Button(
            button_frame, text="语法分析", command=self.do_parser,
            width=12, height=1,
            bg="#27AE60", fg="white", font=("Arial", 10, "bold"),
            relief=tk.FLAT, cursor="hand2"
        )
        self.parse_button.pack(side=tk.LEFT, padx=3)

        self.clear_button = tk.Button(
            button_frame, text="清空结果", command=self.clear_all,
            width=12, height=1,
            bg="#E74C3C", fg="white", font=("Arial", 10, "bold"),
            relief=tk.FLAT, cursor="hand2"
        )
        self.clear_button.pack(side=tk.LEFT, padx=3)

        paned.add(left_frame, stretch="always")

        # ── Right panel - Notebook with tabs ──
        right_frame = tk.Frame(paned, bg="#f0f0f0")

        # Notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: 词法分析
        self.token_viewer = TokenViewer(self.notebook)
        self.notebook.add(self.token_viewer, text="  词法分析  ")

        # Tab 2: 语法分析
        self.syntax_viewer = SyntaxTreeViewer(self.notebook)
        self.notebook.add(self.syntax_viewer, text="  语法分析  ")

        # Tab 3: AST 图像
        self.ast_viewer = ASTGraphViewer(self.notebook)
        self.notebook.add(self.ast_viewer, text="  AST 图像  ")

        # Tab 4: 错误信息
        self.error_display = ErrorDisplay(self.notebook)
        self.notebook.add(self.error_display, text="  错误信息  ")

        paned.add(right_frame, stretch="always")

        # Status bar
        self.status_label = tk.Label(
            main_container, text="就绪", bd=1,
            relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9),
            bg="#E9ECEF"
        )
        self.status_label.pack(fill=tk.X, pady=2)

        # Insert sample code
        self.insert_sample_code()

        # Store errors for detail view
        self._last_errors = []

    def insert_sample_code(self):
        """Insert sample Rust-like code"""
        sample = '''fn main() -> i32 {
    let x: i32 = 10;
    let mut y: i32 = 5;
    y = x + 20;
    if y > 10 {
        return 1;
    } else {
        return 0;
    }
}'''
        self.input_text.insert("1.0", sample)

    def get_source(self):
        """Get source code from input"""
        source = self.input_text.get("1.0", tk.END).strip()
        if not source:
            messagebox.showwarning("警告", "请输入源代码")
            self.set_status("就绪")
            return None
        return source

    def set_status(self, text):
        """Update status bar"""
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def clear_all(self):
        """Clear all views"""
        self.token_viewer.clear()
        self.syntax_viewer.clear()
        self.ast_viewer.clear()
        self.error_display.clear()
        self._last_errors = []
        self.set_status("已清空")

    # ── Lexical Analysis ──

    def do_lexer(self):
        """Perform lexical analysis and show in token tab"""
        self.clear_all()
        self.set_status("正在进行词法分析...")
        self.notebook.select(0)  # Switch to token tab

        source = self.get_source()
        if source is None:
            return

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            # Check for errors
            error_tokens = [t for t in tokens if t.type == "ERROR"]

            # Display in token viewer
            self.token_viewer.display(source, tokens)

            if error_tokens:
                errors = [f"行 {t.line}, 列 {t.column}: {t.value}" for t in error_tokens]
                self._last_errors = errors
                self.error_display.show_errors(errors, "词法错误")
                self.set_status(f"词法分析完成，发现 {len(error_tokens)} 个错误")
            else:
                display_count = len([t for t in tokens if t.type != "EOF"])
                self.set_status(f"词法分析完成，共 {display_count} 个 Token")
                self.error_display.show_message(
                    f"词法分析成功，共识别 {display_count} 个 Token（不含EOF）\n"
                    f"未发现词法错误。",
                    "词法分析成功"
                )

        except Exception as e:
            self._last_errors = [str(e)]
            self.error_display.show_errors([str(e)], "词法分析异常")
            self.set_status("词法分析失败")
            messagebox.showerror("错误", f"词法分析错误:\n{str(e)}")

    # ── Syntax Analysis ──

    def do_parser(self):
        """Perform syntax analysis and show in syntax + AST tabs"""
        self.clear_all()
        self.set_status("正在进行语法分析...")

        source = self.get_source()
        if source is None:
            return

        try:
            # First, lexical analysis
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            # Check for lexical errors
            error_tokens = [t for t in tokens if t.type == "ERROR"]
            if error_tokens:
                errors = [f"行 {t.line}, 列 {t.column}: {t.value}" for t in error_tokens]
                self._last_errors = errors
                self.token_viewer.display(source, tokens)
                self.error_display.show_errors(errors, "词法错误 (阻止语法分析)")
                self.set_status("语法分析失败 - 存在词法错误")
                self.notebook.select(0)  # Switch to token tab to show errors
                messagebox.showerror("词法错误", "存在词法错误，无法进行语法分析")
                return

            # Perform syntax analysis
            parser = Parser(source)
            ast, errors = parser.parse()

            if errors:
                self._last_errors = errors
                self.token_viewer.display(source, tokens)
                self.error_display.show_errors(errors, "语法错误")
                self.set_status("语法分析失败")
                self.notebook.select(3)  # Switch to error tab
                messagebox.showerror("语法错误", "语法分析失败:\n" + "\n".join(errors))
                return

            # Success - populate views
            # Token tab
            self.token_viewer.display(source, tokens)

            # Syntax tree tab
            self.syntax_viewer.display(ast)
            self.notebook.select(1)  # Switch to syntax tab

            # AST graph tab
            self.ast_viewer.display(ast)

            # Show success in error tab
            self.error_display.show_message(
                "语法分析成功完成。\n\n"
                "查看语法结构：请点击「语法分析」标签页\n"
                "查看可视化 AST：请点击「AST 图像」标签页",
                "语法分析成功"
            )

            self.set_status("语法分析完成 - 成功")

        except Exception as e:
            self._last_errors = [str(e)]
            self.error_display.show_errors([str(e)], "语法分析异常")
            self.set_status("语法分析失败")
            self.notebook.select(3)
            messagebox.showerror("错误", f"语法分析错误:\n{str(e)}")


def main():
    root = tk.Tk()
    app = CompilerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
