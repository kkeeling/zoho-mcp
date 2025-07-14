# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Zoho MCP Server
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files from the zoho_mcp package
datas = []
datas += collect_data_files('mcp')
datas += collect_data_files('zoho_mcp')

# Collect all hidden imports
hiddenimports = []
hiddenimports += collect_submodules('mcp')
hiddenimports += collect_submodules('zoho_mcp')
hiddenimports += ['dotenv', 'aiohttp', 'aiocache', 'tenacity', 'httpx']

a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'pygame',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='zoho-mcp-server',
    debug=False,
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