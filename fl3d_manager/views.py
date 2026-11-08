"""
=============================================================================
FL3D Manager - Views Globais do Projeto (fl3d_manager/views.py)
=============================================================================
Views que pertencem ao projeto como um todo, não a um app específico.
=============================================================================
"""

from django.contrib.auth.views import LoginView


class FL3DLoginView(LoginView):
    """
    View de login customizada.
    Sempre redireciona para '/?from_login=1' após o login bem-sucedido,
    ignorando o parâmetro ?next= da URL.
    Isso garante que o crachá de sessão por aba (sessionStorage) seja
    registrado corretamente, evitando loop de login duplo.
    """
    template_name = 'registration/login.html'

    def get_success_url(self):
        return '/?from_login=1'

