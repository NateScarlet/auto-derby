# -*- coding=UTF-8 -*-
# This typing file was generated by typing_from_help.py
"""
win32api - Wraps general API functions that are not subsumed in the more specific modules

"""

import typing

PyDISPLAY_DEVICEType: typing.Any

class error(Exception):
    """
    error(*args, **kw)

    Common base class for all non-exit exceptions.
    """

    __weakref__: ...
    """
    list of weak references to the object (if defined)
    """
    def __init__(self, *args, **kw):
        """ """
        ...
    ...

def AbortSystemShutdown(*args, **kwargs):
    """ """
    ...

def Apply(*args, **kwargs):
    """ """
    ...

def Beep(*args, **kwargs):
    """ """
    ...

def BeginUpdateResource(*args, **kwargs):
    """ """
    ...

def ChangeDisplaySettings(*args, **kwargs):
    """ """
    ...

def ChangeDisplaySettingsEx(*args, **kwargs):
    """ """
    ...

def ClipCursor(*args, **kwargs):
    """ """
    ...

def CloseHandle(*args, **kwargs):
    """ """
    ...

def CommandLineToArgv(*args, **kwargs):
    """ """
    ...

def CopyFile(*args, **kwargs):
    """ """
    ...

def DebugBreak(*args, **kwargs):
    """ """
    ...

def DeleteFile(*args, **kwargs):
    """ """
    ...

def DragFinish(*args, **kwargs):
    """ """
    ...

def DragQueryFile(*args, **kwargs):
    """ """
    ...

def DuplicateHandle(*args, **kwargs):
    """ """
    ...

def EndUpdateResource(*args, **kwargs):
    """ """
    ...

def EnumDisplayDevices(*args, **kwargs):
    """ """
    ...

def EnumDisplayMonitors(*args, **kwargs):
    """ """
    ...

def EnumDisplaySettings(*args, **kwargs):
    """ """
    ...

def EnumDisplaySettingsEx(*args, **kwargs):
    """ """
    ...

def EnumResourceLanguages(*args, **kwargs):
    """ """
    ...

def EnumResourceNames(*args, **kwargs):
    """ """
    ...

def EnumResourceTypes(*args, **kwargs):
    """ """
    ...

def ExitWindows(*args, **kwargs):
    """ """
    ...

def ExitWindowsEx(*args, **kwargs):
    """ """
    ...

def ExpandEnvironmentStrings(*args, **kwargs):
    """ """
    ...

def FindCloseChangeNotification(*args, **kwargs):
    """ """
    ...

def FindExecutable(*args, **kwargs):
    """ """
    ...

def FindFiles(*args, **kwargs):
    """ """
    ...

def FindFirstChangeNotification(*args, **kwargs):
    """ """
    ...

def FindNextChangeNotification(*args, **kwargs):
    """ """
    ...

def FormatMessage(*args, **kwargs):
    """ """
    ...

def FormatMessageW(*args, **kwargs):
    """ """
    ...

def FreeLibrary(*args, **kwargs):
    """ """
    ...

def GenerateConsoleCtrlEvent(*args, **kwargs):
    """ """
    ...

def GetAsyncKeyState(*args, **kwargs):
    """ """
    ...

def GetCommandLine(*args, **kwargs):
    """ """
    ...

def GetComputerName(*args, **kwargs):
    """ """
    ...

def GetComputerNameEx(*args, **kwargs):
    """ """
    ...

def GetComputerObjectName(*args, **kwargs):
    """ """
    ...

def GetConsoleTitle(*args, **kwargs):
    """ """
    ...

def GetCurrentProcess(*args, **kwargs):
    """ """
    ...

def GetCurrentProcessId(*args, **kwargs):
    """ """
    ...

def GetCurrentThread(*args, **kwargs):
    """ """
    ...

def GetCurrentThreadId(*args, **kwargs):
    """ """
    ...

def GetCursorPos(*args, **kwargs):
    """ """
    ...

def GetDateFormat(*args, **kwargs):
    """ """
    ...

def GetDiskFreeSpace(*args, **kwargs):
    """ """
    ...

def GetDiskFreeSpaceEx(*args, **kwargs):
    """ """
    ...

def GetDllDirectory(*args, **kwargs):
    """ """
    ...

def GetDomainName(*args, **kwargs):
    """ """
    ...

def GetEnvironmentVariable(*args, **kwargs):
    """ """
    ...

def GetEnvironmentVariableW(*args, **kwargs):
    """ """
    ...

