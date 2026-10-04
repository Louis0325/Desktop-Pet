$ErrorActionPreference = 'Stop'
$source = 'C:\Users\yumin\OneDrive\Desktop\其他\桌面寵物'
Push-Location -LiteralPath $source
try {
    $nodeRuntime = (Get-Command node.exe).Source
    $nodeVersion = (& $nodeRuntime --version).TrimStart('v')
    if ([version]$nodeVersion -lt [version]'22.12.0') {
        $nodeRuntime = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
        if (-not (Test-Path -LiteralPath $nodeRuntime)) { throw 'Node.js 22.12 or newer is required.' }
    }
    $npmCli = Join-Path (Split-Path (Get-Command npm.cmd).Source) 'node_modules\npm\bin\npm-cli.js'
    & $nodeRuntime $npmCli ci
    if ($LASTEXITCODE -ne 0) { throw 'JavaScript dependency installation failed.' }
    & $nodeRuntime 'node_modules\electron\install.js'
    if ($LASTEXITCODE -ne 0) { throw 'Electron installation failed.' }
    & $nodeRuntime 'node_modules\electron-builder\out\cli\cli.js' --win portable --x64 --publish never
    if ($LASTEXITCODE -ne 0) { throw 'EXE build failed.' }
    $compiler = Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'
    & $compiler PhyDesktopPet.iss
    if ($LASTEXITCODE -ne 0) { throw 'Installer build failed.' }
    & (Join-Path $source 'sync-to-github.ps1')
} finally {
    Pop-Location
}
