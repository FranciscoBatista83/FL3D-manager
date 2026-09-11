@echo off
rem =============================================================================
rem FL3D Manager - Script de Inicialização Rápida para Windows (iniciar_sistema.bat)
rem =============================================================================
rem VISÃO GERAL E CONCEITO:
rem Este é um arquivo de lote (batch script) que automatiza tudo com apenas 2 cliques!
rem Em vez de você ter que abrir o terminal preto, digitar comandos difíceis como
rem ativar ambiente e rodar servidor, este arquivo faz tudo sozinho:
rem   1. Dá um título bonito à janela do terminal.
rem   2. Ativa o ambiente virtual (onde estão o Python e Django instalados).
rem   3. Dispara a abertura do navegador (Google Chrome, Edge, etc.) no endereço certo.
rem   4. Inicia o servidor web na porta 8000 escutando em toda a rede local (0.0.0.0).
rem   5. Permite que você acesse o sistema pelo computador e pelo celular na mesma rede Wi-Fi!
rem =============================================================================

title FL3D Manager - Servidor Local
echo =========================================
echo      Iniciando FL3D Manager...
echo =========================================
echo.

rem Passo 1: Ativa o ambiente virtual 'venv'.
rem Isso garante que o Python use as bibliotecas instaladas para este projeto específico.
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
rem Passo 2: Abre o navegador após 3 segundos de espera (para dar tempo do servidor ligar).
echo Agendando abertura do navegador...
start cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8000"

rem Passo 3: Inicia o servidor Django na porta 8000.
rem Usar "0.0.0.0:8000" faz o sistema aceitar conexões não só do próprio computador,
rem mas também de outros aparelhos (celulares, tablets) conectados na mesma rede Wi-Fi.
echo Iniciando o servidor para a rede local (porta 8000)...
echo.
echo ==============================================================
echo Para acessar pelo CELULAR ou OUTRO COMPUTADOR no mesmo Wi-Fi:
echo Acesse: http://192.168.15.3:8000
echo ==============================================================
echo.
echo Para fechar o sistema, feche esta janela ou aperte CTRL+C.
echo.

python manage.py runserver 0.0.0.0:8000
pause

