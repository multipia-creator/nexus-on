; NEXUS-ON Windows Engine Installer
; InnoSetup Script (https://jrsoftware.org/isinfo.php)
; Build: iscc setup.iss

#define MyAppName "NEXUS Engine"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "NEXUS-ON"
#define MyAppURL "https://nexus-3bm.pages.dev"
#define MyAppExeName "nexus-engine.exe"

[Setup]
AppId={{7F8A9B3C-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\NEXUS-Engine
DefaultGroupName=NEXUS-ON
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALLATION_GUIDE.md
OutputDir=.
OutputBaseFilename=NEXUS-Engine-Windows-x64-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "시스템 시작 시 자동 실행"; GroupDescription: "추가 옵션:"; Flags: unchecked

[Files]
; Python 백엔드 파일
Source: "engine\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "bootstrap.ps1"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 서비스 등록
Filename: "{cmd}"; Parameters: "/c sc create NEXUSEngine binPath= ""{app}\{#MyAppExeName}"" start= auto DisplayName= ""NEXUS Engine Service"""; Flags: runhidden
Filename: "{cmd}"; Parameters: "/c sc description NEXUSEngine ""NEXUS-ON AI 캐릭터 비서 백엔드 엔진"""; Flags: runhidden
; 방화벽 규칙 추가
Filename: "{cmd}"; Parameters: "/c netsh advfirewall firewall add rule name=""NEXUS Engine"" dir=in action=allow protocol=TCP localport=7100"; Flags: runhidden
; 서비스 시작
Filename: "{cmd}"; Parameters: "/c sc start NEXUSEngine"; Flags: runhidden nowait postinstall skipifsilent; Description: "NEXUS Engine 서비스 시작"

[UninstallRun]
; 서비스 중지 및 삭제
Filename: "{cmd}"; Parameters: "/c sc stop NEXUSEngine"; Flags: runhidden
Filename: "{cmd}"; Parameters: "/c sc delete NEXUSEngine"; Flags: runhidden
; 방화벽 규칙 삭제
Filename: "{cmd}"; Parameters: "/c netsh advfirewall firewall delete rule name=""NEXUS Engine"""; Flags: runhidden

[Code]
var
  DataDirPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  // 데이터 디렉토리 선택 페이지
  DataDirPage := CreateInputDirPage(wpSelectDir,
    '데이터 디렉토리 선택', '세리아가 사용할 데이터 폴더를 선택하세요.',
    '문서, 캐시, 로그 등이 저장됩니다.' + #13#10 + '최소 5GB 이상의 여유 공간이 필요합니다.',
    False, '');
  DataDirPage.Add('');
  DataDirPage.Values[0] := ExpandConstant('{userdocs}\NEXUS-Data');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = DataDirPage.ID then
  begin
    // 데이터 디렉토리 생성
    if not DirExists(DataDirPage.Values[0]) then
      CreateDir(DataDirPage.Values[0]);
    
    // .env 파일 생성
    SaveStringToFile(ExpandConstant('{app}\.env'), 
      'DATA_DIR=' + DataDirPage.Values[0] + #13#10 +
      'PORT=7100' + #13#10 +
      'LOG_LEVEL=INFO' + #13#10 +
      '# 아래에 API 키를 입력하세요' + #13#10 +
      'ANTHROPIC_API_KEY=' + #13#10 +
      'OPENAI_API_KEY=' + #13#10 +
      'GOOGLE_CLOUD_API_KEY=' + #13#10,
      False);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Health check
    MsgBox('NEXUS Engine이 설치되었습니다!' + #13#10 + #13#10 +
           '서비스가 http://localhost:7100 에서 실행됩니다.' + #13#10 +
           'API 키 설정은 ' + ExpandConstant('{app}\.env') + ' 파일을 수정하세요.',
           mbInformation, MB_OK);
  end;
end;
