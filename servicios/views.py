"""
Vistas del módulo de servicios (carta de cócteles). 
Incluye manejo robusto de errores y logging.
"""

import logging
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from utils.decorators import handle_view_errors, handle_db_errors, log_performance
from servicios.models import Coctel, Categoria

logger = logging.getLogger(__name__)


def _agrupar_por_categoria():
    """
    Agrupa cócteles por categoría.
    
    Returns:
        list: Lista de diccionarios con estructura {'nombre', 'slug', 'cocteles'}
    
    Manejo de errores:
    - Si BD falla, retorna lista vacía
    - Si hay problemas con un coctel, continúa sin él
    """
    try:
        resultado = []
        categorias = Categoria.objects.prefetch_related('cocteles').all()
        
        for cat in categorias:
            try:
                cocteles = list(cat.cocteles.all())
                if cocteles:
                    resultado.append({
                        'nombre': cat.nombre,
                        'slug': cat.slug,
                        'cocteles': cocteles,
                    })
            except Exception as e:
                logger.warning(
                    f"Error al procesar categoría {cat.id}: {str(e)}",
                    exc_info=True
                )
                # Continuar sin esta categoría
                continue
        
        logger.info(f"Agrupadas {len(resultado)} categorías")
        return resultado
    
    except Exception as e:
        logger.error(
            f"Error crítico al agrupar cócteles: {str(e)}",
            exc_info=True
        )
        return []


def _agrupar_destacados():
    """
    Agrupa cócteles destacados por categoría.
    
    Returns:
        list: Lista de diccionarios con estructura {'nombre', 'slug', 'cocteles'}
        Solo incluye categorías que tienen cócteles destacados
    
    Manejo de errores:
    - Si BD falla, retorna lista vacía
    - Si hay problemas con un coctel, continúa sin él
    """
    try:
        resultado = []
        categorias = Categoria.objects.prefetch_related('cocteles').all()
        
        for cat in categorias:
            try:
                destacados = list(cat.cocteles.filter(destacado_en_index=True))
                if destacados:
                    resultado.append({
                        'nombre': cat.nombre,
                        'slug': cat.slug,
                        'cocteles': destacados,
                    })
            except Exception as e:
                logger.warning(
                    f"Error al procesar destacados de categoría {cat.id}: {str(e)}",
                    exc_info=True
                )
                continue
        
        logger.info(f"Agrupados {len(resultado)} categorías con destacados")
        return resultado
    
    except Exception as e:
        logger.error(
            f"Error crítico al agrupar cócteles destacados: {str(e)}",
            exc_info=True
        )
        return []


@require_http_methods(["GET"])
@handle_view_errors(template_500='500.html')
@handle_db_errors
@log_performance
def carta_cocteles(request):
    """
    Página de carta completa de cócteles.
    
    Manejo de errores:
    - Si BD falla, retorna lista vacía
    - Si falla renderizado, retorna página de error 500
    """
    try:
        categorias_ordenadas = _agrupar_por_categoria()
        
        logger.info(f"Carta cócteles: {len(categorias_ordenadas)} categorías cargadas")
        
        context = {
            'categorias_ordenadas': categorias_ordenadas,
            'meta_title': 'Carta de Cócteles | Galley Pub',
            'meta_description': 'Descubre nuestra carta completa: clásicos, tropicales, sin alcohol y especiales.',
        }
        return render(request, 'servicios/carta_cocteles.html', context)
    
    except Exception as e:
        logger.error(
            f"Error en carta_cocteles: {str(e)}",
            exc_info=True
        )
        raise