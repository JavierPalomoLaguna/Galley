"""
Vistas principales de ProyectoWebApp (Galley Pub).
Incluye manejo robusto de errores y logging.
"""

import logging
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from utils.decorators import handle_view_errors, handle_db_errors, log_performance
from servicios.models import Coctel, Categoria

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@handle_view_errors(template_500='500.html')
@handle_db_errors
@log_performance
def home(request):
    """
    Página principal: renderiza hero, galería de cócteles y testimonios.
    
    Manejo de errores:
    - Si no hay categorías en BD, retorna contexto vacío
    - Si falla BD, retorna página de error 503
    - Si falla renderizado, retorna página de error 500
    """
    try:
        # Obtener categorías con sus cócteles asociados
        categorias = Categoria.objects.prefetch_related('cocteles').all()
        categorias_ordenadas = []
        
        for cat in categorias:
            try:
                destacados = list(cat.cocteles.filter(destacado_en_index=True))
                if destacados:
                    from django.utils.text import slugify
                    categorias_ordenadas.append({
                        'nombre': cat.nombre,
                        'slug': slugify(cat.nombre),
                        'cocteles': destacados,
                    })
            except Exception as e:
                logger.warning(
                    f"Error al procesar categoría {cat.id}: {str(e)}",
                    exc_info=True
                )
                # Continuar sin esta categoría
                continue
        
        logger.info(f"Home: {len(categorias_ordenadas)} categorías cargadas")
        
        return render(request, 'ProyectoWebApp/index.html', {
            'categorias_ordenadas': categorias_ordenadas,
        })
    
    except ObjectDoesNotExist as e:
        logger.warning(f"Objeto no encontrado en home: {str(e)}")
        # Retornar página home con contexto vacío
        return render(request, 'ProyectoWebApp/index.html', {
            'categorias_ordenadas': [],
        })
    
    except Exception as e:
        logger.error(
            f"Error crítico en home: {str(e)}",
            exc_info=True
        )
        # El decorador @handle_view_errors lo manejará
        raise


@require_http_methods(["GET"])
@handle_view_errors(template_500='500.html')
@log_performance
def legal_page(request, page_type):
    """
    Vista genérica para páginas legales (cookies, privacidad, aviso legal).
    
    Args:
        request: Objeto de solicitud HTTP
        page_type: Tipo de página ('cookies', 'privacidad', 'legal')
    
    Manejo de errores:
    - Si page_type inválido, retorna 404
    - Si falla renderizado de template, retorna 500
    """
    pages_config = {
        'cookies': {
            'template': 'ProyectoWebApp/politica_cookies.html',
            'title': 'Política de Cookies',
            'meta_description': 'Política de cookies de Galley Pub.',
        },
        'privacidad': {
            'template': 'ProyectoWebApp/politica_privacidad.html',
            'title': 'Política de Privacidad',
            'meta_description': 'Política de privacidad de Galley Pub.',
        },
        'legal': {
            'template': 'ProyectoWebApp/aviso_legal.html',
            'title': 'Aviso Legal',
            'meta_description': 'Aviso legal de Galley Pub.',
        },
    }
    
    try:
        config = pages_config.get(page_type)
        if not config:
            logger.warning(f"Página legal inválida solicitada: {page_type}")
            return render(request, '404.html', status=404)
        
        logger.info(f"Página legal accedida: {page_type}")
        
        return render(request, config['template'], {
            'title': config['title'],
            'meta_description': config['meta_description'],
        })
    
    except Exception as e:
        logger.error(
            f"Error al renderizar página legal {page_type}: {str(e)}",
            exc_info=True
        )
        raise


# ============================================================================
# Funciones de compatibilidad (aliases)
# ============================================================================

def politica_cookies(request):
    """Redirige a legal_page. Mantiene compatibilidad con URLs antiguas."""
    return legal_page(request, 'cookies')


def politica_privacidad(request):
    """Redirige a legal_page. Mantiene compatibilidad con URLs antiguas."""
    return legal_page(request, 'privacidad')


def aviso_legal(request):
    """Redirige a legal_page. Mantiene compatibilidad con URLs antiguas."""
    return legal_page(request, 'legal')


# ============================================================================
# Handlers personalizados para errores HTTP
# ============================================================================

def handler_404(request, exception=None):
    """
    View personalizada para manejar errores 404 (página no encontrada).
    Se activa cuando Django no encuentra una URL que coincida con los patrones.
    
    Renderiza: 404.html con contexto personalizado
    """
    logger.warning(
        f"404 Not Found: {request.method} {request.path}",
        extra={'request': request}
    )
    return render(request, '404.html', status=404)


def handler_500(request):
    """
    View personalizada para manejar errores 500 (error del servidor).
    Se activa cuando ocurre una excepción no capturada en una view.
    
    Renderiza: 500.html con contexto personalizado
    """
    logger.critical(
        f"500 Server Error: {request.method} {request.path}",
        exc_info=True,
        extra={'request': request}
    )
    return render(request, '500.html', status=500)