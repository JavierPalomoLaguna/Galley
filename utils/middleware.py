"""
Middleware global para manejo centralizado de errores.
Captura y loguea excepciones no manejadas a nivel de aplicación.
"""

import logging
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import DatabaseError
from django.utils.decorators import decorator_from_middleware_with_args

logger = logging.getLogger(__name__)


class GlobalErrorHandlingMiddleware:
    """
    Middleware para capturar y manejar errores globales.
    Proporciona logging centralizado y respuestas amigables.
    Renderiza páginas de error personalizadas incluso con DEBUG=True.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            
            # Interceptar respuestas de error y renderizar páginas personalizadas
            if response.status_code == 404:
                logger.warning(
                    f"404 Not Found: {request.method} {request.path}",
                    extra={'request': request}
                )
                return render(request, '404.html', status=404)
            
            elif response.status_code == 400:
                logger.warning(
                    f"400 Bad Request: {request.method} {request.path}",
                    extra={'request': request}
                )
                return render(request, '400.html', status=400)
            
            elif response.status_code == 403:
                logger.warning(
                    f"403 Forbidden: {request.method} {request.path}",
                    extra={'request': request}
                )
                return render(request, '403.html', status=403)
            
            elif response.status_code == 500:
                logger.critical(
                    f"500 Server Error: {request.method} {request.path}",
                    extra={'request': request}
                )
                return render(request, '500.html', status=500)
            
            elif response.status_code == 503:
                logger.critical(
                    f"503 Service Unavailable: {request.method} {request.path}",
                    extra={'request': request}
                )
                return render(request, '503.html', status=503)
            
            # Loguear otras respuestas de error
            elif response.status_code >= 400:
                logger.warning(
                    f"Respuesta {response.status_code}: {request.method} {request.path}",
                    extra={'request': request}
                )
            
            return response
        
        except ObjectDoesNotExist as e:
            logger.warning(
                f"Recurso no encontrado en {request.path}: {str(e)}",
                extra={'request': request}
            )
            return render(request, '404.html', status=404)
        
        except PermissionDenied as e:
            logger.warning(
                f"Acceso denegado en {request.path}: {str(e)}",
                extra={'request': request}
            )
            return render(request, '403.html', status=403)
        
        except DatabaseError as e:
            logger.critical(
                f"Error de BD en {request.path}: {str(e)}",
                exc_info=True,
                extra={'request': request}
            )
            return render(
                request,
                '503.html',
                {'error': 'Servicio temporalmente no disponible'},
                status=503
            )
        
        except Exception as e:
            logger.error(
                f"Error no capturado en {request.path}: {str(e)}",
                exc_info=True,
                extra={'request': request}
            )
            return render(request, '500.html', status=500)
    
    def process_exception(self, request, exception):
        """
        Procesa excepciones en las vistas.
        """
        logger.error(
            f"Excepción no capturada: {str(exception)}",
            exc_info=True,
            extra={'request': request}
        )
        return render(request, '500.html', status=500)


class RequestLoggingMiddleware:
    """
    Middleware para loguear todas las peticiones.
    Útil para debugging y auditoría.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Loguear petición entrante
        logger.debug(
            f"Petición: {request.method} {request.path}",
            extra={
                'request': request,
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
        
        response = self.get_response(request)
        
        # Loguear respuesta
        logger.debug(
            f"Respuesta: {response.status_code} - {request.method} {request.path}",
            extra={'request': request}
        )
        
        return response
