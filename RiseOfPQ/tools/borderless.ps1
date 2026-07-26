# Toggle borderless-windowed mode for Rise of Nations: EE.
# Usage:
#   powershell -File tools\borderless.ps1            # enable borderless (Fullscreen=0 at desktop res)
#   powershell -File tools\borderless.ps1 -Restore   # restore exclusive fullscreen (Fullscreen=1)

param(
    [switch]$Restore
)

$ErrorActionPreference = 'Stop'

$ini = Join-Path $env:APPDATA 'Microsoft Games\Rise of Nations\rise2.ini'
if (-not (Test-Path $ini)) {
    throw "rise2.ini not found at $ini -- has the game been run at least once?"
}

# One-time backup next to the ini
$backup = "$ini.bak"
if (-not (Test-Path $backup)) {
    Copy-Item $ini $backup
    Write-Output "Backed up original to $backup"
}

# Detect primary desktop resolution
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$w = $screen.Width
$h = $screen.Height

$content = Get-Content $ini

function Set-IniValue($lines, $key, $value) {
    $found = $false
    $out = $lines | ForEach-Object {
        if ($_ -match "^$([regex]::Escape($key))=") { $found = $true; "$key=$value" } else { $_ }
    }
    if (-not $found) { $out += "$key=$value" }
    return $out
}

if ($Restore) {
    $content = Set-IniValue $content 'Fullscreen' '1'
    Write-Output 'Restored exclusive fullscreen (Fullscreen=1).'
} else {
    $content = Set-IniValue $content 'Fullscreen' '0'
    $content = Set-IniValue $content 'Windowed Width' $w
    $content = Set-IniValue $content 'Windowed Height' $h
    $content = Set-IniValue $content 'IgnoreMinimizeOnTabOut' '1'
    Write-Output "Enabled borderless windowed at ${w}x${h} (Fullscreen=0)."
}

# rise2.ini is plain ANSI/ASCII -- write without BOM
[System.IO.File]::WriteAllLines($ini, $content)
Write-Output "Updated $ini"
