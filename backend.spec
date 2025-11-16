# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['backend/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/core', 'backend/core'),
        ('backend/ai', 'backend/ai'),
        ('backend/utils', 'backend/utils'),
        ('backend/api', 'backend/api'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'pydantic',
        'pandas',
        'openpyxl',
        'pdfplumber',
        'pymupdf',
        'openai',
        'httpx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['matplotlib', 'scipy', 'tkinter'],
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
    name='FindingExcellence_Backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
