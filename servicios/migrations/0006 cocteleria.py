from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servicios', '0005_servicio_destacado_en_index'),
    ]

    operations = [
        # 1. Modelo Categoria
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80, unique=True, verbose_name='Nombre')),
                ('orden', models.PositiveIntegerField(default=0, verbose_name='Orden en carta')),
            ],
            options={
                'verbose_name': 'categoría',
                'verbose_name_plural': 'categorías',
                'ordering': ['orden', 'nombre'],
            },
        ),
        # 2. Modelo Ingrediente
        migrations.CreateModel(
            name='Ingrediente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(
                    choices=[
                        ('gluten', 'Gluten'), ('crustaceos', 'Crustáceos'), ('huevos', 'Huevos'),
                        ('pescado', 'Pescado'), ('cacahuetes', 'Cacahuetes'), ('soja', 'Soja'),
                        ('lacteos', 'Lácteos'), ('frutos_cascara', 'Frutos de Cáscara'),
                        ('apio', 'Apio'), ('mostaza', 'Mostaza'), ('sesamo', 'Sésamo'),
                        ('sulfitos', 'Sulfitos'), ('altramuces', 'Altramuces'), ('moluscos', 'Moluscos'),
                    ],
                    max_length=20, unique=True
                )),
                ('nombre', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'ingrediente / alérgeno',
                'verbose_name_plural': 'ingredientes / alérgenos',
            },
        ),
        # 3. Modelo Coctel con FK a Categoria
        migrations.CreateModel(
            name='Coctel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=80, verbose_name='Nombre del cóctel')),
                ('contenido', models.TextField(max_length=500, verbose_name='Descripción')),
                ('imagen', models.ImageField(upload_to='cocteles')),
                ('categoria', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='cocteles',
                    to='servicios.categoria',
                    verbose_name='Categoría',
                )),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('alergenos', models.ManyToManyField(blank=True, to='servicios.ingrediente')),
                ('destacado_en_index', models.BooleanField(default=False, verbose_name='Mostrar en galería del inicio')),
                ('sin_alcohol', models.BooleanField(default=False, verbose_name='Sin alcohol')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'cóctel',
                'verbose_name_plural': 'cócteles',
                'ordering': ['categoria__orden', 'categoria__nombre', 'titulo'],
            },
        ),
    ]