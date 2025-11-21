# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],  # PyInstaller сам найдет пути
    binaries=[],
    datas=[
        ('core', 'core'),
        ('gui', 'gui'), 
        ('emitter.py', '.'),
        ('assets/2.ico', 'assets')
    ],
    hiddenimports=[
        'undetected_chromedriver',
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.common',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support',
        'selenium.webdriver.support.expected_conditions',
        'asyncio',
        'asyncio.windows_events',
        'logging',
        'json',
        'urllib3',
        'requests',
        'charset_normalizer',
        'certifi',
        'emitter'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoclickerApp',
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
    icon='assets/2.ico',
)