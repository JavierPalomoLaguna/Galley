from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_cocteleria, name='index_cocteleria'),
    path('carta/', views.carta_cocteles, name='carta_cocteles'),
]