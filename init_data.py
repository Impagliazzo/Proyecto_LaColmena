# Script de inicialización con datos de ejemplo
# Ejecutar con: .\venv\Scripts\python.exe manage.py shell < init_data.py

from usuarios.models import Usuario, Perfil
from propiedades.models import Categoria, Propiedad
from suscripciones.models import PlanSuscripcion
from django.utils import timezone

print("=== Inicializando datos de ejemplo ===\n")

# Crear categorías
print("Creando categorías...")
categorias_data = [
    {'nombre': 'Departamentos', 'icono': 'fa-building', 'color': 'blue', 'orden': 1},
    {'nombre': 'Casas', 'icono': 'fa-home', 'color': 'green', 'orden': 2},
    {'nombre': 'Locales', 'icono': 'fa-store', 'color': 'purple', 'orden': 3},
    {'nombre': 'Oficinas', 'icono': 'fa-briefcase', 'color': 'orange', 'orden': 4},
    {'nombre': 'Terrenos', 'icono': 'fa-map', 'color': 'yellow', 'orden': 5},
    {'nombre': 'Bodegas', 'icono': 'fa-warehouse', 'color': 'pink', 'orden': 6},
    {'nombre': 'Alojamiento', 'icono': 'fa-bed', 'color': 'red', 'orden': 7},
]

for cat_data in categorias_data:
    cat, created = Categoria.objects.get_or_create(
        nombre=cat_data['nombre'],
        defaults=cat_data
    )
    if created:
        print(f"  ✓ Categoría '{cat.nombre}' creada")
    else:
        print(f"  - Categoría '{cat.nombre}' ya existe")

# Crear planes de suscripción
print("\nCreando planes de suscripción...")
planes_data = [
    {
        'nombre': 'Plan Básico',
        'descripcion': 'Ideal para comenzar. Primera publicación gratis.',
        'precio': 0,
        'duracion_dias': 30,
        'max_publicaciones': 1,
        'destacar_publicaciones': False,
        'soporte_prioritario': False,
        'orden': 1
    },
    {
        'nombre': 'Plan Estándar',
        'descripcion': 'Para propietarios con varias propiedades.',
        'precio': 29.99,
        'duracion_dias': 30,
        'max_publicaciones': 5,
        'destacar_publicaciones': False,
        'soporte_prioritario': False,
        'orden': 2
    },
    {
        'nombre': 'Plan Premium',
        'descripcion': 'Máxima visibilidad para tus propiedades.',
        'precio': 59.99,
        'duracion_dias': 30,
        'max_publicaciones': 15,
        'destacar_publicaciones': True,
        'soporte_prioritario': True,
        'orden': 3
    },
]

for plan_data in planes_data:
    plan, created = PlanSuscripcion.objects.get_or_create(
        nombre=plan_data['nombre'],
        defaults=plan_data
    )
    if created:
        print(f"  ✓ Plan '{plan.nombre}' creado")
    else:
        print(f"  - Plan '{plan.nombre}' ya existe")

print("\n=== Datos inicializados correctamente ===")
print("\nPara crear un superusuario ejecuta:")
print("  .\\venv\\Scripts\\python.exe manage.py createsuperuser")
print("\nPara iniciar el servidor ejecuta:")
print("  .\\venv\\Scripts\\python.exe manage.py runserver")
