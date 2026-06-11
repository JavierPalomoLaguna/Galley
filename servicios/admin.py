from django.contrib import admin
from .models import Categoria, Coctel, Ingrediente


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'num_cocteles')
    list_editable = ('orden',)
    ordering = ('orden', 'nombre')

    def num_cocteles(self, obj):
        return obj.cocteles.count()
    num_cocteles.short_description = 'Cócteles'


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')


@admin.register(Coctel)
class CoctelAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'precio', 'sin_alcohol', 'destacado_en_index', 'created')
    list_filter = ('categoria', 'sin_alcohol', 'destacado_en_index')
    search_fields = ('titulo', 'contenido')
    readonly_fields = ('created', 'updated')
    filter_horizontal = ('alergenos',)
    list_editable = ('destacado_en_index', 'sin_alcohol')

    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'contenido', 'categoria', 'precio', 'sin_alcohol')
        }),
        ('Imagen y alérgenos', {
            'fields': ('imagen', 'alergenos')
        }),
        ('Visibilidad', {
            'fields': ('destacado_en_index',)
        }),
        ('Metadatos', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )