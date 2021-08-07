function Move-LegacyDebugData() {
    $legacyPaths = @(
        "ocr_images.local",
        "screenshots.local",
        "nurturing_event_images.local",
        "single_mode_event_images.local",
        "single_mode_training_images.local",
        "last_screenshot.local.png"
    ) | Where-Object { Test-Path $_ }

    if (-not $legacyPaths) {
        return
    }    

    [void](New-Item -Force -ItemType Directory debug)
    foreach ($i in $legacyPaths) {
        Move-Item $i debug
    }
}

function Get-DebugDataPath() {
    Param (
        [int]$BackupCount=0
    )
    if ($BackupCount -eq 0) {
        return "debug"
    }
    return "debug.$BackupCount"
}
    
function Backup-DebugData() {
    Param (
        [int]$MaxBackupCount
    )
            
    for ($i = $MaxBackupCount; $i -ge 0; $i--) {
        $path = Get-DebugDataPath $i
        if (Test-Path $path) {
            if ($i -eq $MaxBackupCount) {
                Remove-Item -Recurse $path
            }
            else {
                Move-Item $path (Get-DebugDataPath ($i + 1))
            }
        }
    }
    [void](New-Item -ItemType Directory (Get-DebugDataPath))
}
        
Move-LegacyDebugData
Backup-DebugData -MaxBackupCount 3
