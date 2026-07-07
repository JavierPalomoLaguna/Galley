from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django_ratelimit.decorators import ratelimit
from ProyectoWebApp.sitemaps import StaticViewSitemap, BlogSitemap
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from ProyectoWebApp import views

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ProyectoWebApp.urls')),
    path('servicios/', include('servicios.urls')),
    path('blog/', include('blog.urls')),
    path('contacto/', include('contacto.urls')),
    path('password_reset/', ratelimit(key='ip', rate='5/m', method=['POST'], block=True)(auth_views.PasswordResetView.as_view()), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('politica-cookies/', views.politica_cookies, name='politica_cookies'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ============================================================================
# Handlers personalizados para errores HTTP
# ============================================================================
handler404 = 'ProyectoWebApp.views.handler_404'
handler500 = 'ProyectoWebApp.views.handler_500'