"""
=============================================================================
FL3D Manager - Context Processors (context_processors.py)
=============================================================================
Disponibiliza variáveis multi-empresa e perfil diretamente em todos os templates HTML.
=============================================================================
"""

def empresa_context(request):
    """
    Injeta informações da empresa ativa e perfil nos templates.
    """
    empresa = getattr(request, 'empresa', None)
    perfil = getattr(request, 'perfil', None)
    return {
        'empresa_atual': empresa,
        'perfil_usuario': perfil,
        'is_master': perfil.is_master if perfil else False,
        'is_gestor': perfil.is_gestor if perfil else False,
    }

