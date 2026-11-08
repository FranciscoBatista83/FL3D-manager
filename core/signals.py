"""
=============================================================================
FL3D Manager - Sinais do Módulo Core (signals.py)
=============================================================================
Garante que todo usuário criado no Django receba automaticamente
um PerfilUsuario associado, mantendo a consistência dos dados.
=============================================================================
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario, Empresa


@receiver(post_save, sender=User)
def criar_ou_atualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Cria automaticamente o PerfilUsuario se ainda não existir.
    """
    if created:
        empresa_padrao = Empresa.objects.filter(ativo=True).order_by('id').first()
        nivel = PerfilUsuario.NivelAcesso.MASTER if instance.is_superuser else PerfilUsuario.NivelAcesso.OPERADOR
        PerfilUsuario.objects.get_or_create(
            usuario=instance,
            defaults={
                'empresa': empresa_padrao,
                'nivel': nivel
            }
        )

