"""
Decoradores para manejo consistente de errores en vistas.
Proporciona manejo automático de excepciones y logging.
"""

import logging
import functools
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def handle_view_errors(view_func=None, template_500='500.html', json_response=False):
    """
    Decorador para manejar errores en vistas de forma consistente.
    
    Args:
        view_func: La función de vista a decorar
        template_500: Template para errores 500
        json_response: Si True, retorna JSON en lugar de HTML
    
    Returns:
        Función decorada con manejo de errores
        
    Ejemplo:
        @handle_view_errors(template_500='errors/500.html')
        def mi_vista(request):
            ...
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(request, *args, **kwargs):
            try:
                return f(request, *args, **kwargs)
            
            except ObjectDoesNotExist as e:
                logger.warning(
                    f"Objeto no encontrado en {f.__name__}: {str(e)}",
                    extra={'request': request}
                )
                if json_response:
                    return JsonResponse(
                        {'error': 'Recurso no encontrado'},
                        status=404
                    )
                return render(request, '404.html', status=404)
            
            except ValueError as e:
                logger.warning(
                    f"Validación fallida en {f.__name__}: {str(e)}",
                    extra={'request': request}
                )
                if json_response:
                    return JsonResponse(
                        {'error': f'Datos inválidos: {str(e)}'},
                        status=400
                    )
                return render(
                    request, 
                    '400.html',
                    {'error': str(e)},
                    status=400
                )
            
            except PermissionError as e:
                logger.warning(
                    f"Acceso denegado en {f.__name__}: {str(e)}",
                    extra={'request': request}
                )
                if json_response:
                    return JsonResponse(
                        {'error': 'Acceso denegado'},
                        status=403
                    )
                return render(request, '403.html', status=403)
            
            except Exception as e:
                # Errores no esperados
                logger.error(
                    f"Error no controlado en {f.__name__}: {str(e)}\n{traceback.format_exc()}",
                    extra={'request': request, 'exc_info': True}
                )
                if json_response:
                    return JsonResponse(
                        {'error': 'Error interno del servidor'},
                        status=500
                    )
                return render(request, template_500, status=500)
        
        return wrapper
    
    if view_func is None:
        return decorator
    return decorator(view_func)


def handle_db_errors(view_func=None):
    """
    Decorador específico para vistas que acceden intensivamente a BD.
    Maneja timeouts y conexión.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(request, *args, **kwargs):
            try:
                return f(request, *args, **kwargs)
            except Exception as e:
                # Base de datos desconectada
                if 'lost connection' in str(e).lower() or 'connection refused' in str(e).lower():
                    logger.critical(
                        f"BD desconectada en {f.__name__}",
                        exc_info=True
                    )
                    return render(
                        request, 
                        '503.html',
                        {'error': 'Base de datos no disponible'},
                        status=503
                    )
                
                # Error de timeout
                elif 'timeout' in str(e).lower():
                    logger.error(
                        f"Timeout en BD en {f.__name__}",
                        exc_info=True
                    )
                    return render(
                        request,
                        '504.html',
                        {'error': 'Tiempo de espera agotado'},
                        status=504
                    )
                
                # Otros errores
                else:
                    raise
        
        return wrapper
    
    if view_func is None:
        return decorator
    return decorator(view_func)


def log_performance(view_func=None, threshold_ms=500):
    """
    Decorador para loguear vistas que exceden cierto tiempo.
    
    Args:
        view_func: Función a decorar
        threshold_ms: Umbral de tiempo en milisegundos
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(request, *args, **kwargs):
            import time
            start = time.time()
            
            try:
                response = f(request, *args, **kwargs)
                return response
            finally:
                elapsed = (time.time() - start) * 1000
                if elapsed > threshold_ms:
                    logger.warning(
                        f"Vista lenta: {f.__name__} tardó {elapsed:.2f}ms",
                        extra={'request': request}
                    )
        
        return wrapper
    
    if view_func is None:
        return decorator
    return decorator(view_func)
