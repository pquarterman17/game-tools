# Regenerate the local vanilla/ baseline from your Rise of Nations: EE install.
# vanilla/ is git-ignored (game files are not redistributed in this repo);
# run this once after cloning, and again after any Steam update to the game.
# Usage: powershell -File tools\snapshot-vanilla.ps1 [-GameDir <path>]

param(
    [string]$GameDir = 'G:\SteamLibrary\steamapps\common\Rise of Nations'
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path (Join-Path $GameDir 'riseofnations.exe'))) {
    throw "Rise of Nations install not found at: $GameDir (pass -GameDir)"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$dst = Join-Path $repoRoot 'vanilla'
New-Item -ItemType Directory -Force $dst | Out-Null

# Data XMLs the mod overrides or is likely to override
$dataFiles = @(
    'rules.xml', 'balance.xml', 'techrules.xml', 'unitrules.xml',
    'buildingrules.xml', 'resourcerules.xml', 'craftrules.xml',
    'interface.xml', 'help.xml'
)
foreach ($f in $dataFiles) {
    Copy-Item (Join-Path $GameDir "Data\$f") (Join-Path $dst $f)
}

# Root-level config references
Copy-Item (Join-Path $GameDir 'graphics.txt') (Join-Path $dst 'graphics.txt')

# User display settings reference (if the game has been run)
$ini = Join-Path $env:APPDATA 'Microsoft Games\Rise of Nations\rise2.ini'
if (Test-Path $ini) { Copy-Item $ini (Join-Path $dst 'rise2.ini') }

$count = (Get-ChildItem -File $dst | Measure-Object).Count
Write-Output "Snapshot complete: $count file(s) in $dst"
