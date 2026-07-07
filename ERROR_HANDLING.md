# Guía de Manejo de Errores - Galley Pub

## 📋 Resumen Ejecutivo

Se implementó un **sistema empresarial de manejo de errores** que previene que la aplicación caiga ante excepciones inesperadas. El sistema incluye:

- ✅ Decoradores automáticos para vistas
- ✅ Middleware global de errores
- ✅ Logging centralizado con rotación
- ✅ Páginas de error personalizadas
- ✅ Excepciones tipadas y reutilizables
- ✅ Rate limiting con feedback amigable
- ✅ Manejo de errores de BD y email

---

## 🏗️ Arquitectura del Sistema

### 1. **Capa de Excepciones** (`utils/exceptions.py`)

Excepciones personalizadas que permiten clasificar y manejar errores de forma consistente:

```python
# Errores de BD
DatabaseException

# Errores de email
EmailException

# Errores de validación
ValidationException

# Errores de servicios externos
ExternalServiceException

# Límite de peticiones
RateLimitException
```

### 2. **Capa de Decoradores** (`utils/decorators.py`)

Decoradores que envuelven vistas y manejan automáticamente excepciones:

```python
@handle_view_errors(template_500='500.html')
@handle_db_errors
@log_performance(threshold_ms=500)
def mi_vista(request):
    ...
```

**Características:**
- Captura excepciones automáticamente
- Retorna páginas de error apropiadas
- Loguea eventos con contexto completo
- Rastrea performance de vistas

### 3. **Capa de Middleware** (`utils/middleware.py`)

Capas globales de aplicación que capturan errores no manejados:

- **GlobalErrorHandlingMiddleware**: Maneja excepciones globales
- **RequestLoggingMiddleware**: Loguea todas las peticiones

### 4. **Capa de Logging** (en `settings.py`)

Sistema de logging centralizado con:

- ✅ Archivos de log rotables (10MB max)
- ✅ Logs generales: `logs/galley.log`
- ✅ Logs de errores: `logs/galley_errors.log`
- ✅ Logs críticos: `logs/galley_critical.log`
- ✅ Formato JSON-compatible
- ✅ Niveles diferentes por app

### 5. **Plantillas de Error** (`proyectoweb/templates/`)

Páginas HTML personalizadas con temas de Galley:

```
404.html  →  Página no encontrada
400.html  →  Solicitud inválida
403.html  →  Acceso denegado
500.html  →  Error del servidor
503.html  →  Servicio no disponible
504.html  →  Timeout
```

---

## 🔧 Cómo Funciona en Cada Vista

### ProyectoWebApp/views.py (Home)

```python
@handle_view_errors(template_500='500.html')
@handle_db_errors
@log_performance
def home(request):
    try:
        categorias = Categoria.objects.prefetch_related('cocteles').all()
        # ... procesamiento seguro ...
        return render(request, 'ProyectoWebApp/index.html', context)
    except ObjectDoesNotExist:
        # → Retorna 404
        raise
```

**Casos manejados:**
- ✅ BD desconectada → 503
- ✅ Timeout en BD → 504
- ✅ Coctel no existe → Continúa sin él (log)
- ✅ Error de renderizado → 500
- ✅ Vista muy lenta → Log de warning

### contacto/views.py (Más crítica: email + BD)

```python
@handle_view_errors(template_500='500.html')
@ratelimit(key='ip', rate='5/m', method=['POST'], block=True)
def contacto(request):
    try:
        # Validar formulario
        if not formulario.is_valid():
            # → Devuelve formulario con errores
            
        # Guardar en BD
        try:
            MensajeContacto.objects.create(...)
        except Exception as e:
            logger.error("Error al guardar mensaje")
            # → Pero continúa sin fallar
            
        # Enviar email
        try:
            send_mail(...)
        except Exception as e:
            logger.error("Fallo email, pero mensaje guardado en BD")
            # → Usuario recibe feedback positivo
```

**Estrategia de resiliencia:**
- Si email falla: Mensaje guardado en BD, usuario recibe confirmación
- Si BD falla: Error amigable al usuario
- Si formulario inválido: Retorna formulario con errores
- Si rate limit: Django retorna 429 automáticamente

### blog/views.py y servicios/views.py

```python
@handle_db_errors
def blog(request):
    try:
        posts = Post.objects.prefetch_related('categorias').order_by('-created')
        for post in posts:
            try:
                # Procesar categorías
            except Exception as e:
                logger.warning(f"Error en post {post.id}: {e}")
                continue  # Continuar sin fallar
```

---

## 📊 Flujo de Manejo de Errores

```
Petición HTTP
    ↓
RequestLoggingMiddleware (loga entrada)
    ↓
GlobalErrorHandlingMiddleware (catch global)
    ↓
Vista con @handle_view_errors
    ↓
    ├─→ Éxito: Renderizar plantilla
    ├─→ ObjectDoesNotExist: 404.html
    ├─→ ValueError: 400.html
    ├─→ DatabaseError: 503.html
    ├─→ Exception no esperada: 500.html
    ↓
Middleware loga salida
    ↓
Respuesta HTTP
```

