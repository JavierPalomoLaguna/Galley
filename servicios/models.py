from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True, verbose_name='Nombre')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden en carta')

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    @property
    def slug(self):
        return slugify(self.nombre)


class Ingrediente(models.Model):
    INGREDIENTES_CHOICES = [
        ('gluten', 'Gluten'),
        ('crustaceos', 'Crustáceos'),
        ('huevos', 'Huevos'),
        ('pescado', 'Pescado'),
        ('cacahuetes', 'Cacahuetes'),
        ('soja', 'Soja'),
        ('lacteos', 'Lácteos'),
        ('frutos_cascara', 'Frutos de Cáscara'),
        ('apio', 'Apio'),
        ('mostaza', 'Mostaza'),
        ('sesamo', 'Sésamo'),
        ('sulfitos', 'Sulfitos'),
        ('altramuces', 'Altramuces'),
        ('moluscos', 'Moluscos'),
    ]

    codigo = models.CharField(max_length=20, choices=INGREDIENTES_CHOICES, unique=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'ingrediente / alérgeno'
        verbose_name_plural = 'ingredientes / alérgenos'

    def __str__(self):
        return self.nombre


class Coctel(models.Model):
    titulo = models.CharField(max_length=80, verbose_name='Nombre del cóctel')
    contenido = models.TextField(max_length=500, verbose_name='Descripción')
    imagen = models.ImageField(upload_to='cocteles')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Categoría',
        related_name='cocteles',
    )
    precio = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    alergenos = models.ManyToManyField(Ingrediente, blank=True)
    destacado_en_index = models.BooleanField(
        default=False,
        verbose_name='Mostrar en galería del inicio'
    )
    sin_alcohol = models.BooleanField(default=False, verbose_name='Sin alcohol')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'cóctel'
        verbose_name_plural = 'cócteles'
        ordering = ['categoria__orden', 'categoria__nombre', 'titulo']

    def __str__(self):
        cat = self.categoria.nombre if self.categoria else 'Sin categoría'
        return f"{self.titulo} — {cat}"

    def get_alergenos_html(self):
        alergenos_data = {
            'gluten':        {'icon': 'fa-bread-slice',   'color': '#8B4513', 'title': 'Contiene gluten'},
            'crustaceos':    {'icon': 'fa-shrimp',        'color': '#FF6B6B', 'title': 'Crustáceos'},
            'huevos':        {'icon': 'fa-egg',           'color': '#FFD700', 'title': 'Huevos'},
            'pescado':       {'icon': 'fa-fish',          'color': '#4682B4', 'title': 'Pescado'},
            'cacahuetes':    {'icon': 'fa-seedling',      'color': '#8B7355', 'title': 'Cacahuetes'},
            'soja':          {'icon': 'fa-leaf',          'color': '#32CD32', 'title': 'Soja'},
            'lacteos':       {'icon': 'fa-cheese',        'color': '#F0E68C', 'title': 'Lácteos'},
            'frutos_cascara':{'icon': 'fa-tree',          'color': '#A0522D', 'title': 'Frutos de cáscara'},
            'apio':          {'icon': 'fa-carrot',        'color': '#90EE90', 'title': 'Apio'},
            'mostaza':       {'icon': 'fa-mortar-pestle', 'color': '#FFD700', 'title': 'Mostaza'},
            'sesamo':        {'icon': 'fa-seedling',      'color': '#F4A460', 'title': 'Sésamo'},
            'sulfitos':      {'icon': 'fa-flask',         'color': '#C8A951', 'title': 'Sulfitos'},
            'altramuces':    {'icon': 'fa-seedling',      'color': '#8A2BE2', 'title': 'Altramuces'},
            'moluscos':      {'icon': 'fa-water',         'color': '#FFB6C1', 'title': 'Moluscos'},
        }

        html_icons = []
        for alergeno_rel in self.alergenos.all():
            data = alergenos_data.get(alergeno_rel.codigo)
            if data:
                html_icons.append(
                    f'<i class="fas {data["icon"]}" style="color:{data["color"]};'
                    f'font-size:1.1rem;margin:0 3px;" title="{data["title"]}"></i>'
                )

        return ' '.join(html_icons) if html_icons else ''