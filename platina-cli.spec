# -*- mode: python ; coding: utf-8 -*-
import os
import pyfiglet

project_dir = os.path.abspath(os.getcwd())

pyfiglet_fonts = os.path.join(os.path.dirname(pyfiglet.__file__), 'fonts')

a = Analysis(
    ['platina-cli.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'platina/playbooks'), 'platina/playbooks'),
        (pyfiglet_fonts, 'pyfiglet/fonts'),
    ],
    hiddenimports=[],
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
    name='platina-cli',
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
