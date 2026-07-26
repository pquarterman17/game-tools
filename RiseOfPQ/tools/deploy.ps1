# Deploy the Rise of PQ mod to the game's mods folder.
# Usage: powershell -File tools\deploy.ps1

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$modSrc   = Join-Path $repoRoot 'mod\Rise of PQ'
$gameDir  = 'G:\SteamLibrary\steamapps\common\Rise of Nations'
$modDst   = Join-Path $gameDir 'mods\Rise of PQ'

if (-not (Test-Path $gameDir)) {
    throw "Game directory not found: $gameDir"
}
if (-not (Test-Path (Join-Path $modSrc 'info.xml'))) {
    throw "Mod source missing info.xml: $modSrc"
}

# Mirror the mod folder (removes files deleted from the repo copy)
if (Test-Path $modDst) {
    Remove-Item -Recurse -Force $modDst
}
Copy-Item -Recurse $modSrc $modDst

$count = (Get-ChildItem -Recurse -File $modDst | Measure-Object).Count
Write-Output "Deployed $count file(s) to $modDst"
Write-Output 'Enable the mod in-game: Main Menu -> Mods -> Rise of PQ'

# Deploy standalone scripts (selectable in the game setup screen, not part of the mod overlay)
$scriptsSrc = Join-Path $repoRoot 'scripts'
$scriptsDst = Join-Path $gameDir 'scenario\Scripts'
if (Test-Path $scriptsSrc) {
    foreach ($dir in Get-ChildItem -Directory $scriptsSrc) {
        $dst = Join-Path $scriptsDst $dir.Name
        if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
        Copy-Item -Recurse $dir.FullName $dst
        Write-Output "Deployed script: $($dir.Name) -> $dst"
    }
}
