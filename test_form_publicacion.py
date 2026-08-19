import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from usuarios.models import Usuario
from usuarios.forms import PublicacionCompaneroForm

# Simular datos del POST como vendrían del formulario HTML
post_data = {
    'titulo': 'Depto 2 ambientes Palermo',
    'descripcion': 'Busco compañero/a para compartir',
    'provincia': 'Buenos Aires',
    'ciudad': 'CABA',
    'distrito': 'Palermo',
    'direccion': 'Cerca de Av Santa Fe',
    'precio_mensual': '50000',  # Como string, así viene del formulario
    'habitaciones_totales': '2',
    'habitaciones_disponibles': '1',
    'banos': '1',
    'preferencia_genero': 'indiferente',
    # Checkboxes NO marcados no se envían (esto es importante!)
    # 'amoblado': 'on',  # Solo se envía si está marcado
    'wifi': 'on',
    'cocina': 'on',
}

print("Datos del POST simulado:")
for k, v in post_data.items():
    print(f"  {k}: {v}")

print("\n" + "="*80)
print("Creando formulario con estos datos...")
print("="*80)

form = PublicacionCompaneroForm(data=post_data)

print(f"\nForm is bound: {form.is_bound}")
print(f"Form is valid: {form.is_valid()}")

if not form.is_valid():
    print("\n❌ ERRORES DEL FORMULARIO:")
    for field, errors in form.errors.items():
        print(f"  Campo '{field}':")
        for error in errors:
            print(f"    - {error}")
else:
    print("\n✅ Formulario válido!")
    print("\nDatos limpiados (cleaned_data):")
    for k, v in form.cleaned_data.items():
        print(f"  {k}: {v} (type: {type(v).__name__})")
    
    print("\n🎉 El formulario funcionaría correctamente!")