def GetFileAttributes(*args, **kwargs):
    """ """
    ...

def GetFileVersionInfo(*args, **kwargs):
    """ """
    ...

def GetFocus(*args, **kwargs):
    """ """
    ...

def GetFullPathName(*args, **kwargs):
    """ """
    ...

def GetHandleInformation(*args, **kwargs):
    """ """
    ...

def GetKeyState(*args, **kwargs):
    """ """
    ...

def GetKeyboardLayout(*args, **kwargs):
    """ """
    ...

def GetKeyboardLayoutList(*args, **kwargs):
    """ """
    ...

def GetKeyboardLayoutName(*args, **kwargs):
    """ """
    ...

def GetKeyboardState(*args, **kwargs):
    """ """
    ...

def GetLastError(*args, **kwargs):
    """ """
    ...

def GetLastInputInfo(*args, **kwargs):
    """ """
    ...

def GetLocalTime(*args, **kwargs):
    """ """
    ...

def GetLogicalDriveStrings(*args, **kwargs):
    """ """
    ...

def GetLogicalDrives(*args, **kwargs):
    """ """
    ...

def GetLongPathName(*args, **kwargs):
    """ """
    ...

def GetLongPathNameW(*args, **kwargs):
    """ """
    ...

def GetModuleFileName(*args, **kwargs):
    """ """
    ...

def GetModuleFileNameW(*args, **kwargs):
    """ """
    ...

def GetModuleHandle(*args, **kwargs):
    """ """
    ...

def GetMonitorInfo(*args, **kwargs):
    """ """
    ...

def GetNativeSystemInfo(*args, **kwargs):
    """ """
    ...

def GetProcAddress(*args, **kwargs):
    """ """
    ...

def GetProfileSection(*args, **kwargs):
    """ """
    ...

def GetProfileVal(*args, **kwargs):
    """ """
    ...

def GetPwrCapabilities(*args, **kwargs):
    """ """
    ...

def GetShortPathName(*args, **kwargs):
    """ """
    ...

def GetStdHandle(*args, **kwargs):
    """ """
    ...

def GetSysColor(*args, **kwargs):
    """ """
    ...

def GetSystemDefaultLCID(*args, **kwargs):
    """ """
    ...

def GetSystemDefaultLangID(*args, **kwargs):
    """ """
    ...

def GetSystemDirectory(*args, **kwargs):
    """ """
    ...

def GetSystemFileCacheSize(*args, **kwargs):
    """ """
    ...

def GetSystemInfo(*args, **kwargs):
    """ """
    ...

def GetSystemMetrics(*args, **kwargs):
    """ """
    ...

def GetSystemTime(*args, **kwargs):
    """ """
    ...

def GetTempFileName(*args, **kwargs):
    """ """
    ...

def GetTempPath(*args, **kwargs):
    """ """
    ...

def GetThreadLocale(*args, **kwargs):
    """ """
    ...

def GetTickCount(*args, **kwargs):
    """ """
    ...

def GetTimeFormat(*args, **kwargs):
    """ """
    ...

def GetTimeZoneInformation(*args, **kwargs):
    """ """
    ...

def GetUserDefaultLCID(*args, **kwargs):
    """ """
    ...

def GetUserDefaultLangID(*args, **kwargs):
    """ """
    ...

def GetUserName(*args, **kwargs):
    """ """
    ...

def GetUserNameEx(*args, **kwargs):
    """ """
    ...

def GetVersion(*args, **kwargs):
    """ """
    ...

def GetVersionEx(*args, **kwargs):
    """ """
    ...

def GetVolumeInformation(*args, **kwargs):
    """ """
    ...

def GetWindowLong(*args, **kwargs):
    """ """
    ...

def GetWindowsDirectory(*args, **kwargs):
    """ """
    ...

def GlobalMemoryStatus(*args, **kwargs):
    """ """
    ...

def GlobalMemoryStatusEx(*args, **kwargs):
    """ """
    ...

def HIBYTE(*args, **kwargs):
    """ """
    ...

def HIWORD(*args, **kwargs):
    """ """
    ...

def InitiateSystemShutdown(*args, **kwargs):
    """ """
    ...

def LOBYTE(*args, **kwargs):
    """ """
    ...

def LOWORD(*args, **kwargs):
    """ """
    ...

def LoadCursor(*args, **kwargs):
    """ """
    ...

def LoadKeyboardLayout(*args, **kwargs):
    """ """
    ...

def LoadLibrary(*args, **kwargs):
    """ """
    ...

