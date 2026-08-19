from django.test import RequestFactory
from usuarios.forms import PerfilBusquedaForm

# Crear formulario
form = PerfilBusquedaForm()

# Ver cómo se renderiza el campo habitos_vicios
print("=== Renderizado del campo habitos_vicios ===")
print(form.fields['habitos_vicios'].choices[:3])  # Ver las primeras 3 opciones

# Intentar renderizar como string
field_html = str(form['habitos_vicios'])
print("\n=== HTML del campo (primeros 500 caracteres) ===")
print(field_html[:500])
