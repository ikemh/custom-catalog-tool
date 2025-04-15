!define ADMIN_EXE "GeradorCatalogo_Admin.exe"
!define USER_EXE "EstruturaArquivos.exe"

Outfile "Instalador_Final.exe"  ; Nome do instalador final
RequestExecutionLevel user      ; Executa SEM privilégios elevados

Section "Instalação Completa"
    ; Define a pasta temporária como local de extração
    SetOutPath $TEMP

    ; Inclui os arquivos no instalador e os extrai para a pasta temporária
    File /oname=$TEMP\${ADMIN_EXE} "C:\Users\ikemh\Desktop\GeradorCatalogo_Admin.exe"
    File /oname=$TEMP\${USER_EXE} "C:\Users\ikemh\Desktop\EstruturaArquivos.exe"

    ; Executa o primeiro instalador como Administrador (forçando elevação de privilégios)
    ExecShell "runas" "$TEMP\${ADMIN_EXE}"

    ; Executa o segundo instalador normalmente (como usuário comum)
    ExecWait '"$TEMP\${USER_EXE}"'

    ; Limpa os arquivos temporários
    Delete "$TEMP\${ADMIN_EXE}"
    Delete "$TEMP\${USER_EXE}"
SectionEnd
