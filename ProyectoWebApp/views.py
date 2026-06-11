from django.shortcuts import render


def home(request):
    # Importación local para evitar dependencia circular
    from servicios.models import Coctel, Categoria

    categorias = Categoria.objects.prefetch_related('cocteles').all()
    categorias_ordenadas = []
    for cat in categorias:
        destacados = list(cat.cocteles.filter(destacado_en_index=True))
        if destacados:
            from django.utils.text import slugify
            categorias_ordenadas.append({
                'nombre': cat.nombre,
                'slug': slugify(cat.nombre),
                'cocteles': destacados,
            })

    return render(request, 'ProyectoWebApp/index.html', {
        'categorias_ordenadas': categorias_ordenadas,
    })


def politica_cookies(request):
    return render(request, 'ProyectoWebApp/politica_cookies.html', {
        'title': 'Política de Cookies',
        'meta_description': 'Política de cookies de Galley Pub.',
    })


def politica_privacidad(request):
    return render(request, 'ProyectoWebApp/politica_privacidad.html', {
        'title': 'Política de Privacidad',
        'meta_description': 'Política de privacidad de Galley Pub.',
    })


def aviso_legal(request):
    return render(request, 'ProyectoWebApp/aviso_legal.html', {
        'title': 'Aviso Legal',
        'meta_description': 'Aviso legal de Galley Pub.',
    })