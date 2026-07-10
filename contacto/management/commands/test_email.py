"""
Comando para probar la conexión SMTP y enviar email de prueba.
Uso: python manage.py test_email
"""
import smtplib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Prueba la conexión SMTP y envía un email de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipient',
            type=str,
            default='galleypub@galleypub.es',
            help='Email destino para la prueba (default: galleypub@galleypub.es)'
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('PRUEBA DE CONEXIÓN SMTP PARA GALLEY PUB'))
        self.stdout.write(self.style.WARNING('=' * 70))
        
        # Mostrar configuración
        self.stdout.write('\n📧 CONFIGURACIÓN ACTUAL:')
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"  EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Prueba 1: Conexión SMTP directa
        self.stdout.write('\n🔗 PRUEBA 1: Conexión SMTP directa...')
        try:
            if settings.EMAIL_USE_SSL:
                conexion = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            else:
                conexion = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            
            self.stdout.write(self.style.SUCCESS('  ✅ Conexión SMTP establecida'))
            
            # Prueba 2: Login
            self.stdout.write('\n🔐 PRUEBA 2: Autenticación...')
            conexion.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            self.stdout.write(self.style.SUCCESS('  ✅ Autenticación exitosa'))
            
            conexion.quit()
            
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error de autenticación: {str(e)}'))
            self.stdout.write(self.style.ERROR('     Verifica usuario y contraseña en .env'))
            return
        except smtplib.SMTPException as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error SMTP: {str(e)}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error de conexión: {str(e)}'))
            return
        
        # Prueba 3: Enviar email de prueba
        self.stdout.write(f'\n📨 PRUEBA 3: Enviando email de prueba a {recipient}...')
        try:
            resultado = send_mail(
                subject='🧪 PRUEBA: Galley Pub - Conexión SMTP',
                message='Este es un email de prueba de la conexión SMTP.\n\nSi lo recibiste, ¡todo está funcionando correctamente!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ Email enviado exitosamente (resultado: {resultado})'))
            self.stdout.write(self.style.SUCCESS('\n✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error al enviar email: {str(e)}'))
            self.stdout.write(self.style.ERROR('\n❌ Verifica la configuración y los logs'))
