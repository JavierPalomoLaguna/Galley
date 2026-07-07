"""
Excepciones personalizadas para Galley Pub.
Proporcionan manejo consistente de errores en toda la aplicación.
"""


class GalleyBaseException(Exception):
    """Excepción base para todas las excepciones de Galley."""
    
    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code or 'GALLEY_ERROR'
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(GalleyBaseException):
    """Error al acceder a la base de datos."""
    
    def __init__(self, message, code='DB_ERROR', details=None):
        super().__init__(message, code, details)


class CacheException(GalleyBaseException):
    """Error al acceder a caché."""
    
    def __init__(self, message, code='CACHE_ERROR', details=None):
        super().__init__(message, code, details)


class ExternalServiceException(GalleyBaseException):
    """Error al conectar con servicio externo (email, APIs, etc)."""
    
    def __init__(self, message, code='EXTERNAL_SERVICE_ERROR', details=None):
        super().__init__(message, code, details)


class EmailException(ExternalServiceException):
    """Error al enviar correo."""
    
    def __init__(self, message, code='EMAIL_ERROR', details=None):
        super().__init__(message, code, details)


class ValidationException(GalleyBaseException):
    """Error de validación de datos."""
    
    def __init__(self, message, code='VALIDATION_ERROR', details=None):
        super().__init__(message, code, details)


class RateLimitException(GalleyBaseException):
    """Error: límite de peticiones alcanzado."""
    
    def __init__(self, message='Too many requests', code='RATE_LIMIT_ERROR', details=None):
        super().__init__(message, code, details)


class TemplateException(GalleyBaseException):
    """Error al renderizar template."""
    
    def __init__(self, message, code='TEMPLATE_ERROR', details=None):
        super().__init__(message, code, details)
