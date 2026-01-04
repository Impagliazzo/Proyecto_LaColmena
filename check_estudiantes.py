import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from propiedades.models import Propiedad

# Ver todas las propiedades
total = Propiedad.objects.count()
print(f"Total de propiedades: {total}")

# Ver propiedades con especial_estudiantes=True
estudiantes = Propiedad.objects.filter(especial_estudiantes=True)
print(f"\nPropiedades con especial_estudiantes=True: {estudiantes.count()}")

for prop in estudiantes:
    print(f"\n- ID: {prop.id}")
    print(f"  Título: {prop.titulo}")
    print(f"  Estado: {prop.estado}")
    print(f"  Especial estudiantes: {prop.especial_estudiantes}")

# Ver propiedades activas con especial_estudiantes=True
activas_estudiantes = Propiedad.objects.filter(estado='activa', especial_estudiantes=True)
print(f"\nPropiedades ACTIVAS con especial_estudiantes=True: {activas_estudiantes.count()}")

for prop in activas_estudiantes:
    print(f"\n- ID: {prop.id}")
    print(f"  Título: {prop.titulo}")
    print(f"  Estado: {prop.estado}")
