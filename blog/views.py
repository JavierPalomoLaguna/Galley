"""
Vistas del blog. Incluye manejo robusto de errores y logging.
"""

import logging
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from utils.decorators import handle_view_errors, handle_db_errors, log_performance
from blog.models import Post, Categoria

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@handle_view_errors(template_500='500.html')
@handle_db_errors
@log_performance
def blog(request):
    """
    Página principal del blog con todos los posts ordenados por fecha.
    
    Manejo de errores:
    - Si no hay posts, retorna lista vacía
    - Si falla BD, retorna página de error 503
    - Si falla renderizado, retorna página de error 500
    """
    try:
        posts = Post.objects.prefetch_related('categorias').order_by('-created')
        categorias_unicas = {}
        
        for post in posts:
            try:
                for cat in post.categorias.all():
                    categorias_unicas[cat.nombre] = cat
            except Exception as e:
                logger.warning(
                    f"Error al procesar categorías del post {post.id}: {str(e)}",
                    exc_info=True
                )
                continue
        
        logger.info(f"Blog: {posts.count()} posts cargados")
        
        context = {
            'posts': posts,
            'categorias_unicas': categorias_unicas.values(),
            'meta_title': 'Blog de Desarrollo Web y Marketing Digital | Código Vivo Studio',
            'meta_description': 'Consejos sobre desarrollo web, tiendas online y posicionamiento SEO para restaurantes y comercios.',
        }
        return render(request, 'blog/blog.html', context)
    
    except Exception as e:
        logger.error(
            f"Error crítico en blog: {str(e)}",
            exc_info=True
        )
        raise


@require_http_methods(["GET"])
@handle_view_errors(template_500='500.html')
@handle_db_errors
@log_performance
def categoria(request, categoria_id):
    """
    Posts filtrados por categoría específica.
    
    Args:
        request: Objeto de solicitud HTTP
        categoria_id: ID de la categoría
    
    Manejo de errores:
    - Si categoría no existe, retorna 404
    - Si falla BD, retorna página de error 503
    - Si falla renderizado, retorna página de error 500
    """
    try:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        posts = Post.objects.filter(categorias=categoria).order_by('-created')
        
        logger.info(f"Categoría {categoria_id}: {posts.count()} posts cargados")
        
        context = {
            "categoria": categoria,
            "posts": posts,
            'meta_title': f'{categoria.nombre} - Blog | Código Vivo Studio',
            'meta_description': f'Artículos sobre {categoria.nombre}. Consejos y noticias del sector.',
        }
        return render(request, "blog/categoria.html", context)
    
    except ObjectDoesNotExist:
        logger.warning(f"Categoría no encontrada: {categoria_id}")
        # El decorador @handle_view_errors lo manejará
        raise
    
    except Exception as e:
        logger.error(
            f"Error en categoría {categoria_id}: {str(e)}",
            exc_info=True
        )
        raise


@require_http_methods(["GET"])
@handle_view_errors(template_500='500.html')
@handle_db_errors
@log_performance
def post_detail(request, post_id):
    """
    Detalle completo de un post individual.
    
    Args:
        request: Objeto de solicitud HTTP
        post_id: ID del post
    
    Manejo de errores:
    - Si post no existe, retorna 404
    - Si falla BD, retorna página de error 503
    - Si falla renderizado, retorna página de error 500
    """
    try:
        post = get_object_or_404(Post, id=post_id)
        
        logger.info(f"Post accedido: {post_id} - {post.titulo}")
        
        context = {
            'post': post,
            'meta_title': f'{post.titulo} | Código Vivo Studio',
            'meta_description': post.contenido[:155] if post.contenido else '',
        }
        return render(request, 'blog/post_detail.html', context)
    
    except ObjectDoesNotExist:
        logger.warning(f"Post no encontrado: {post_id}")
        # El decorador @handle_view_errors lo manejará
        raise
    
    except Exception as e:
        logger.error(
            f"Error al cargar post {post_id}: {str(e)}",
            exc_info=True
        )
        raise