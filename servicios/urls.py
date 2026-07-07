from django.urls import path
from . import views

urlpatterns = [
    path('', views.carta_cocteles, name='carta_cocteles'),
    path('carta/', views.carta_cocteles),
]