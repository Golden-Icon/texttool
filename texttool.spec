# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for TextTool.
# Build: pyinstaller --clean --noconfirm texttool.spec

import sys

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('pystray')
if sys.platform.startswith('linux'):
    hiddenimports += collect_submodules('gi')

a = Analysis(
    ['texttool.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('NotoSansMath-Regular.ttf', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'matplotlib'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='texttool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/texttool.ico' if not sys.platform.startswith('linux') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='texttool',
)