"""Main UI for Rust-like language lexer and parser"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, font as tkfont
from lexer import Lexer
from parser import Parser
from visualization import format_ast, format_syntax_structure


class CompilerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("类Rust词法和语法分析工具")
        self.root.geometry("1200x700")

        # Create main container
        main_container = tk.Frame(root, padx=10, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_container, text="类Rust词法和语法分析工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=5)

        # Create paned window for left/right layout
        paned = tk.PanedWindow(main_container, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)

        # Left panel - Code input
        left_frame = tk.Frame(paned)

        input_label = tk.Label(left_frame, text="源代码输入", font=("Arial", 12, "bold"))
        input_label.pack(pady=5)

        self.input_text = scrolledtext.ScrolledText(left_frame, width=50, height=30, font=("Consolas", 10))
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons below input
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5, padx=5)

        self.lex_button = tk.Button(button_frame, text="词法分析", command=self.do_lexer, width=12, height=2)
        self.lex_button.pack(side=tk.LEFT, padx=3)

        self.parse_button = tk.Button(button_frame, text="语法分析", command=self.do_parser, width=12, height=2)
        self.parse_button.pack(side=tk.LEFT, padx=3)

        self.clear_button = tk.Button(button_frame, text="清空结果", command=self.clear_output, width=12, height=2)
        self.clear_button.pack(side=tk.LEFT, padx=3)

        paned.add(left_frame, stretch="always")

        # Right panel - Output
        right_frame = tk.Frame(paned)

        output_label = tk.Label(right_frame, text="分析结果", font=("Arial", 12, "bold"))
        output_label.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(right_frame, width=60, height=30, font=("Consolas", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        paned.add(right_frame, stretch="always")

        # Status bar
        self.status_label = tk.Label(main_container, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=2)

        # Insert sample code
        self.insert_sample_code()

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

    def set_status(self, text):
        """Update status bar"""
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def append_output(self, text):
        """Append text to output"""
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    def clear_output(self):
        """Clear output text"""
        self.output_text.delete("1.0", tk.END)

    def do_lexer(self):
        """Perform lexical analysis"""
        self.clear_output()
        self.set_status("正在进行词法分析...")

        source = self.input_text.get("1.0", tk.END).strip()

        if not source:
            messagebox.showwarning("警告", "请输入源代码")
            self.set_status("就绪")
            return

        self.append_output("=" * 60)
        self.append_output("词法分析结果")
        self.append_output("=" * 60)

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            # Display tokens
            self.append_output("\nToken序列:")
            self.append_output("-" * 40)

            for i, token in enumerate(tokens):
                self.append_output(f"  [{i + 1:3}] {token.type:15} | 值: {token.value:15} | 位置: 行{token.line}, 列{token.column}")

            self.append_output("-" * 40)
            self.append_output(f"\n共识别 {len(tokens)} 个Token (包含EOF)")

            # Check for errors
            error_tokens = [t for t in tokens if t.type == "ERROR"]
            if error_tokens:
                self.append_output("\n词法错误:")
                for t in error_tokens:
                    self.append_output(f"  行 {t.line}, 列 {t.column}: {t.value}")

            self.set_status(f"词法分析完成，共 {len(tokens)} 个Token")

        except Exception as e:
            self.append_output(f"词法分析错误: {str(e)}")
            self.set_status("词法分析失败")
            messagebox.showerror("错误", f"词法分析错误:\n{str(e)}")

    def do_parser(self):
        """Perform syntax analysis"""
        self.clear_output()
        self.set_status("正在进行语法分析...")

        source = self.input_text.get("1.0", tk.END).strip()

        if not source:
            messagebox.showwarning("警告", "请输入源代码")
            self.set_status("就绪")
            return

        self.append_output("=" * 60)
        self.append_output("语法分析结果")
        self.append_output("=" * 60)

        try:
            # First perform lexical analysis
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            # Check for lexical errors
            error_tokens = [t for t in tokens if t.type == "ERROR"]
            if error_tokens:
                self.append_output("\n词法错误 (阻止语法分析):")
                for t in error_tokens:
                    self.append_output(f"  行 {t.line}, 列 {t.column}: {t.value}")
                self.set_status("语法分析失败 - 词法错误")
                return

            # Perform syntax analysis
            parser = Parser(source)
            ast, errors = parser.parse()

            if errors:
                self.append_output("\n语法错误:")
                for i, err in enumerate(errors, 1):
                    self.append_output(f"  [{i}] {err}")
                self.set_status("语法分析失败")
                messagebox.showerror("语法错误", "语法分析失败:\n" + "\n".join(errors))
                return

            # Output syntax structure
            self.append_output("\n" + "=" * 60)
            self.append_output("语法结构")
            self.append_output("=" * 60)
            syntax_output = format_syntax_structure(ast)
            self.append_output(syntax_output)

            # Output AST tree
            self.append_output("\n" + "=" * 60)
            self.append_output("抽象语法树 (AST)")
            self.append_output("=" * 60)
            ast_output = format_ast(ast)
            self.append_output(ast_output)

            self.append_output("\n" + "=" * 60)
            self.append_output("语法分析成功!")
            self.append_output("=" * 60)

            self.set_status("语法分析完成")

        except Exception as e:
            self.append_output(f"语法分析错误: {str(e)}")
            self.set_status("语法分析失败")
            messagebox.showerror("错误", f"语法分析错误:\n{str(e)}")


def main():
    root = tk.Tk()
    app = CompilerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()