def LoadLibraryEx(*args, **kwargs):
    """ """
    ...

def LoadResource(*args, **kwargs):
    """ """
    ...

def LoadString(*args, **kwargs):
    """ """
    ...

def MAKELANGID(*args, **kwargs):
    """ """
    ...

def MAKELONG(*args, **kwargs):
    """ """
    ...

def MAKEWORD(*args, **kwargs):
    """ """
    ...

def MapVirtualKey(*args, **kwargs):
    """ """
    ...

def MessageBeep(*args, **kwargs):
    """ """
    ...

def MessageBox(*args, **kwargs):
    """ """
    ...

def MessageBoxEx(*args, **kwargs):
    """ """
    ...

def MonitorFromPoint(*args, **kwargs):
    """ """
    ...

def MonitorFromRect(*args, **kwargs):
    """ """
    ...

def MonitorFromWindow(*args, **kwargs):
    """ """
    ...

def MoveFile(*args, **kwargs):
    """ """
    ...

def MoveFileEx(*args, **kwargs):
    """ """
    ...

def OpenProcess(*args, **kwargs):
    """ """
    ...

def OpenThread(*args, **kwargs):
    """ """
    ...

def OutputDebugString(*args, **kwargs):
    """ """
    ...

def PostMessage(*args, **kwargs):
    """ """
    ...

def PostQuitMessage(*args, **kwargs):
    """ """
    ...

def PostThreadMessage(*args, **kwargs):
    """ """
    ...

def RGB(*args, **kwargs):
    """ """
    ...

def RegCloseKey(*args, **kwargs):
    """ """
    ...

def RegConnectRegistry(*args, **kwargs):
    """ """
    ...

def RegCopyTree(*args, **kwargs):
    """ """
    ...

def RegCreateKey(*args, **kwargs):
    """ """
    ...

def RegCreateKeyEx(*args, **kwargs):
    """ """
    ...

def RegDeleteKey(*args, **kwargs):
    """ """
    ...

def RegDeleteKeyEx(*args, **kwargs):
    """ """
    ...

def RegDeleteTree(*args, **kwargs):
    """ """
    ...

def RegDeleteValue(*args, **kwargs):
    """ """
    ...

def RegEnumKey(*args, **kwargs):
    """ """
    ...

def RegEnumKeyEx(*args, **kwargs):
    """ """
    ...

def RegEnumKeyExW(*args, **kwargs):
    """ """
    ...

def RegEnumValue(*args, **kwargs):
    """ """
    ...

def RegFlushKey(*args, **kwargs):
    """ """
    ...

def RegGetKeySecurity(*args, **kwargs):
    """ """
    ...

def RegLoadKey(*args, **kwargs):
    """ """
    ...

def RegNotifyChangeKeyValue(*args, **kwargs):
    """ """
    ...

def RegOpenCurrentUser(*args, **kwargs):
    """ """
    ...

def RegOpenKey(*args, **kwargs):
    """ """
    ...

def RegOpenKeyEx(*args, **kwargs):
    """ """
    ...

def RegOpenKeyTransacted(*args, **kwargs):
    """ """
    ...

def RegOverridePredefKey(*args, **kwargs):
    """ """
    ...

def RegQueryInfoKey(*args, **kwargs):
    """ """
    ...

def RegQueryInfoKeyW(*args, **kwargs):
    """ """
    ...

def RegQueryValue(*args, **kwargs):
    """ """
    ...

def RegQueryValueEx(*args, **kwargs):
    """ """
    ...

def RegRestoreKey(*args, **kwargs):
    """ """
    ...

def RegSaveKey(*args, **kwargs):
    """ """
    ...

def RegSaveKeyEx(*args, **kwargs):
    """ """
    ...

def RegSetKeySecurity(*args, **kwargs):
    """ """
    ...

def RegSetValue(*args, **kwargs):
    """ """
    ...

def RegSetValueEx(*args, **kwargs):
    """ """
    ...

def RegUnLoadKey(*args, **kwargs):
    """ """
    ...

def RegisterWindowMessage(*args, **kwargs):
    """ """
    ...

def SearchPath(*args, **kwargs):
    """ """
    ...

def SendMessage(*args, **kwargs):
    """ """
    ...

def SetClassLong(*args, **kwargs):
    """ """
    ...

def SetClassWord(*args, **kwargs):
    """ """
    ...

def SetConsoleCtrlHandler(*args, **kwargs):
    """ """
    ...

def SetConsoleTitle(*args, **kwargs):
    """ """
    ...

