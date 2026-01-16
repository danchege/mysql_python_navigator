# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('app.py', '.'), ('db.py', '.'), ('backup.py', '.'), ('operations.py', '.'), ('config.py', '.')],
    hiddenimports=['PIL._tkinter_finder', 'PIL.ImageTk', 'PIL.Image', 'ttkbootstrap', 'ttkthemes', 'mysql.connector', 'cryptography', 'tkinterdnd2'],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='MySQL_Navigator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
