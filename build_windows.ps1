$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$version = (& python --version 2>&1).ToString()
if ($version -notmatch "Python 3\.(12|13)\.") {
    throw "请使用 Python 3.12 或 3.13 构建。当前版本: $version。Python 3.14 可能导致 OR-Tools 冻结版访问冲突。"
}

python -m venv .build-venv
& .\.build-venv\Scripts\python.exe -m pip install --upgrade pip
& .\.build-venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller

# 将 Chromium 安装到 Playwright 包内，随后由 PyInstaller 一起收集。
$env:PLAYWRIGHT_BROWSERS_PATH = "0"
& .\.build-venv\Scripts\python.exe -m playwright install chromium
& .\.build-venv\Scripts\python.exe -m PyInstaller --clean --noconfirm 大红艺术家.spec

Write-Host "完成: dist\三角洲行动-大红艺术家"
