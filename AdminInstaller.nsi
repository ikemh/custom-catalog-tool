RequestExecutionLevel admin
Outfile "GeradorCatalogo_Admin.exe"  ; Nome do instalador admin
Name "Gerador de Catalogo (Admin)"
InstallDir "$PROGRAMFILES\GeradorCatalogo"

; Páginas do instalador
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Instalar Gerador Catalogo - Admin"
    ; Define o diretório de instalação
    SetOutPath "$INSTDIR"
    
    ; Copia recursivamente o conteúdo da pasta dist\main (incluindo _internal e demais pastas)
    File /r "C:\Users\ikemh\Desktop\projeto_catalogo\main.dist\*.*"
    
    ; Cria diretório e atalhos no Menu Iniciar e na Área de Trabalho para todos os usuários
    CreateDirectory "$SMPROGRAMS\Gerador de Catalogo"
    CreateShortcut "$SMPROGRAMS\Gerador de Catalogo\Gerador de Catalogo.lnk" "$INSTDIR\main.exe"

    ; Criar atalho no Desktop de TODOS os usuários (Pasta pública)
    CreateShortcut "C:\Users\Public\Desktop\Gerador de Catalogo.lnk" "$INSTDIR\main.exe"
    
    ; Registra o desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    ; Remove atalhos do Menu Iniciar e da Área de Trabalho global
    Delete "$SMPROGRAMS\Gerador de Catalogo\Gerador de Catalogo.lnk"
    RMDir "$SMPROGRAMS\Gerador de Catalogo"
    
    Delete "C:\Users\Public\Desktop\Gerador de Catalogo.lnk"  ; Remove atalho do Desktop público
    
    ; Remove todos os arquivos e a pasta de instalação
    RMDir /r "$INSTDIR"
    Delete "$INSTDIR\uninstall.exe"
SectionEnd
