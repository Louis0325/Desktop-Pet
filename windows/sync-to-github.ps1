$ErrorActionPreference = 'Stop'
$source = 'C:\Users\yumin\OneDrive\Desktop\其他\桌面寵物'
$destination = 'C:\Users\yumin\OneDrive\Documents\GitHub\Desktop-Pet\windows'
if (-not (Test-Path -LiteralPath (Join-Path $source 'package.json'))) {
    throw "Source project was not found: $source"
}
New-Item -ItemType Directory -Path $destination -Force | Out-Null
if ((Resolve-Path -LiteralPath $destination).Path -ne 'C:\Users\yumin\OneDrive\Documents\GitHub\Desktop-Pet\windows') {
    throw 'Unexpected synchronization destination.'
}
# Copy every project file, including generated assets and release artifacts.
# Mirror only the verified windows directory so obsolete generated frames disappear.
# Repository root files and Git metadata are outside this destination.
& robocopy $source $destination /MIR /IS /IT /COPY:DAT /DCOPY:DAT /XJ /XD node_modules /R:2 /W:1 /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw "Project synchronization failed: robocopy exit $LASTEXITCODE" }
$files = Get-ChildItem -LiteralPath $source -File -Recurse | Where-Object { $_.FullName -notlike '*\node_modules\*' }
foreach ($file in $files) {
    $relative = $file.FullName.Substring($source.Length + 1)
    $target = Join-Path $destination $relative
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Missing synchronized file: $relative" }
    $sourceHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    $targetHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
    if ($sourceHash -ne $targetHash) { throw "Synchronized file differs: $relative" }
}
$targetFiles = Get-ChildItem -LiteralPath $destination -File -Recurse | Where-Object { $_.FullName -notlike '*\node_modules\*' }
if ($targetFiles.Count -ne $files.Count) { throw 'Synchronized file count differs.' }
Write-Output "Synchronized and verified $($files.Count) files to $destination"

