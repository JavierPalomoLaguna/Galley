"""
Vistas del módulo de contacto. Incluye manejo robusto de errores y logging.
"""

import logging
from django.shortcuts import render
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django.conf import settings
from utils.decorators import handle_view_errors, log_performance
from utils.exceptions import EmailException, ValidationException
from .forms import FormularioContacto
from .models import MensajeContacto

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
@handle_view_errors(template_500='500.html')
@ratelimit(key='ip', rate='5/m', method=['POST'], block=True)
@log_performance(threshold_ms=1000)
def contacto(request):
    """
    Vista de contacto con validación, rate limiting y manejo de errores.
    
    Rate Limiting: 5 mensajes máximo por IP cada minuto
    
    Manejo de errores:
    - Validación de formulario: retorna formulario con errores
    - Error al guardar en BD: notifica al usuario, loga error
    - Error al enviar email: notifica al usuario pero guarda mensaje en BD
    - Rate limit: retorna página 429 (Too Many Requests)
    """
    mensaje_exito = None
    mensaje_error = None
    formulario = FormularioContacto()

    if request.method == "POST":
        try:
            formulario = FormularioContacto(request.POST)
            
            if not formulario.is_valid():
                # Errores de validación del formulario
                logger.warning(
                    f"Formulario contacto inválido desde {request.META.get('REMOTE_ADDR')}: "
                    f"{formulario.errors}",
                    extra={'request': request}
                )
                mensaje_error = "Por favor, revisa los datos del formulario."
            else:
                # Formulario válido, procesar
                nombre = formulario.cleaned_data.get("name", "").strip()
                email = formulario.cleaned_data.get("email", "").strip()
                contenido = formulario.cleaned_data.get("contenido", "").strip()
                
                # Validación adicional de seguridad
                if not all([nombre, email, contenido]):
                    raise ValidationException("Datos incompletos recibidos")
                
                # Guardar en base de datos
                try:
                    mensaje = MensajeContacto.objects.create(
                        nombre=nombre,
                        email=email,
                        contenido=contenido
                    )
                    logger.info(
                        f"Mensaje de contacto guardado: {mensaje.id} de {email}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error al guardar mensaje de contacto: {str(e)}",
                        exc_info=True,
                        extra={'request': request}
                    )
                    mensaje_error = "Error al guardar tu mensaje. Por favor, intenta más tarde."
                    raise
                
                # Enviar email al administrador
                try:
                    asunto = f"📧 Nuevo mensaje de contacto desde {nombre}"
                    
                    mensaje_texto = (
                        f"Nombre: {nombre}\n"
                        f"Email: {email}\n"
                        f"---\n"
                        f"{contenido}\n"
                        f"---\n"
                        f"Enviado desde: {request.META.get('REMOTE_ADDR', 'IP desconocida')}"
                    )
                    
                    # Enviar mail con manejo de excepciones
                    send_mail(
                        subject=asunto,
                        message=mensaje_texto,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=['jpalomolaguna@gmail.com'],
                        fail_silently=False,
                    )
                    
                    logger.info(f"Email de contacto enviado: {email}")
                    mensaje_exito = "✅ Mensaje enviado correctamente. Te responderemos pronto."
                
                except Exception as e:
                    # Email falló, pero el mensaje está guardado en BD
                    logger.error(
                        f"Error al enviar email de contacto de {email}: {str(e)}",
                        exc_info=True,
                        extra={'request': request}
                    )
                    # No mostramos error al usuario para no exponerlo detalles de email
                    # Pero dejamos saber que el mensaje se guardó
                    mensaje_exito = "Mensaje recibido. Nos pondremos en contacto pronto."
        
        except ValidationException as e:
            logger.warning(f"Error de validación: {str(e)}")
            mensaje_error = "Los datos proporcionados no son válidos."
        
        except Exception as e:
            logger.error(
                f"Error inesperado en formulario contacto: {str(e)}",
                exc_info=True,
                extra={'request': request}
            )
            mensaje_error = "Ocurrió un error procesando tu mensaje. Intenta más tarde."
        
        finally:
            # Limpiar formulario después de envío exitoso
            if mensaje_exito:
                formulario = FormularioContacto()
    
    # Contexto para la plantilla
    context = {
        "formulario": formulario,
        "mensaje_exito": mensaje_exito,
        "mensaje_error": mensaje_error,
        'meta_title': 'Contacta con Nuestros Desarrolladores Web | Código Vivo Studio',
        'meta_description': 'Solicita presupuesto para tu proyecto web. Desarrollo personalizado para restaurantes, comercios y empresas.',
    }
    
    return render(request, "contacto/contacto.html", context)