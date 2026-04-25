# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[os.path.dirname(os.path.abspath(SPECFILE))],
    binaries=[],
    datas=[
        ('app', 'app'),
    ],
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'fastapi',
        'fastapi.middleware.cors',
        'pydantic',
        'pydantic_settings',
        'sqlalchemy',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.orm',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.sql.expression',
        'sqlalchemy.dialects.sqlite',
        'fitz',
        'PyMuPDF',
        'httpx',
        'networkx',
        'networkx.algorithms',
        'networkx.algorithms.centrality',
        'networkx.algorithms.components',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',            # NO local LLMs - we use Ollama Cloud
        'torchvision',
        'torchaudio',
        'transformers',     # NO heavy HuggingFace models
        'spacy',            # NO spaCy - everything via Ollama
        'spacy.lang',
        'spacy.lang.en',
        'sklearn',
        'tensorflow',
        'keras',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='visual-learner-backend',
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
