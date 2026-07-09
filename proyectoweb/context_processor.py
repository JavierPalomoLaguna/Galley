from django.conf import settings

def admin_prefix(request):
    """
    Context processor que proporciona el prefijo correcto del admin
    según el entorno (local o producción)
    """
    if settings.DEBUG:
        # En desarrollo, no hay prefijo
        prefix = ''
    else:
        # En producción, usa FORCE_SCRIPT_NAME
        prefix = getattr(settings, 'FORCE_SCRIPT_NAME', '')
    
    return {
        'admin_prefix': prefix,
    }
