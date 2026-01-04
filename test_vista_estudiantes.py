import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from propiedades.models import Propiedad

# Simular exactamente lo que hace la vista
propiedades_estudiantes = Propiedad.objects.filter(
    estado='activa',
    especial_estudiantes=True
).select_related('propietario', 'categoria').prefetch_related('imagenes')[:12]

print(f"QuerySet evaluado: {list(propiedades_estudiantes)}")
print(f"\nCantidad: {len(propiedades_estudiantes)}")
print(f"Tipo: {type(propiedades_estudiantes)}")

for prop in propiedades_estudiantes:
    print(f"\n--- Propiedad {prop.id} ---")
    print(f"Título: {prop.titulo}")
    print(f"Estado: {prop.estado}")
    print(f"Especial estudiantes: {prop.especial_estudiantes}")
    print(f"Imagen principal (property): {prop.imagen_principal}")
    if prop.imagen_principal:
        print(f"URL de la imagen: {prop.imagen_principal.imagen.url}")
