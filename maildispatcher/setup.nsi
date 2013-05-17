;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Mail Dispatcher"
  OutFile "maildispatcher-0.2.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Mail Dispatcher"
 
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Mail Dispatcher" ""

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "gpl-3.0.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
 
  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Package" SecDummy

  SetOutPath "$INSTDIR"
 
   File /r "dist\*.*"
   
  ;Store installation folder
  WriteRegStr HKCU "Software\Mail Dispatcher" "" $INSTDIR
 
  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
 
 
  CreateShortCut "$INSTDIR\Mail Dispatcher.lnk" "$INSTDIR\maildispatcher.exe"
 
  SetOutPath "$SMPROGRAMS\Mail Dispatcher\"
  CopyFiles "$INSTDIR\Mail Dispatcher.lnk" "$SMPROGRAMS\Mail Dispatcher\"
  CopyFiles "$INSTDIR\Mail Dispatcher.lnk" "$DESKTOP\"
  Delete "$INSTDIR\Mail Dispatcher.lnk" 
  CreateShortCut "$SMPROGRAMS\Mail Dispatcher\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

SectionEnd

Section "GTK+" SecDummy2

  SetOutPath "$INSTDIR\"
  File "..\..\gtklib\bin\*.dll"

  SetOutPath "$INSTDIR\etc\fonts\"
  File "..\..\gtklib\etc\fonts\*.*"

  SetOutPath "$INSTDIR\etc\gtk-2.0\"
  File "..\..\gtklib\etc\gtk-2.0\*.*"

  SetOutPath "$INSTDIR\etc\pango\"
  File "..\..\gtklib\etc\pango\*.*"

  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\"
  File "..\..\gtklib\lib\gtk-2.0\2.10.0\loaders\*.*"

  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\engines\"
  File "..\..\gtklib\lib\gtk-2.0\2.10.0\engines\*.*"

  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\immodules\"
  File "..\..\gtklib\lib\gtk-2.0\2.10.0\immodules\*.*"

  SetOutPath "$INSTDIR\lib\pango\1.6.0\modules\"
  File "..\..\gtklib\lib\pango\1.6.0\modules\*.*"

  SetOutPath "$INSTDIR\share\themes\Default\gtk-2.0-key\"
  File "..\..\gtklib\share\themes\Default\gtk-2.0-key\*.*"

  SetOutPath "$INSTDIR\share\themes\MS-Windows\gtk-2.0\"
  File "..\..\gtklib\share\themes\MS-Windows\gtk-2.0\*.*"

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "Main Package"
  LangString DESC_SecDummy2 ${LANG_ENGLISH} "GTK+ Package. To be installed if you dont have pre installed GTK+"

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy2} $(DESC_SecDummy2)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall" 

  Delete "$INSTDIR\*.*"

  Delete "$DESKTOP\Mail Dispatcher.lnk"
  Delete "$SMPROGRAMS\Mail Dispatcher\Mail Dispatcher.lnk"
  Delete "$SMPROGRAMS\Mail Dispatcher\Uninstall.lnk"

  RMDir  "$SMPROGRAMS\Mail Dispatcher\"

  RMDir /r "$INSTDIR\etc\"   
  RMDir /r "$INSTDIR\lib\"
  RMDir /r "$INSTDIR\share\"

  RMDir "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\Mail Dispatcher"

SectionEnd 
