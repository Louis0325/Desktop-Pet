$ErrorActionPreference = 'Stop'
$source = 'C:\Users\yumin\OneDrive\Desktop\其他\桌面寵物'
$destination = 'C:\Users\yumin\OneDrive\Documents\GitHub\Desktop-Pet\windows'
if (-not (Test-Path -LiteralPath (Join-Path $source 'phy_pet.py'))) {
    throw "Source project was not found: $source"
}
New-Item -ItemType Directory -Path $destination -Force | Out-Null
# Copy every project file, including generated assets and release artifacts.
# Do not delete destination-only files or traverse junctions into other folders.
& robocopy $source $destination /E /IS /IT /COPY:DAT /DCOPY:DAT /XJ /R:2 /W:1 /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw "Project synchronization failed: robocopy exit $LASTEXITCODE" }
$files = Get-ChildItem -LiteralPath $source -File -Recurse
foreach ($file in $files) {
    $relative = $file.FullName.Substring($source.Length + 1)
    $target = Join-Path $destination $relative
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Missing synchronized file: $relative" }
    $sourceHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    $targetHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
    if ($sourceHash -ne $targetHash) { throw "Synchronized file differs: $relative" }
}
Write-Output "Synchronized and verified $($files.Count) files to $destination"

