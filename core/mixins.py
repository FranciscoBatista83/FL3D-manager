"""
=============================================================================
FL3D Manager - Mixins Multi-Empresa (mixins.py)
=============================================================================
Fornece mixins para filtrar QuerySets automaticamente pela empresa do usuário
e associar a empresa ao salvar novos registros.
=============================================================================
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class EmpresaScopedMixin(LoginRequiredMixin):
    """
    Mixin para CBVs (ListView, DetailView, UpdateView, DeleteView):
    - Se for Super Administrador (Master) e não tiver empresa fixa, vê tudo.
    - Se pertencer a uma Empresa, filtra estritamente por aquela empresa.
    - Ao salvar (CreateView/UpdateView), injeta form.instance.empresa automaticamente.
    """
    empresa_field = 'empresa'

    def get_queryset(self):
        qs = super().get_queryset()
        empresa = getattr(self.request, 'empresa', None)
        perfil = getattr(self.request, 'perfil', None)

        if perfil and perfil.is_master and not empresa:
            return qs

        if empresa:
            filter_kwargs = {self.empresa_field: empresa}
            return qs.filter(**filter_kwargs)

        return qs.none()

    def form_valid(self, form):
        empresa = getattr(self.request, 'empresa', None)
        if hasattr(form.instance, self.empresa_field):
            if not getattr(form.instance, self.empresa_field, None) and empresa:
                setattr(form.instance, self.empresa_field, empresa)
        return super().form_valid(form)


class GestorRequiredMixin(LoginRequiredMixin):
    """
    Garante que apenas Gestores da Empresa ou Super Administradores
    possam acessar determinadas views (ex: cadastro de usuários da empresa).
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        perfil = getattr(request, 'perfil', None)
        if not perfil or not perfil.is_gestor:
            raise PermissionDenied("Apenas administradores da empresa têm permissão para acessar esta página.")
        return super().dispatch(request, *args, **kwargs)


class MasterRequiredMixin(LoginRequiredMixin):
    """
    Garante que apenas o Super Administrador da plataforma (você)
    possa acessar (ex: gerenciamento global de empresas clientes).
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        perfil = getattr(request, 'perfil', None)
        if not perfil or not perfil.is_master:
            raise PermissionDenied("Acesso restrito ao Administrador Geral da Plataforma.")
        return super().dispatch(request, *args, **kwargs)

