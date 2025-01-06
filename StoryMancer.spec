# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['StoryMancer.py'],
    pathex=[],
    binaries=[],
    datas=[('model_alur_naive_bayes.pkl', '.'), ('model_tema_naive_bayes.pkl', '.'), ('model_vectorizer.pkl', '.'), ('orang.csv', '.'), ('datatempat.csv', '.'), ('Background.png', '.')],
    hiddenimports=['sklearn', 'sklearn.utils._weight_vector'],
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
    name='StoryMancer',
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
)
