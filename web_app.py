"""Flask backend for CompilerLab — serves REST API for the compiler pipeline."""

import os
import json
import sys
import shutil
import subprocess
import tempfile

# ── compiler_tools 路径查找 ──────────────────────────
# PyInstaller 打包后文件在 sys._MEIPASS 下解压；
# 开发模式下在脚本同级目录。
# 找到后加入 PATH 使 nasm.exe / golink.exe 可被发现。
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # PyInstaller 打包模式
    _tools_dir = os.path.join(sys._MEIPASS, "compiler_tools")
else:
    # 开发模式 / 普通 Python 运行
    _tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compiler_tools")

if os.path.isdir(_tools_dir):
    os.environ["PATH"] = _tools_dir + os.pathsep + os.environ.get("PATH", "")
_TOOLS_DIR = _tools_dir  # 供后续 _assemble_and_run_native 引用

from flask import Flask, request, jsonify, send_from_directory, make_response

# Ensure the project root is on sys.path
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from lexer import Lexer
from parser import Parser, ParserTracer
from semantic import SemanticAnalyzer, SemanticError
from ir_generator import IRGenerator
from assembly_generator import AssemblyGenerator
from compiler_ast import *
from token_types import Token


def _get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


app = Flask(__name__,
            static_folder=_get_resource_path("static"),
            template_folder=_get_resource_path("templates"))


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(app.template_folder, "index.html")


