function Move-LegacyData() {
    if (Test-Path data) {
        return
    }

    $legacyPaths = @(
        "single_mode_choices.csv",
        "single_mode_choices.json",
        "single_mode_choices.json~",
        "ocr_lables.csv",
        "ocr_lables.json",
        "ocr_lables.json~"
    ) | Where-Object { Test-Path $_ }

    if (-not $legacyPaths) {
        return
    }    

    [void](New-Item -Force -ItemType Directory data)
    foreach ($i in $legacyPaths) {
        Move-Item $i data
    }
}

Move-LegacyData
