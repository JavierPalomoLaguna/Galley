from django.urls import path
from ProyectoWebApp import views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', views.home, name='index'),
    #path('home/', lambda request: redirect('/', permanent=True)),
    path('politica-privacidad/', views.politica_privacidad, name='politica_privacidad'),
    path('aviso-legal/', views.aviso_legal, name='aviso_legal'),
]

# Rutas de testing para ver páginas de error personalizadas (solo en desarrollo)
if settings.DEBUG:
    # Testing de errores
    def test_404_view(request):
        """Test para ver la página 404 personalizada"""
        return views.handler_404(request)
    
    def test_500_view(request):
        """Test para ver la página 500 personalizada"""
        return views.handler_500(request)
    
    def test_403_view(request):
        """Test para ver la página 403 personalizada"""
        from django.shortcuts import render
        return render(request, '403.html', status=403)
    
    def test_error_exception(request):
        """Test que lanza una excepción para ver manejo"""
        raise Exception("Error de prueba para testing")
    
    urlpatterns += [
        path('test-404/', test_404_view, name='test_404'),
        path('test-500/', test_500_view, name='test_500'),
        path('test-403/', test_403_view, name='test_403'),
        path('test-error/', test_error_exception, name='test_error'),
    ]
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)