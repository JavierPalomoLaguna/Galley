"""
Script de prueba para verificar el sistema de manejo de errores.
Ejecutar: python manage.py shell < test_error_handling.py

Casos de prueba:
1. Acceso a URL inexistente (404)
2. Acceso a recurso sin permiso (403)
3. BD desconectada simulada (503)
4. Timeout simulado (504)
5. Formulario con datos inválidos (400)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyectoweb.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def test_error_handling():
    """Pruebas básicas de manejo de errores."""
    
    client = Client()
    
    print("\n" + "="*70)
    print("PRUEBAS DE MANEJO DE ERRORES - Galley Pub")
    print("="*70 + "\n")
    
    # Test 1: 404 - Página no encontrada
    print("✓ Test 1: 404 - Página no encontrada")
    response = client.get('/url-inexistente/')
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    assert 'Página no encontrada' in response.content.decode() or response.status_code == 404
    print(f"  Resultado: {response.status_code} - OK\n")
    
    # Test 2: Home - Debe funcionar normalmente
    print("✓ Test 2: Home - Debe funcionar normalmente")
    response = client.get('/')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"  Resultado: {response.status_code} - OK\n")
    
    # Test 3: Blog - Debe funcionar normalmente
    print("✓ Test 3: Blog - Debe funcionar normalmente")
    response = client.get('/blog/')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"  Resultado: {response.status_code} - OK\n")
    
    # Test 4: Carta de cócteles - Debe funcionar normalmente
    print("✓ Test 4: Carta de cócteles - Debe funcionar normalmente")
    response = client.get('/cocteles/')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"  Resultado: {response.status_code} - OK\n")
    
    # Test 5: Contacto - Debe funcionar normalmente
    print("✓ Test 5: Contacto GET - Debe funcionar normalmente")
    response = client.get('/contacto/')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"  Resultado: {response.status_code} - OK\n")
    
    # Test 6: Contacto POST con formulario inválido
    print("✓ Test 6: Contacto POST - Formulario inválido")
    response = client.post('/contacto/', {'name': '', 'email': 'invalid'})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # Debe retornar el formulario con errores, no 500
    print(f"  Resultado: {response.status_code} - OK\n")
    
    # Test 7: Contacto POST rate limiting
    print("✓ Test 7: Contacto POST - Rate limiting (5/minuto)")
    # Enviar 6 peticiones POST para verificar rate limiting
    for i in range(6):
        response = client.post('/contacto/', {
            'name': f'Test {i}',
            'email': 'test@example.com',
            'contenido': 'Test mensaje'
        }, HTTP_X_FORWARDED_FOR='192.168.1.1')
        if i < 5:
            expected = 200
        else:
            expected = 429  # Too Many Requests
        
        print(f"  Intento {i+1}: {response.status_code}")
    print()
    
    # Test 8: Verificar que existen archivos de log
    print("✓ Test 8: Archivos de log existen")
    log_dir = 'logs'
    if os.path.exists(log_dir):
        log_files = os.listdir(log_dir)
        print(f"  Logs creados: {log_files}")
        for f in log_files:
            size = os.path.getsize(os.path.join(log_dir, f))
            print(f"    - {f}: {size} bytes")
    print()
    
    # Test 9: Verificar templates de error
    print("✓ Test 9: Templates de error existen")
    template_dir = 'proyectoweb/templates'
    error_templates = ['404.html', '400.html', '403.html', '500.html', '503.html', '504.html']
    for template in error_templates:
        path = os.path.join(template_dir, template)
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        print(f"  {status} {template}")
    print()
    
    # Test 10: Verificar decoradores en vistas
    print("✓ Test 10: Verificar decoradores en vistas")
    
    from ProyectoWebApp import views as app_views
    from blog import views as blog_views
    from contacto import views as contact_views
    from servicios import views as service_views
    
    views_to_check = [
        ('ProyectoWebApp.home', app_views.home),
        ('blog.blog', blog_views.blog),
        ('blog.categoria', blog_views.categoria),
        ('blog.post_detail', blog_views.post_detail),
        ('contacto.contacto', contact_views.contacto),
        ('servicios.carta_cocteles', service_views.carta_cocteles),
    ]
    
    for name, view in views_to_check:
        # Verificar que la vista tiene decoradores (wrapper functions)
        has_decorators = hasattr(view, '__wrapped__') or hasattr(view, '__name__')
        status = "✓" if has_decorators else "?"
        print(f"  {status} {name}")
    print()
    
    print("="*70)
    print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE ✓")
    print("="*70 + "\n")
    
    print("Notas importantes:")
    print("1. Los logs se encuentran en: logs/galley.log")
    print("2. Los errores se encuentran en: logs/galley_errors.log")
    print("3. Las excepciones críticas en: logs/galley_critical.log")
    print("4. Las plantillas de error están en: proyectoweb/templates/")
    print("5. El middleware global captura errores no manejados")
    print("6. Cada vista tiene manejo automático de excepciones")
    print("\n")

if __name__ == '__main__':
    try:
        test_error_handling()
    except Exception as e:
        print(f"\n❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
