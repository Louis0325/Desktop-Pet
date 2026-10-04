$ErrorActionPreference = 'Stop'
$source = 'C:\Users\yumin\OneDrive\Desktop\其他\桌面寵物'
Push-Location -LiteralPath $source
try {
    & py -3.14 -m PyInstaller --noconfirm --onefile --windowed --name PhyDesktopPet --icon assets/phy.ico --add-data 'assets;assets' phy_pet.py
    if ($LASTEXITCODE -ne 0) { throw 'EXE build failed.' }
    $compiler = Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'
    & $compiler PhyDesktopPet.iss
    if ($LASTEXITCODE -ne 0) { throw 'Installer build failed.' }
    & (Join-Path $source 'sync-to-github.ps1')
} finally {
    Pop-Location
}
