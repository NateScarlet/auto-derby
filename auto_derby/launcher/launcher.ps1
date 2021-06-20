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
    $version = Get-Date -Format "yyyy-MM-dd HH:mm"
}

$host.ui.RawUI.WindowTitle = "auto-derby: $version"


Add-Type –AssemblyName PresentationFramework

[System.Windows.Window]$mainWindow = [Windows.Markup.XamlReader]::Load( (New-Object System.Xml.XmlNodeReader ([xml](Get-Content "$PSScriptRoot\launcher.xaml"))) )

Add-Type -Language CSharp ([string](Get-Content "$PSScriptRoot\launcher.cs"))

$data = New-Object NateScarlet.AutoDerby.DataContext -Property @{
    DefaultSingleModeChoicesDataPath = [System.IO.Path]::GetFullPath("single_mode_choices.json")
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
            Filter           = "JSON data Files|*.json"
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
            Filter           = "Executable|*.exe|Any File|*.*"
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
    "PythonExecutablePath",
    "SingleModeChoicesDataPath",
    "PauseIfRaceOrderGt",
    "Plugins",
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
    $env:DEBUG = "auto_derby"
    $env:AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH = "last_screenshot.local.png"
    $env:AUTO_DERBY_OCR_IMAGE_PATH = "ocr_images.local"
    $env:AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH = "single_mode_event_images.local"
}

if ($data.SingleModeChoicesDataPath) {
    $env:AUTO_DERBY_SINGLE_MODE_CHOICE_PATH = $data.SingleModeChoicesDataPath
}

$env:AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT = $data.PauseIfRaceOrderGt
$env:AUTO_DERBY_PLUGINS = $data.Plugins
$env:AUTO_DERBY_ADB_ADDRESS = $data.ADBAddress

$requireAdmin = (-not $data.ADBAddress)

$verb = "open"
if ($requireAdmin) {
    $verb = "runAs"
}

# # https://stackoverflow.com/a/11440595
# if (-not (
#         [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
#     ).IsInRole(
#         [Security.Principal.WindowsBuiltInRole]::Administrator
#     )
# ) {
#     Start-Process PowerShell -Verb runAs -ArgumentList @(
#         "-Version", "3",
#         "-NoProfile",
#         "& '" + $MyInvocation.MyCommand.Definition + "'"
#     )
#     return
# }

$command = @"
title auto-derby: $version
cd /d "$WorkspaceFolder"
set "DEBUG=$($env:DEBUG)"
set "AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH=$($env:AUTO_DERBY_LAST_SCREENSHOT_SAVE_PATH)"
set "AUTO_DERBY_OCR_IMAGE_PATH=$($env:AUTO_DERBY_OCR_IMAGE_PATH)"
set "AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH=$($env:AUTO_DERBY_SINGLE_MODE_EVENT_IMAGE_PATH)"
set "AUTO_DERBY_SINGLE_MODE_CHOICE_PATH=$($env:AUTO_DERBY_SINGLE_MODE_CHOICE_PATH)"
set "AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT=$($env:AUTO_DERBY_PAUSE_IF_RACE_ORDER_GT)"
set "AUTO_DERBY_PLUGINS=$($env:AUTO_DERBY_PLUGINS)"
set "AUTO_DERBY_ADB_ADDRESS=$($env:AUTO_DERBY_ADB_ADDRESS)"
"$($Data.PythonExecutablePath)" -m auto_derby $($data.Job)
exit
"@

"command: "
$command
Start-Process cmd.exe -Verb $verb -ArgumentList @(
    "/K",
    ($command -split "`n" -join " && ")
)

Stop-Transcript