def SetCursor(*args, **kwargs):
    """ """
    ...

def SetCursorPos(*args, **kwargs):
    """ """
    ...

def SetDllDirectory(*args, **kwargs):
    """ """
    ...

def SetEnvironmentVariable(*args, **kwargs):
    """ """
    ...

def SetEnvironmentVariableW(*args, **kwargs):
    """ """
    ...

def SetErrorMode(*args, **kwargs):
    """ """
    ...

def SetFileAttributes(*args, **kwargs):
    """ """
    ...

def SetHandleInformation(*args, **kwargs):
    """ """
    ...

def SetLastError(*args, **kwargs):
    """ """
    ...

def SetLocalTime(*args, **kwargs):
    """ """
    ...

def SetStdHandle(*args, **kwargs):
    """ """
    ...

def SetSysColors(*args, **kwargs):
    """ """
    ...

def SetSystemFileCacheSize(*args, **kwargs):
    """ """
    ...

def SetSystemPowerState(*args, **kwargs):
    """ """
    ...

def SetSystemTime(*args, **kwargs):
    """ """
    ...

def SetThreadLocale(*args, **kwargs):
    """ """
    ...

def SetTimeZoneInformation(*args, **kwargs):
    """ """
    ...

def SetWindowLong(*args, **kwargs):
    """ """
    ...

def ShellExecute(*args, **kwargs):
    """ """
    ...

def ShowCursor(*args, **kwargs):
    """ """
    ...

def Sleep(*args, **kwargs):
    """ """
    ...

def SleepEx(*args, **kwargs):
    """ """
    ...

def TerminateProcess(*args, **kwargs):
    """ """
    ...

def ToAsciiEx(*args, **kwargs):
    """ """
    ...

def Unicode(*args, **kwargs):
    """ """
    ...

def UpdateResource(*args, **kwargs):
    """ """
    ...

def VkKeyScan(*args, **kwargs):
    """ """
    ...

def VkKeyScanEx(*args, **kwargs):
    """ """
    ...

def WinExec(*args, **kwargs):
    """ """
    ...

def WinHelp(*args, **kwargs):
    """ """
    ...

def WriteProfileSection(*args, **kwargs):
    """ """
    ...

def WriteProfileVal(*args, **kwargs):
    """ """
    ...

def keybd_event(bVK: int, bScan: int, dwFlags: int, dwExtraInfo: int) -> None:
    """
    https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    """
    ...

def mouse_event(*args, **kwargs):
    """ """
    ...

NameCanonical: int = 7

NameCanonicalEx: int = 9

NameDisplay: int = 3

NameFullyQualifiedDN: int = 1

NameSamCompatible: int = 2

NameServicePrincipal: int = 10

NameUniqueId: int = 6

NameUnknown: int = 0

NameUserPrincipal: int = 8

REG_NOTIFY_CHANGE_ATTRIBUTES: int = 2

REG_NOTIFY_CHANGE_LAST_SET: int = 4

REG_NOTIFY_CHANGE_NAME: int = 1

REG_NOTIFY_CHANGE_SECURITY: int = 8

STD_ERROR_HANDLE: int = -12

STD_INPUT_HANDLE: int = -10

STD_OUTPUT_HANDLE: int = -11

VFT_APP: int = 1

VFT_DLL: int = 2

VFT_DRV: int = 3

VFT_FONT: int = 4

VFT_STATIC_LIB: int = 7

VFT_UNKNOWN: int = 0

VFT_VXD: int = 5

VOS_DOS: int = 65536

VOS_DOS_WINDOWS16: int = 65537

VOS_DOS_WINDOWS32: int = 65540

VOS_NT: int = 262144

VOS_NT_WINDOWS32: int = 262148

VOS_OS216: int = 131072

VOS_OS216_PM16: int = 131074

VOS_OS232: int = 196608

VOS_OS232_PM32: int = 196611

VOS_UNKNOWN: int = 0

VOS__PM16: int = 2

VOS__PM32: int = 3

VOS__WINDOWS16: int = 1

VOS__WINDOWS32: int = 4

VS_FF_DEBUG: int = 1

VS_FF_INFOINFERRED: int = 16

VS_FF_PATCHED: int = 4

VS_FF_PRERELEASE: int = 2

VS_FF_PRIVATEBUILD: int = 8

VS_FF_SPECIALBUILD: int = 32

__all__: ...
"""
['AbortSystemShutdown', 'Apply', 'Beep', 'BeginUpdateResourc...
"""