@app.route("/api/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


# ── Download API (for save in desktop/exe mode) ─

@app.route("/api/download", methods=["POST"])
def api_download():
    """Return content as a downloadable text file.
    This server-side approach works in PyWebView/native web views
    where JavaScript blob downloads are often blocked."""
    content = request.form.get("content", request.get_data(as_text=True))
    filename = request.form.get("filename", "compiler_output.txt")
    response = make_response(content)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response


# ── Lexer API ─────────────────────────────────

@app.route("/api/lex", methods=["POST"])
def api_lex():
    data = request.get_json()
    source = data.get("source", "")
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        return jsonify({
            "success": True,
            "tokens": [_token_to_dict(t) for t in tokens],
            "errors": [t.value for t in tokens if t.type == "ERROR"],
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ── Parser API ─────────────────────────────────

@app.route("/api/parse", methods=["POST"])
def api_parse():
    data = request.get_json()
    source = data.get("source", "")
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        error_tokens = [t for t in tokens if t.type == "ERROR"]
        if error_tokens:
            return jsonify({
                "success": False,
                "error": "存在词法错误，无法进行语法分析",
                "lex_errors": [t.value for t in error_tokens],
                "tokens": [_token_to_dict(t) for t in tokens],
            }), 400

        tracer = ParserTracer()
        parser = Parser(source, tracer=tracer)
        ast, errors = parser.parse()

        if errors:
            return jsonify({
                "success": False,
                "error": "语法分析失败",
                "parse_errors": errors,
            }), 400

        return jsonify({
            "success": True,
            "ast": _ast_to_dict(ast) if ast else None,
            "trace": tracer.get_log(),
            "trace_events": [_trace_event_to_dict(e) for e in tracer.events],
            "tokens": [_token_to_dict(t) for t in tokens],
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ── Semantic API ───────────────────────────────

@app.route("/api/semantic", methods=["POST"])
def api_semantic():
    data = request.get_json()
    source = data.get("source", "")
    try:
        # Parse first
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(source)
        ast, parse_errors = parser.parse()
        if parse_errors:
            return jsonify({"success": False, "error": "语法分析失败", "parse_errors": parse_errors}), 400

        # Semantic analysis
        analyzer = SemanticAnalyzer()
        sem_errors = analyzer.analyze(ast)

        # Extract symbol table from scopes
        symbol_table = _extract_symbol_table(analyzer)

        return jsonify({
            "success": True,
            "ast": _ast_to_dict(ast),
            "symbol_table": symbol_table,
            "semantic_errors": [_semantic_error_to_dict(e) for e in sem_errors],
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ── IR API ─────────────────────────────────────

@app.route("/api/ir", methods=["POST"])
def api_ir():
    data = request.get_json()
    source = data.get("source", "")
    try:
        # Parse first
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(source)
        ast, parse_errors = parser.parse()
        if parse_errors:
            return jsonify({"success": False, "error": "语法分析失败"}), 400
        if ast is None:
            return jsonify({"success": False, "error": "AST为空"}), 400

        # Generate IR
        ir_gen = IRGenerator()
        quads = ir_gen.generate(ast)

        return jsonify({
            "success": True,
            "quads": [_quad_to_dict(q) for q in quads],
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ── Assembly API ───────────────────────────────

@app.route("/api/asm", methods=["POST"])
def api_asm():
    data = request.get_json()
    source = data.get("source", "")
    try:
        # Parse first
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(source)
        ast, parse_errors = parser.parse()
        if parse_errors:
            return jsonify({"success": False, "error": "语法分析失败"}), 400
        if ast is None:
            return jsonify({"success": False, "error": "AST为空"}), 400

        # Generate IR
        ir_gen = IRGenerator()
        quads = ir_gen.generate(ast)

        # Generate Assembly
        asm_gen = AssemblyGenerator(quads)
        asm_code = asm_gen.generate()

        return jsonify({
            "success": True,
            "assembly": asm_code,
            "quads": [_quad_to_dict(q) for q in quads],
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ── Assembly Run API ──────────────────────────

@app.route("/api/asmrun", methods=["POST"])
def api_asmrun():
    data = request.get_json()
    source = data.get("source", "")
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(source)
        ast, parse_errors = parser.parse()
        if parse_errors:
            return jsonify({
                "success": False,
                "error": "语法分析失败",
                "stage": "parser",
                "parse_errors": parse_errors,
                "errors": [ {"message": err, "stage": "Parser"} for err in parse_errors ],
            }), 400

        analyzer = SemanticAnalyzer()
        sem_errors = analyzer.analyze(ast)
        symbol_table = _extract_symbol_table(analyzer)

        ir_gen = IRGenerator()
        quads = ir_gen.generate(ast)
        asm_gen = AssemblyGenerator(quads)
        asm_code = asm_gen.generate()

        run_result = _assemble_and_run_native(asm_code)

        return jsonify({
            "success": True,
            "tokens": [_token_to_dict(t) for t in tokens],
            "ast": _ast_to_dict(ast),
            "symbol_table": symbol_table,
            "semantic_errors": [_semantic_error_to_dict(e) for e in sem_errors],
            "errors": [_semantic_error_to_dict(e) for e in sem_errors],
            "quads": [_quad_to_dict(q) for q in quads],
            "assembly": asm_code,
            "run_result": run_result,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "stage": "runtime"}), 400


def _run_command(cmd, cwd):
    try:
        proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        return {
            "success": proc.returncode == 0,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "return_code": proc.returncode,
        }
    except subprocess.TimeoutExpired as e:
        return {"success": False, "stdout": e.stdout or "", "stderr": e.stderr or "Timeout", "return_code": None, "error": "timeout"}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": "", "return_code": None, "error": str(e)}


def _assemble_and_run_native(asm_code):
    tempdir = tempfile.mkdtemp()
    asm_path = os.path.join(tempdir, "prog.asm")
    with open(asm_path, "w", encoding="utf-8") as f:
        f.write(asm_code)

    # 首先寻找本地工具链
    # 优先使用 shutil.which（查找 PATH）；若未找到则 fallback 到 _TOOLS_DIR
    nasm_candidates = ["nasm.exe", "nasm"]
    nasm_exe = None
    for c in nasm_candidates:
        nasm_exe = shutil.which(c)
        if nasm_exe:
            break
    if nasm_exe is None and _TOOLS_DIR:
        for c in nasm_candidates:
            candidate = os.path.join(_TOOLS_DIR, c)
            if os.path.isfile(candidate):
                nasm_exe = candidate
                break

    if nasm_exe is None:
        return {"success": False, "error": "未找到 nasm/nasm.exe"}

    is_windows = sys.platform.startswith("win") or nasm_exe.endswith(".exe")

    if is_windows:
        obj_name = "prog.obj"
        out_name = "prog.exe"
        fmt = "win64"
        asm_cmd = [nasm_exe, "-f", fmt, "-o", obj_name, "prog.asm"]
        result = _run_command(asm_cmd, cwd=tempdir)
        if not result["success"]:
            return {**result, "error": result.get("stderr") or "nasm 汇编失败"}

        # Windows 下首选 golink.exe
        golink_exe = shutil.which("golink.exe")
        if golink_exe is None and _TOOLS_DIR:
            golink_candidate = os.path.join(_TOOLS_DIR, "GoLink.exe")
            if os.path.isfile(golink_candidate):
                golink_exe = golink_candidate
        if golink_exe:
            # golink: golink.exe prog.obj /console /entry:main
            link_cmd = [golink_exe, obj_name, "/console", "/entry:main"]
            result = _run_command(link_cmd, cwd=tempdir)
            if not result["success"]:
                return {**result, "error": result.get("stderr") or "golink 链接失败"}
        else:
            # 后备：尝试 gcc / clang（如 MinGW）
            linker = shutil.which("gcc.exe") or shutil.which("clang.exe") or shutil.which("gcc") or shutil.which("clang")
            if linker is None:
                return {"success": False, "error": "未找到 golink.exe 或 gcc/clang 链接器"}
            link_cmd = [linker, "-o", out_name, obj_name]
            result = _run_command(link_cmd, cwd=tempdir)
            if not result["success"]:
                return {**result, "error": result.get("stderr") or "链接失败"}

        exec_path = os.path.join(tempdir, out_name)
        run_result = _run_command([exec_path], cwd=tempdir)
        return run_result
    else:
        obj_name = "prog.o"
        out_name = "prog"
        fmt = "elf64"
        asm_cmd = [nasm_exe, "-f", fmt, "-o", obj_name, "prog.asm"]
        result = _run_command(asm_cmd, cwd=tempdir)
        if not result["success"]:
            return {**result, "error": result.get("stderr") or "nasm 汇编失败"}

        linker = shutil.which("gcc") or shutil.which("clang")
        if linker is None:
            return {"success": False, "error": "未找到 gcc 或 clang 链接器"}
        link_cmd = [linker, "-no-pie", "-o", out_name, obj_name]
        result = _run_command(link_cmd, cwd=tempdir)
        if not result["success"]:
            return {**result, "error": result.get("stderr") or "链接失败"}

        exec_path = os.path.join(tempdir, "./" + out_name)
        run_result = _run_command([exec_path], cwd=tempdir)
        return run_result


# ── Full Pipeline API ──────────────────────────

@app.route("/api/pipeline", methods=["POST"])
def api_pipeline():
    data = request.get_json()
    source = data.get("source", "")
    try:
        result = {"source": source}

        # 1. Lexer
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        result["tokens"] = [_token_to_dict(t) for t in tokens]
        result["lex_errors"] = [t.value for t in tokens if t.type == "ERROR"]

        if result["lex_errors"]:
            result["success"] = False
            result["stage"] = "lexer"
            return jsonify(result), 200

        # 2. Parser
        tracer = ParserTracer()
        parser = Parser(source, tracer=tracer)
        ast, parse_errors = parser.parse()

        result["trace"] = tracer.get_log()
        result["trace_events"] = [_trace_event_to_dict(e) for e in tracer.events]
        result["parse_errors"] = parse_errors
        result["ast"] = _ast_to_dict(ast) if ast else None

        # 3. Semantic Analysis (continue even if parse_errors exist)
        analyzer = SemanticAnalyzer()
        sem_errors = analyzer.analyze(ast)
        result["symbol_table"] = _extract_symbol_table(analyzer)
        result["semantic_errors"] = [_semantic_error_to_dict(e) for e in sem_errors]

        # 4. IR Generation (continue even if previous errors exist)
        ir_gen = IRGenerator()
        quads = ir_gen.generate(ast)
        result["quads"] = [_quad_to_dict(q) for q in quads]

        # 5. Assembly Generation (continue even if previous errors exist)
        asm_gen = AssemblyGenerator(quads)
        asm_code = asm_gen.generate()
        result["assembly"] = asm_code

        # 6. Statistics
        result["stats"] = _compute_stats(ast, tokens, quads)

        # 7. Determine overall success: only lex errors block completely
        has_lex_errors = bool(result.get("lex_errors"))
        has_parse_errors = bool(parse_errors)
        result["success"] = not has_lex_errors
        if has_lex_errors:
            result["stage"] = "lexer"
        elif has_parse_errors:
            result["stage"] = "parser"
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e), "stage": "runtime"}), 500


# ── Helper Functions ───────────────────────────

def _token_to_dict(t):
    return {
        "type": t.type,
        "value": t.value,
        "line": t.line,
        "column": t.column,
    }


def _trace_event_to_dict(e):
    return {
        "step": e.step,
        "type": e.type,
        "func_name": e.func_name or "",
        "rule": e.rule or "",
        "token_pos": e.token_pos,
        "token_info": e.token_info or "",
        "ast_info": e.ast_info or "",
        "message": e.message or "",
        "stack": e.stack_snapshot or [],
    }


def _quad_to_dict(q):
    return q.to_dict()


def _semantic_error_to_dict(err):
    """Normalize a SemanticError (or legacy string) to a serializable dict."""
    if isinstance(err, SemanticError):
        return err.to_dict()
    return {"code": "E_SEMANTIC", "message": str(err), "line": 0, "column": 0, "node": ""}


def _ast_to_dict(node):
    """Convert AST node to a dict suitable for JSON serialization & D3.js."""
    if node is None:
        return None

    d = {"name": node.node_name}

    if hasattr(node, "name") and not isinstance(getattr(node, "name", None), list):
        d["label"] = str(node.name)
    if hasattr(node, "value") and not isinstance(getattr(node, "value", None), (list, ASTNode)):
        d["label"] = str(node.value)
    if hasattr(node, "op"):
        d["label"] = str(node.op)
    if hasattr(node, "type_name"):
        d["label"] = str(node.type_name)

    # Add extra info
    extras = []
    if isinstance(node, VarDeclStmtNode):
        extras.append(f"mut={node.is_mutable}")
    elif isinstance(node, ParamNode):
        extras.append(f"mut={node.is_mutable}")
    elif isinstance(node, ForStmtNode):
        extras.append(f"mut={node.is_mutable}")
    elif isinstance(node, NumberLiteralNode):
        extras.append(f"val={node.value}")
    elif isinstance(node, ArrayLiteralNode):
        extras.append(f"cnt={len(node.elements)}")
    elif isinstance(node, BlockStmtNode):
        extras.append(f"stmts={len(node.statements)}")
    elif isinstance(node, ArrayTypeNode):
        extras.append(f"size={node.size}")
    elif isinstance(node, FuncCallNode):
        extras.append(f"args={len(node.args)}")
    if extras:
        d["extra"] = ", ".join(extras)

    children = []
    if isinstance(node, ProgramNode):
        for c in node.declarations:
            child = _ast_to_dict(c)
            if child:
                children.append(child)
    elif isinstance(node, FunctionDeclNode):
        if node.params:
            for p in node.params:
                child = _ast_to_dict(p)
                if child:
                    children.append(child)
        if node.return_type:
            children.append(_ast_to_dict(node.return_type))
        if node.body:
            children.append(_ast_to_dict(node.body))
    elif isinstance(node, ParamNode):
        if node.param_type:
            children.append(_ast_to_dict(node.param_type))
    elif isinstance(node, BlockStmtNode):
        for s in node.statements:
            child = _ast_to_dict(s)
            if child:
                children.append(child)
    elif isinstance(node, ReturnStmtNode):
        if node.expr:
            children.append(_ast_to_dict(node.expr))
    elif isinstance(node, VarDeclStmtNode):
        if node.var_type:
            children.append(_ast_to_dict(node.var_type))
        if node.init_expr:
            children.append(_ast_to_dict(node.init_expr))
    elif isinstance(node, AssignStmtNode):
        children.append(_ast_to_dict(node.left))
        children.append(_ast_to_dict(node.value))
    elif isinstance(node, ExprStmtNode):
        children.append(_ast_to_dict(node.expr))
    elif isinstance(node, IfStmtNode):
        children.append(_ast_to_dict(node.condition))
        children.append(_ast_to_dict(node.then_block))
        if node.else_block:
            children.append(_ast_to_dict(node.else_block))
    elif isinstance(node, WhileStmtNode):
        children.append(_ast_to_dict(node.condition))
        children.append(_ast_to_dict(node.body))
    elif isinstance(node, ForStmtNode):
        children.append(_ast_to_dict(node.iterable))
        children.append(_ast_to_dict(node.body))
    elif isinstance(node, LoopStmtNode):
        children.append(_ast_to_dict(node.body))
    elif isinstance(node, RangeNode):
        children.append(_ast_to_dict(node.start))
        children.append(_ast_to_dict(node.end))
    elif isinstance(node, BinaryExprNode):
        children.append(_ast_to_dict(node.left))
        children.append(_ast_to_dict(node.right))
    elif isinstance(node, FuncCallNode):
        for a in node.args:
            children.append(_ast_to_dict(a))
    elif isinstance(node, UnaryMinusNode):
        children.append(_ast_to_dict(node.expr))
    elif isinstance(node, ArrayLiteralNode):
        for e in node.elements:
            children.append(_ast_to_dict(e))
    elif isinstance(node, ArrayAccessNode):
        children.append(_ast_to_dict(node.array))
        children.append(_ast_to_dict(node.index))

    if children:
        d["children"] = children
    return d


def _extract_symbol_table(analyzer):
    """Extract flat symbol table from analyzer scopes.

    Uses the analyzer's flat symbol registry (which survives scope
    pop) so the UI can show every variable, parameter, and function
    that the semantic pass encountered.
    """
    symbols: dict = {}
    flat = analyzer.symbols.all
    for name, sym in flat.items():
        info = {
            "kind": sym.kind,
            "type": sym.type_name,
            "mutable": sym.mutable,
            "initialized": sym.initialized,
        }
        if sym.kind == "fn":
            info["params"] = [
                {"name": p.name, "type": p.type_name, "mutable": p.mutable}
                for p in sym.params
            ]
        symbols[name] = info
    return symbols


def _compute_stats(ast, tokens, quads):
    """Compute compiler statistics."""
    display_tokens = [t for t in tokens if t.type != "EOF"]
    identifiers = set()
    for t in display_tokens:
        if t.type == "ID":
            identifiers.add(t.value)

    # Count AST nodes
    ast_nodes = [1]

    def count_nodes(node):
        if node is None:
            return
        if isinstance(node, ASTNode):
            from visualization import ASTVisualizer
            viz = ASTVisualizer(None)
            children = viz._get_children(node)
            for c in children:
                if isinstance(c, ASTNode):
                    ast_nodes[0] += 1
                    count_nodes(c)

    count_nodes(ast)

    return {
        "total_tokens": len(display_tokens),
        "unique_identifiers": len(identifiers),
        "ast_nodes": ast_nodes[0],
        "ir_instructions": len(quads),
        "asm_lines": len([q for q in quads]) * 2 + 20,  # rough estimate
    }


# ── Entry point ────────────────────────────────

def create_app():
    return app


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
