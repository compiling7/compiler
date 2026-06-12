# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# spec 文件中 __file__ 不可用，使用当前工作目录
ROOT = os.getcwd()

block_cipher = None

# Collect all Python files + templates
a = Analysis(
    ['main_app.py', 'web_app.py'],
    pathex=[ROOT],
    binaries=[],
    datas=[
        ('templates/index.html', 'templates'),
    ],
    hiddenimports=['flask', 'webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'cv2',
        'tkinter', 'PyQt5', 'PySide2', 'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Bundle compiler_tools (nasm.exe, GoLink.exe) as a Tree
# This places them next to the executable at runtime
tools_tree = Tree(os.path.join(ROOT, 'compiler_tools'), prefix='compiler_tools')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    tools_tree,            # <-- bundled compiler_tools
    [],
    name='CompilerLab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # False = GUI mode (no terminal window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
