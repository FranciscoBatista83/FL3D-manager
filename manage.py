#!/usr/bin/env python
"""
=============================================================================
FL3D Manager - Utilitário de Linha de Comando Principal (manage.py)
=============================================================================
Este arquivo é o "painel de controle" do Django via terminal para o FL3D Manager.

VISÃO GERAL E CONCEITO:
Pense no Django como um carro cheio de recursos. O arquivo `manage.py` é a chave
de ignição e o volante com comandos especiais. Através dele, você digita ordens
no terminal do seu computador para:
  1. Iniciar o servidor web para ver o sistema no navegador (`runserver`).
  2. Criar ou atualizar as tabelas do banco de dados (`makemigrations` e `migrate`).
  3. Criar uma conta de administrador inicial (`createsuperuser`).
  4. Executar testes automatizados (`test`).

COMO FUNCIONA O CÓDIGO ABAIXO:
- Ele avisa ao Python onde estão as configurações do sistema (`fl3d_manager.settings`).
- Tenta carregar o Django e, se não estiver instalado no ambiente virtual,
  exibe um aviso amigável explicando o que aconteceu.
- Repassa os comandos que você digitou no terminal diretamente para o motor do Django.
=============================================================================
"""
import os
import sys


def main():
    """
    Função principal que prepara o ambiente e executa o comando solicitado.
    """
    # 1. Define qual arquivo guarda as configurações do projeto:
    # Aponta para 'fl3d_manager/settings.py'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fl3d_manager.settings')
    
    try:
        # 2. Tenta importar a função do Django que processa ordens de terminal
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Se falhar, é porque o Django não está instalado ou o ambiente virtual (venv)
        # não foi ativado antes de rodar o comando.
        raise ImportError(
            "Não foi possível importar o Django. Você tem certeza de que ele está instalado "
            "e disponível na variável de ambiente PYTHONPATH? Você lembrou de ativar "
            "o ambiente virtual (venv) antes de executar este comando?"
        ) from exc
    
    # 3. Executa o comando que o usuário digitou no terminal (ex: runserver, migrate)
    execute_from_command_line(sys.argv)


# Padrão Python: só executa a função main() se o arquivo for chamado diretamente no terminal
if __name__ == '__main__':
    main()

