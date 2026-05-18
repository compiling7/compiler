# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Collect templates and static files
# Note: In .spec files, __file__ is not defined; use relative paths
datas = []
for dirname in ('templates', 'static'):
    if os.path.isdir(dirname):
        for dirpath, dirnames, filenames in os.walk(dirname):
            for f in filenames:
                src = os.path.join(dirpath, f)
                datas.append((src, dirname))

a = Analysis(
    ['main_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'webview',
        'flask',
        'lexer',
        'parser',
        'compiler_ast',
        'semantic',
        'ir_generator',
        'assembly_generator',
        'token_types',
        'visualization',
        'web_app',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tcl', 'tk', 'tkinter',
        'test',
        'matplotlib', 'scipy', 'sympy',
        'PIL', 'Pillow',
        'cv2', 'opencv',
        'pandas',
        'notebook', 'jupyter',
        'pytest',
        'IPython',
        'zmq',
        'bokeh',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CompilerLab',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
