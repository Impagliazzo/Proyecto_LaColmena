import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from propiedades.models import Propiedad

propiedades_estudiantes = Propiedad.objects.filter(
    estado='activa',
    especial_estudiantes=True
).select_related('propietario', 'categoria').prefetch_related('imagenes')[:12]

print(f"Cantidad encontrada: {propiedades_estudiantes.count()}")

for prop in propiedades_estudiantes:
    print(f"\nID: {prop.id}")
    print(f"Título: {prop.titulo}")
    print(f"Estado: {prop.estado}")
    print(f"Especial estudiantes: {prop.especial_estudiantes}")
    print(f"Imagen principal: {prop.imagen_principal()}")
    print(f"Cantidad de imágenes: {prop.imagenes.count()}")
