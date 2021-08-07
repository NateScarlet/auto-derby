$WorkspaceFolder = $PSScriptRoot | Split-Path -Parent | Split-Path -Parent
$env:PYTHONIOENCODING = ""
Start-Transcript "$WorkspaceFolder\launcher.log"

$ErrorActionPreference = "Stop"
Set-Location $WorkspaceFolder
[System.Environment]::CurrentDirectory = $WorkspaceFolder


try {
    $version = & git.exe describe --dirty --always 
}
catch {
}
if (-not $version) {
    $version = Get-Content "$WorkspaceFolder\version"
}

$host.ui.RawUI.WindowTitle = "auto-derby: $version"


Add-Type –AssemblyName PresentationFramework

[System.Windows.Window]$mainWindow = [Windows.Markup.XamlReader]::Load( (New-Object System.Xml.XmlNodeReader ([xml](Get-Content "$PSScriptRoot\launcher.xaml"))) )

Add-Type -Language CSharp ([string](Get-Content "$PSScriptRoot\launcher.cs"))

$data = New-Object NateScarlet.AutoDerby.DataContext -Property @{
    DefaultSingleModeChoicesDataPath = [System.IO.Path]::GetFullPath("single_mode_choices.csv")
    DefaultPythonExecutablePath      = . {
        try {
            & py.exe -3.8 -c 'import sys; print(sys.executable)'
        }
        catch {
            
        }
    }
}
$mainWindow.DataContext = $data

$mainWindow.Content.FindName('startButton').add_Click( 
    {
        $mainWindow.DialogResult = $true
        $mainWindow.Close()
    }
)
$mainWindow.Content.FindName('chooseSingleModeChoicesDataPathButton').add_Click( 
    {
        $dialog = New-Object Microsoft.Win32.SaveFileDialog -Property @{
            Title            = "Choose single mode choices"
            AddExtension     = $true
            DefaultExt       = ".json"
            Filter           = "CSV data file|*.csv|Legacy JSON data file|*.json|Any file|*.*"
            FileName         = $data.SingleModeChoicesDataPath
            InitialDirectory = (Split-Path $data.SingleModeChoicesDataPath -Parent)
        }
        if ($dialog.ShowDialog()) {
            $data.SingleModeChoicesDataPath = $dialog.FileName
        }
    }
)
$mainWindow.Content.FindName('choosePythonExecutablePathButton').add_Click( 
    {
        $dialog = New-Object Microsoft.Win32.OpenFileDialog -Property @{
            Title            = "Choose python executable"
            Filter           = "Executable|*.exe|Any file|*.*"
            FileName         = $data.PythonExecutablePath
            InitialDirectory = (Split-Path $data.PythonExecutablePath -Parent)
        }
        if ($dialog.ShowDialog()) {
            $data.PythonExecutablePath = $dialog.FileName
        }
    }
)


if (-not $mainWindow.ShowDialog()) {
    "Cancelled"
    Exit 0
}

$data | Format-List -Property (
    "Job",
    "Debug", 
    "CheckUpdate",
    "PythonExecutablePath",
    "SingleModeChoicesDataPath",
    "PauseIfRaceOrderGt",
    "Plugins",
    "TargetTrainingLevels",
    "ADBAddress",
    @{
        Name       = "Version"
        Expression = { $version }
    }, 
    @{
        Name       = "Python Version"
        Expression = { & "$($Data.PythonExecutablePath)" -VV }
    }
)


if ($data.Debug) {   
    $env:DEBUG = "auto_derby"
    $env:AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH = "debug/last_screenshot.png"
    $env:AUTO_DERBY_OCR_IMAGE_PATH = "debug/ocr_images"
    $env:AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH = "debug/single_mode_event_images"
    $env:AUTO_DERBY_SINGLE_MODE_TRAINING_IMAGE_PATH = "debug/single_mode_training_images"
    & "$WorkspaceFolder/auto_derby/launcher/rotate_debug_data.ps1"
}

if ($data.CheckUpdate) {
    $env:AUTO_DERBY_CHECK_UPDATE = "true"
}

if ($data.SingleModeChoicesDataPath) {
    $env:AUTO_DERBY_SINGLE_MODE_CHOICE_PATH = $data.SingleModeChoicesDataPath
}

$env:AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT = $data.PauseIfRaceOrderGt
$env:AUTO_DERBY_PLUGINS = $data.Plugins
$env:AUTO_DERBY_ADB_ADDRESS = $data.ADBAddress
$env:AUTO_DERBY_SINGLE_MODE_TARGET_TRAINING_LEVELS = $data.TargetTrainingLevels

$requireAdmin = (-not $data.ADBAddress)

$verb = "open"
if ($requireAdmin) {
    $verb = "runAs"
}

$command = @"
title auto-derby: $version
cd /d "$WorkspaceFolder"
set "DEBUG=$($env:DEBUG)"
set "AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH=$($env:AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH)"
set "AUTO_DERBY_OCR_IMAGE_PATH=$($env:AUTO_DERBY_OCR_IMAGE_PATH)"
set "AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH=$($env:AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH)"
set "AUTO_DERBY_SINGLE_MODE_TRAINING_IMAGE_PATH=$($env:AUTO_DERBY_SINGLE_MODE_TRAINING_IMAGE_PATH)"
set "AUTO_DERBY_SINGLE_MODE_CHOICE_PATH=$($env:AUTO_DERBY_SINGLE_MODE_CHOICE_PATH)"
set "AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT=$($env:AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT)"
set "AUTO_DERBY_PLUGINS=$($env:AUTO_DERBY_PLUGINS)"
set "AUTO_DERBY_SINGLE_MODE_TARGET_TRAINING_LEVELS=$($env:AUTO_DERBY_SINGLE_MODE_TARGET_TRAINING_LEVELS)"
set "AUTO_DERBY_ADB_ADDRESS=$($env:AUTO_DERBY_ADB_ADDRESS)"
set "AUTO_DERBY_CHECK_UPDATE=$($env:AUTO_DERBY_CHECK_UPDATE)"
"$($Data.PythonExecutablePath)" -m auto_derby $($data.Job)
exit
"@

"command: "
$command
""
Start-Process cmd.exe -Verb $verb -ArgumentList @(
    "/K",
    ($command -split "`n" -join " && ")
)


if ($data.Debug) {
    "Installed packages: "
    
    & cmd.exe /c "`"$($Data.PythonExecutablePath)`" -m pip list 2>&1" | Select-String (
        '^opencv-python\b',
        '^opencv-contrib-python\b', 
        '^pywin32\b', 
        '^numpy\b',
        '^Pillow\b',
        '^mouse\b',
        '^cast-unknown\b',
        '^adb-shell\b'
    )
    ""
}


Stop-Transcript
