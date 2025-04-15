Unicode True
RequestExecutionLevel user
Outfile "GeradorCatalogo_User.exe"  ; Nome do instalador User
Name "Gerador de Catalogo (User)"
InstallDir "$PROFILE\Documents\GeradorCatalogo"  ; Força o uso de "C:\Users\ikemh\Documents\GeradorCatalogo"

; Páginas do instalador
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Instalar Gerador Catalogo - User"
    ; Instala os arquivos adicionais no diretório do usuário usando caminho absoluto para os arquivos
    SetOutPath "$PROFILE\Documents\GeradorCatalogo"
    File "C:\Users\ikemh\Desktop\projeto_catalogo\catalog_groups.py"
    
    SetOutPath "$PROFILE\Documents\GeradorCatalogo\data"
    File "C:\Users\ikemh\Desktop\projeto_catalogo\Planilha_Catalogo_2025.ods"
    
    ; Cria os diretórios de imagens se ainda não existirem
    CreateDirectory "$PROFILE\Documents\GeradorCatalogo\images"
    CreateDirectory "$PROFILE\Documents\GeradorCatalogo\images\catalogo_principal"
    CreateDirectory "$PROFILE\Documents\GeradorCatalogo\images\catalogo_secundario"
    
    ; Cria o diretório de saída "Catálogos" na Área de Trabalho e atalhos para "images" e "data"
    CreateDirectory "$DESKTOP\Catálogos"
    CreateShortcut "$DESKTOP\Catálogos\Imagens.lnk" "$PROFILE\Documents\GeradorCatalogo\images" "" "$PROFILE\Documents\GeradorCatalogo\images" 0
    CreateShortcut "$DESKTOP\Catálogos\Data.lnk" "$PROFILE\Documents\GeradorCatalogo\data" "" "$PROFILE\Documents\GeradorCatalogo\data" 0
    
    ; Registra o desinstalador (neste caso, instalado dentro do diretório do usuário)
    WriteUninstaller "$PROFILE\Documents\GeradorCatalogo\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$PROFILE\Documents\GeradorCatalogo\catalog_groups.py"
    Delete "$PROFILE\Documents\GeradorCatalogo\data\Planilha_Catalogo_2025.ods"
    RMDir /r "$PROFILE\Documents\GeradorCatalogo\images\catalogo_principal"
    RMDir /r "$PROFILE\Documents\GeradorCatalogo\images\catalogo_secundario"
    RMDir "$PROFILE\Documents\GeradorCatalogo\images"
    RMDir /r "$PROFILE\Documents\GeradorCatalogo"
    Delete "$DESKTOP\Catálogos\Imagens.lnk"
    Delete "$DESKTOP\Catálogos\Data.lnk"
    RMDir "$DESKTOP\Catálogos"
SectionEnd