# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_main_ctk.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('config', 'config'), ('icon.ico', '.')],
    hiddenimports=['src.worker_ctk', 'src.main_window_ctk', 'src.account_manager', 'src.downloader', 'src.uploader', 'src.api_endpoints', 'src.xbogus', 'customtkinter', 'requests', 'rich', 'browser_cookie3', 'playwright'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook_playwright.py'],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='douyou_assistant',
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
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='douyou_assistant',
)
app = BUNDLE(
    coll,
    name='douyou_assistant.app',
    icon='icon.ico',
    bundle_identifier=None,
)