---

## 🔍 Cómo Revisar Logs

### Localización de logs:
```
Galley/
  logs/
    galley.log           # Todos los eventos
    galley_errors.log    # Solo errores
    galley_critical.log  # Solo críticos
```

### Ver en tiempo real (en desarrollo):
```bash
cd Galley
tail -f logs/galley_errors.log
```

### Ver en terminal Django:
```
Los logs se imprimirán en la consola en desarrollo (DEBUG=True)
```

### Estructura de un log:
```
[ERROR] 07/Jul/2026 14:32:15 contacto_views 1234 5678 - Error al enviar email de xxx@example.com: SMTPAuthenticationError('...')
```

---

## 🛡️ Patrones de Error Manejados

### 1. **Errores de Base de Datos**
```python
# ❌ Antes (aplicación cae)
categoria = Categoria.objects.get(id=cat_id)  # DoesNotExist → crash

# ✅ Después (manejo seguro)
categoria = get_object_or_404(Categoria, id=cat_id)  # → 404
# O
try:
    categoria = Categoria.objects.get(id=cat_id)
except ObjectDoesNotExist:
    logger.warning(f"Categoría {cat_id} no existe")
    return render(..., 404)
```

### 2. **Errores de Email**
```python
# ❌ Antes (falla, usuario no sabe qué pasó)
send_mail(...)  # SMTPException → crash

# ✅ Después (resiliente)
try:
    send_mail(...)
    logger.info("Email enviado")
except Exception as e:
    logger.error(f"Fallo email: {e}")
    # Mensaje ya guardado en BD, usuario feliz
    mensaje_exito = "Mensaje recibido, responderemos pronto"
```

### 3. **Errores de Validación**
```python
# ❌ Antes (error críptico)
contenido = request.POST['field']  # KeyError → 500

# ✅ Después (validación clara)
formulario = FormularioContacto(request.POST)
if not formulario.is_valid():
    return render(request, template, {'formulario': formulario})
    # Usuario ve errores específicos
```

### 4. **Errores de Timeout**
```python
# ✅ Automático
@handle_db_errors
def vista_lenta(request):
    # Si BD timeout → 504.html
    # Si BD demora mucho → log de warning
```

### 5. **Rate Limiting**
```python
@ratelimit(key='ip', rate='5/m', method=['POST'], block=True)
def contacto(request):
    # Más de 5 POST por minuto → Django retorna 429 automáticamente
```

---

## 📈 Mejoras Implementadas

| Problema | Antes | Después |
|----------|-------|---------|
| **Error BD** | Crash con 500 | Log + 503 friendly |
| **Email falla** | Crash con 500 | Mensaje guardado, usuario confirmado |
| **Coctel no existe** | Crash con 500 | Log + continúa sin él |
| **Validación** | Crash con 500 | Devuelve formulario con errores |
| **Timeout** | Crash sin respuesta | 504 con opción de reintentar |
| **Rate limit** | Crash con 500 | 429 automático de Django |
| **Vista lenta** | Sin visibilidad | Log de warning automático |
| **Logs** | Ninguno | Sistema completo con rotación |

---

## 🚀 Próximos Pasos (Opcional)

Para mejorar aún más la resiliencia:

1. **Caché de fallback**: Si BD falla, servir datos cacheados
2. **Alertas de email**: Enviar alertas a admin cuando hay errores críticos
3. **Métricas**: Integrar con Sentry o similar
4. **Circuit breaker**: Desactivar email temporalmente si falla
5. **Retry automático**: Reintentar operaciones con backoff

---

## ✅ Verificación Post-Implementación

Para verificar que todo funciona:

```bash
# 1. Comprueba que los decoradores se aplican
grep -r "@handle_view_errors" ProyectoWebApp/ blog/ contacto/ servicios/

# 2. Comprueba que el middleware está registrado
grep -r "GlobalErrorHandlingMiddleware" proyectoweb/settings.py

# 3. Comprueba que los templates de error existen
ls -la proyectoweb/templates/*.html | grep -E "40[34]|50[34]"

# 4. En desarrollo, intenta acceder a una URL inexistente
# Deberías ver: 404.html personalizado (no el por defecto)

# 5. Revisa los logs
ls -la logs/
```

---

## 📚 Referencias

- **Excepciones**: `utils/exceptions.py`
- **Decoradores**: `utils/decorators.py`
- **Middleware**: `utils/middleware.py`
- **Logging**: `proyectoweb/settings.py` (sección LOGGING)
- **Vistas refactorizadas**: 
  - `ProyectoWebApp/views.py`
  - `blog/views.py`
  - `contacto/views.py`
  - `servicios/views.py`

---

**Implementado por:** Senior Developer  
**Fecha:** Julio 2026  
**Objetivo:** Prevenir errores 500/502 y mejorar UX con feedback amigable
