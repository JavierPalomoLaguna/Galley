"""
Vistas del módulo de contacto.
"""

from django.shortcuts import render
from django.core.mail import send_mail
from .forms import FormularioContacto
from .models import MensajeContacto
from django.conf import settings


def contacto(request):
    mensaje_exito = None
    mensaje_error = None

    if request.method == "POST":
        formulario = FormularioContacto(request.POST)
        if formulario.is_valid():
            nombre = formulario.cleaned_data["name"]
            email = formulario.cleaned_data["email"]
            contenido = formulario.cleaned_data["contenido"]

            # Guardar en la base de datos
            MensajeContacto.objects.create(
                nombre=nombre,
                email=email,
                contenido=contenido
            )

            # Enviar correo
            try:
                send_mail(
                    subject="Nuevo mensaje de contacto desde Galley Pub",
                    message=f"Nombre: {nombre}\nEmail: {email}\n---\n{contenido}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['contacto@codigovivostudio.cloud'],
                    fail_silently=False,
                )
                mensaje_exito = "✅ Mensaje enviado correctamente. Te responderemos pronto."
            except Exception as e:
                mensaje_exito = f"Mensaje guardado, pero email falló: {str(e)}"
            
            formulario = FormularioContacto()
        else:
            mensaje_error = "Por favor, revisa los datos del formulario."
    else:
        formulario = FormularioContacto()

    context = {
        "formulario": formulario,
        "mensaje_exito": mensaje_exito,
        "mensaje_error": mensaje_error,
        'meta_title': 'Contacta con Nuestros Desarrolladores Web | Código Vivo Studio',
        'meta_description': 'Solicita presupuesto para tu proyecto web. Desarrollo personalizado para restaurantes, comercios y empresas.',
    }
    
    return render(request, "contacto/contacto.html", context)
    
    return render(request, "contacto/contacto.html", context)