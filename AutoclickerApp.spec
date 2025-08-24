# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['c:\\Users\\Kirill\\Desktop\\.vs\\Python\\Autoclicker App\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('core', 'core'), ('gui', 'gui'), ('emitter.py', '.'), ('assets/2.ico', 'assets')],
    hiddenimports=['undetected_chromedriver', 'selenium', 'asyncio', 'logging'],
    hookspath=[],
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
    name='AutoclickerApp',
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
    icon=['assets\\2.ico'],
)
