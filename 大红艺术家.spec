# -*- mode: python ; coding: utf-8 -*-
"""Windows onedir release: Python runtime, OR-Tools, Tkinter and Playwright Chromium."""
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = Path(SPEC).parent
playwright_datas, playwright_binaries, playwright_hidden = collect_all("playwright")
ortools_datas, ortools_binaries, ortools_hidden = collect_all("ortools")
numpy_datas, numpy_binaries, numpy_hidden = collect_all("numpy")

datas = [
    (str(ROOT / "core"), "core"),
    (str(ROOT / "integrations"), "integrations"),
    (str(ROOT / "ui"), "ui"),
    *playwright_datas,
    *ortools_datas,
    *numpy_datas,
]

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[*playwright_binaries, *ortools_binaries, *numpy_binaries],
    datas=datas,
    hiddenimports=[
        *playwright_hidden,
        *ortools_hidden,
        *numpy_hidden,
        *collect_submodules("google.protobuf"),
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
    ],
    excludes=["pandas", "matplotlib", "scipy", "IPython", "jupyter"],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="三角洲行动-大红艺术家", console=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name="三角洲行动-大红艺术家")
