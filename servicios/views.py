from django.shortcuts import render
from servicios.models import Coctel, Categoria


def _agrupar_por_categoria():
    categorias = Categoria.objects.prefetch_related('cocteles').all()
    resultado = []
    for cat in categorias:
        cocteles = list(cat.cocteles.all())
        if cocteles:
            resultado.append({
                'nombre': cat.nombre,
                'slug': cat.slug,
                'cocteles': cocteles,
            })
    return resultado


def _agrupar_destacados():
    categorias = Categoria.objects.prefetch_related('cocteles').all()
    resultado = []
    for cat in categorias:
        destacados = list(cat.cocteles.filter(destacado_en_index=True))
        if destacados:
            resultado.append({
                'nombre': cat.nombre,
                'slug': cat.slug,
                'cocteles': destacados,
            })
    return resultado


def index_cocteleria(request):
    context = {
        'categorias_ordenadas': _agrupar_destacados(),
        'meta_title': 'Galley Pub | Coctelería en Candás, Asturias',
        'meta_description': 'Galley Pub en Candás, Asturias. Mejor Gin Tonic de Asturias, Mejor Bartender y Mejor Decoración.',
    }
    return render(request, 'servicios/index_cocteleria.html', context)


def carta_cocteles(request):
    context = {
        'categorias_ordenadas': _agrupar_por_categoria(),
        'meta_title': 'Carta de Cócteles | Galley Pub',
        'meta_description': 'Descubre nuestra carta completa: clásicos, tropicales, sin alcohol y especiales.',
    }
    return render(request, 'servicios/carta_cocteles.html', context)