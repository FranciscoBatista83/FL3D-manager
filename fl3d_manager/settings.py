"""
=============================================================================
FL3D Manager - Configurações Gerais do Sistema (settings.py)
=============================================================================
Este arquivo é o "coração das configurações" de todo o sistema FL3D Manager.

VISÃO GERAL E CONCEITO:
Imagine que o FL3D Manager é uma fábrica com várias máquinas e departamentos.
Este arquivo é o manual de regras e a central elétrica da fábrica. É aqui que
definimos:
  - Qual língua o sistema fala (Português do Brasil).
  - Em qual fuso horário os horários são gravados (Horário de Brasília).
  - Onde fica guardado o banco de dados (o grande caderno digital de registros).
  - Quais módulos (departamentos) da empresa estão ativos: Clientes, Estoque,
    Impressoras, Pedidos, Produção, Financeiro, Relatórios, etc.
  - Onde ficam guardadas as fotos e arquivos enviados pelos usuários.
=============================================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis definidas no arquivo .env para dentro do ambiente do sistema
load_dotenv()

# =============================================================================
# 1. DIRETÓRIOS BÁSICOS DO PROJETO
# =============================================================================
# BASE_DIR calcula automaticamente a pasta onde todo o projeto está instalado no seu computador.
# Assim, não importa se você instalou em "C:\dev\Projetos\FL3D Manager" ou em outro lugar,
# o sistema sabe encontrar seus arquivos sozinho.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# 2. SEGURANÇA E AMBIENTE DE DESENVOLVIMENTO
# =============================================================================
# A SECRET_KEY é lida do arquivo .env — nunca deve ficar exposta no código-fonte.
# Para gerar uma nova chave: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get('SECRET_KEY', 'chave-insegura-troque-no-env')

# DEBUG é lido do .env: 'True' em desenvolvimento, 'False' em produção.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS lê uma lista separada por vírgulas do .env.
# Exemplo no .env: ALLOWED_HOSTS=127.0.0.1,localhost,meusite.com
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split(',')


# =============================================================================
# 3. MÓDULOS ATIVOS (APLICATIVOS DO SISTEMA)
# =============================================================================
# Aqui listamos todos os blocos de construção do sistema.
# O Django vem com blocos prontos (como controle de login e área administrativa)
# e nós adicionamos os blocos exclusivos da FL3D Studio.
INSTALLED_APPS = [
    # Módulos padrão do Django:
    'django.contrib.admin',        # Painel administrativo pronto para gerenciar registros
    'django.contrib.auth',         # Sistema de autenticação (usuários, senhas, grupos)
    'django.contrib.contenttypes', # Permite vincular diferentes tipos de dados
    'django.contrib.sessions',     # Guarda informações de quem está logado no navegador
    'django.contrib.messages',     # Mensagens de alerta na tela (ex: "Salvo com sucesso!")
    'django.contrib.staticfiles',  # Gerenciador de arquivos visuais (CSS, JS, imagens)
    
    # Módulos customizados da FL3D Studio:
    'core',         # Utilitários gerais e recursos compartilhados por todos os módulos
    'dashboard',    # Painel inicial com gráficos e resumos rápidos do dia
    'clientes',     # Cadastro e histórico dos clientes da loja
    'produtos',     # Catálogo de produtos 3D vendidos ou impressos
    'pedidos',      # Gestão de orçamentos, vendas e pedidos de impressão
    'producao',     # Fila das impressoras, tempo real de máquina e controle de falhas/perdas
    'estoque',      # Controle de carretéis de filamento (PLA, PETG, ABS, peso e cores)
    'impressoras',  # Cadastro e monitoramento do parque de impressoras 3D
    'financeiro',   # Contas a pagar, contas a receber, caixa e faturamento
    'relatorios',   # Relatórios analíticos e indicadores de desempenho
    'usuarios',     # Gestão de usuários do sistema (criar, editar, ativar/desativar)
]


# =============================================================================
# 4. INTERMEDIÁRIOS DE REQUISIÇÃO (MIDDLEWARE)
# =============================================================================
# Os Middlewares são "seguranças e ajudantes" que ficam na porta de entrada do sistema.
# Toda vez que alguém clica em um link ou envia um formulário, eles verificam:
# se a pessoa está logada, se o envio é seguro (contra ataques hackers como CSRF), etc.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',               # Proteção contra envios falsos
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Descobre quem é o usuário logado
    'django.contrib.messages.middleware.MessageMiddleware',    # Permite exibir alertas na tela
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Impede páginas de serem roubadas em iframes
]

# Indica qual arquivo é o mapa principal de links e páginas do sistema
ROOT_URLCONF = 'fl3d_manager.urls'


# =============================================================================
# 5. TELAS VISUAIS (TEMPLATES HTML)
# =============================================================================
# O Django usa "templates" para montar as páginas HTML que o usuário vê.
# Aqui configuramos onde essas páginas ficam guardadas na pasta do projeto.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Pasta principal onde ficam todos os arquivos .html
        'APP_DIRS': True,                 # Também procura por pastas templates dentro de cada app
        'OPTIONS': {
            'context_processors': [
                # Variáveis automáticas disponíveis em todos os arquivos HTML
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',        # Permite saber se o usuário está logado
                'django.contrib.messages.context_processors.messages',# Exibe os balões de avisos
            ],
        },
    },
]

# Aplicação WSGI usada para conectar o Django a servidores de internet
WSGI_APPLICATION = 'fl3d_manager.wsgi.application'


# =============================================================================
# 6. BANCO DE DADOS (DATABASE)
# =============================================================================
# O banco de dados é a "gaveta de arquivos" onde tudo fica gravado de forma permanente.
# Usamos o SQLite: um banco leve, rápido e contido em um único arquivo ('db.sqlite3'),
# perfeito para rodar localmente sem precisar instalar servidores pesados.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =============================================================================
# 7. REGRAS DE SEGURANÇA PARA SENHAS
# =============================================================================
# Validadores que garantem que ninguém crie senhas fáceis demais ou previsíveis.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =============================================================================
# 8. IDIOMA E FUSO HORÁRIO (INTERNACIONALIZAÇÃO)
# =============================================================================
# Define o idioma do sistema para Português do Brasil (pt-BR)
LANGUAGE_CODE = 'pt-br'

# Fuso horário oficial do Brasil (Horário de Brasília) para que as impressões e
# vendas tenham a data e a hora corretas.
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_TZ = True


# =============================================================================
# 9. ARQUIVOS VISUAIS (ESTÁTICOS E MÍDIA)
# =============================================================================
# STATIC: São os arquivos de código visual do sistema que nunca mudam sozinhos
# (folhas de estilo CSS, scripts JavaScript, fontes e ícones).
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# MEDIA: São os arquivos que os usuários e operadores sobem para o sistema
# (fotos de produtos prontos, modelos 3D, comprovantes financeiros).
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# 10. REDIRECIONAMENTO DE LOGIN E LOGOUT
# =============================================================================
# Para onde o sistema manda o usuário quando precisa de autenticação:
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:index' # Ao fazer login com sucesso, vai direto para o Dashboard!
LOGOUT_REDIRECT_URL = 'login'          # Ao sair, volta para a tela de login


# =============================================================================
# 11. TIPO PADRÃO DE IDENTIFICADOR DE BANCO DE DADOS (PRIMARY KEY)
# =============================================================================
# Garante identificadores numéricos grandes (BigInteger) para que o sistema possa
# cadastrar milhões de registros sem esgotar a numeração de IDs.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

