#define AppName "Phy 桌寵"
#define AppVersion "1.1.2"
#define AppExe "PhyDesktopPet.exe"

[Setup]
AppId={{ED515B4C-3E13-4DCE-97DA-93BDD3AC8CC8}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Phy Desktop Pet
DefaultDirName={localappdata}\Programs\PhyDesktopPet
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
OutputDir=dist
OutputBaseFilename=PhyDesktopPet-Setup
SetupIconFile=assets\phy.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "chinesetraditional"; MessagesFile: "installer\ChineseTraditional.isl"

[Tasks]
Name: "desktopicon"; Description: "建立桌面捷徑"; Flags: unchecked

[Files]
Source: "dist\win-unpacked\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "啟動 {#AppName}"; Flags: nowait postinstall skipifsilent
