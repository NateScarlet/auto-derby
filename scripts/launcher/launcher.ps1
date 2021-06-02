$WorkspaceFolder = $PSScriptRoot | Split-Path -Parent | Split-Path -Parent
$env:PYTHONIOENCODING = ""
Start-Transcript "$WorkspaceFolder\launcher.log"

# https://stackoverflow.com/a/11440595
if (-not (
        [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )
) {
    Start-Process PowerShell -Verb runAs -ArgumentList @(
        "-Version", "3",
        "-NoProfile",
        "& '" + $MyInvocation.MyCommand.Definition + "'"
    )
    return
}
            

$ErrorActionPreference = "Stop"
Set-Location $WorkspaceFolder
[System.Environment]::CurrentDirectory = $WorkspaceFolder


try {
    $version = git.exe describe --dirty --always
}
catch {
    $version = Get-Date -Format "yyyy-MM-dd HH:mm"
}
$host.ui.RawUI.WindowTitle = "auto-derby: $version"


Add-Type –AssemblyName PresentationFramework

[System.Windows.Window]$mainWindow = [Windows.Markup.XamlReader]::Load( (New-Object System.Xml.XmlNodeReader ([xml](Get-Content "$PSScriptRoot\launcher.xaml"))) )

Add-Type -Language CSharp ([string](Get-Content "$PSScriptRoot\launcher.cs"))

$data = New-Object NateScarlet.AutoDerby.DataContext -Property @{
    DefaultNurturingChoicesDataPath = [System.IO.Path]::GetFullPath("nurturing_choices.json")
    DefaultPythonExecutablePath     = . {
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
$mainWindow.Content.FindName('chooseNurturingChoicesDataPathButton').add_Click( 
    {
        $dialog = New-Object Microsoft.Win32.SaveFileDialog -Property @{
            Title            = "Choose nurturing choices"
            AddExtension     = $true
            DefaultExt       = ".json"
            Filter           = "JSON data Files|*.json"
            FileName         = $data.NurturingChoicesDataPath
            InitialDirectory = (Split-Path $data.NurturingChoicesDataPath -Parent)
        }
        if ($dialog.ShowDialog()) {
            $data.NurturingChoicesDataPath = $dialog.FileName
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


$dialogResult = $mainWindow.ShowDialog()
$data | Format-List -Property "Job", "Debug", "PythonExecutablePath", "NurturingChoicesDataPath", @{
    Name       = "Version"
    Expression = { $version }
}, @{
    Name       = "Python Version"
    Expression = { & "$($Data.PythonExecutablePath)" -VV }
}

# XXX: Powershell throw error if stderr of external command is redirected
$ErrorActionPreference = ""

if ($data.Debug) {
    "Installed packages: "
    
    & "$($Data.PythonExecutablePath)" -m pip list *>&1 | Select-String (
        '^opencv-python\b',
        '^opencv-contrib-python\b', 
        '^pywin32\b', 
        '^numpy\b',
        '^Pillow\b',
        '^mouse\b',
        '^cast-unknown\b'
    )
    ""
    $env:DEBUG = "auto_derby"
}

if ($data.NurturingChoicesDataPath) {
    $env:AUTO_DERBY_NURTURING_CHOICE_PATH = $data.NurturingChoicesDataPath
}

if ($dialogResult) {
    &  "$($data.PythonExecutablePath)" -m auto_derby $data.Job *>&1 | ForEach-Object { 

        if ($_.GetType() -eq [System.Management.Automation.ErrorRecord]) {
            Write-Host -ForegroundColor ([ConsoleColor]::Cyan)  $_ 
        }
        else {
            Write-Host $_
        }
    }
    Exit $?
}
else {
    "Cancelled"
    Exit 0
}


Stop-Transcript
