import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from django.test import RequestFactory
from propiedades.views import estudiantes

# Crear una request falsa
factory = RequestFactory()
request = factory.get('/propiedades/estudiantes/')

# Llamar a la vista
response = estudiantes(request)

print(f"Status code: {response.status_code}")
print(f"Template usado: {response.template_name}")

# Ver el contexto
context = response.context_data
print(f"\nContexto completo: {context.keys()}")
print(f"\nPropiedades en contexto: {context['propiedades_estudiantes']}")
print(f"Cantidad: {len(context['propiedades_estudiantes'])}")

for prop in context['propiedades_estudiantes']:
    print(f"\n- {prop.id}: {prop.titulo}")
    print(f"  Estado: {prop.estado}")
    print(f"  Especial: {prop.especial_estudiantes}")
