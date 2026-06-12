#!/usr/bin/env python3
"""Build script for CompilerLab — packages the application into a single executable.

Usage:
    python build.py          # Build for current platform
    python build.py --debug  # Build with console for debugging
"""

import os
import sys
import subprocess
import shutil

# Project root
ROOT = os.path.dirname(os.path.abspath(__file__))


def check_dependencies():
    """Verify all required packages are installed."""
    required = ['flask', 'webview', 'PyInstaller']
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            missing.append(pkg)
    return missing


def build(debug=False):
    """Build the executable using PyInstaller."""
    print("=" * 60)
    print("  CompilerLab — Build Script")
    print("=" * 60)

    # Check deps
    missing = check_dependencies()
    if missing:
        print(f"\n[!] Missing packages: {', '.join(missing)}")
        print(f"    Install: pip install {' '.join(missing)}")
        return False

    # Clean previous builds
    for d in ['build', 'dist']:
        if os.path.exists(os.path.join(ROOT, d)):
            print(f"  Cleaning {d}/...")
            shutil.rmtree(os.path.join(ROOT, d))

    # Verify all source files exist
    required_files = [
        'main_app.py', 'web_app.py',
        'lexer.py', 'parser.py', 'compiler_ast.py',
        'semantic.py', 'ir_generator.py', 'assembly_generator.py',
        'token_types.py', 'visualization.py',
        'templates/index.html',
    ]
    missing_files = [f for f in required_files
                     if not os.path.exists(os.path.join(ROOT, f))]
    if missing_files:
        print(f"\n[!] Missing files: {missing_files}")
        return False

    # Verify compiler_tools directory exists (nasm.exe, GoLink.exe)
    tools_dir = os.path.join(ROOT, 'compiler_tools')
    if not os.path.isdir(tools_dir):
        print("\n[!] 缺少 compiler_tools/ 目录 (需要 nasm.exe 和 GoLink.exe)")
        print("    请将 nasm.exe 和 GoLink.exe 放入 compiler_tools/ 后重试。")
        return False

    spec_path = os.path.join(ROOT, 'CompilerLab.spec')

    print(f"\n  Source: {ROOT}")
    print(f"  Spec:   {spec_path}")
    print(f"  Debug:  {debug}")
    print()

    # For debug builds, set console=True in the spec file
    # (PyInstaller --debug flag doesn't work with .spec files)
    if debug:
        print("  [Debug mode] Setting console=True in spec...")
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec_content = f.read()
        spec_content = spec_content.replace('console=False', 'console=True')
        spec_content = spec_content.replace('debug=False', 'debug=True')
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)

    # Run PyInstaller (use python -m to avoid PATH issues)
    cmd = [sys.executable, '-m', 'PyInstaller', spec_path]

    print(f"  Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=ROOT, capture_output=False)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("  Build successful!")
        print("=" * 60)
        dist_dir = os.path.join(ROOT, 'dist')
        if os.path.exists(dist_dir):
            print(f"\n  Output directory: {dist_dir}")
            for f in os.listdir(dist_dir):
                fpath = os.path.join(dist_dir, f)
                size = os.path.getsize(fpath)
                print(f"    {f}  ({size / 1024 / 1024:.1f} MB)")
        return True
    else:
        print("\n[!] Build failed")
        return False


if __name__ == '__main__':
    debug = '--debug' in sys.argv
    success = build(debug=debug)
    sys.exit(0 if success else 1)
