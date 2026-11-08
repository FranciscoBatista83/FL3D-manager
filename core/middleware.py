"""
=============================================================================
FL3D Manager - Middleware Multi-Tenant (middleware.py)
=============================================================================
Garante que em qualquer requisição HTTP, a empresa e o perfil do usuário logado
fiquem facilmente acessíveis em `request.empresa` e `request.perfil`.
Além disso, verifica se a empresa do usuário está ativa.
=============================================================================
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import PerfilUsuario, Empresa


class MultiEmpresaMiddleware:
    """
    Injeta request.empresa e request.perfil na requisição corrente.
    Bloqueia o acesso caso a empresa do usuário esteja desativada pelo Master.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.empresa = None
        request.perfil = None

        if request.user.is_authenticated:
            # Tenta obter o perfil do usuário
            perfil = getattr(request.user, 'perfil', None)
            if not perfil:
                # Caso o usuário ainda não tenha perfil criado por sinal antigo
                empresa_padrao = Empresa.objects.filter(ativo=True).first()
                nivel = PerfilUsuario.NivelAcesso.MASTER if request.user.is_superuser else PerfilUsuario.NivelAcesso.OPERADOR
                perfil, _ = PerfilUsuario.objects.get_or_create(
                    usuario=request.user,
                    defaults={'empresa': empresa_padrao, 'nivel': nivel}
                )

            request.perfil = perfil
            request.empresa = perfil.empresa

            # Se a empresa estiver inativa e o usuário não for Super Admin Master
            if perfil.empresa and not perfil.empresa.ativo and not perfil.is_master:
                # Desloga e impede o acesso
                logout(request)
                messages.error(request, 'O acesso da sua empresa está suspenso. Entre em contato com o administrador da plataforma.')
                return redirect('login')

        response = self.get_response(request)
        return response

