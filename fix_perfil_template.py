"""
Script para optimizar el template de perfil
Cambios:
1. Reducir tamaño de secciones de verificación
2. Mover perfil de búsqueda más arriba (antes de estadísticas)
3. Agregar tooltips a etiquetas
4. Eliminar sección redundante de Estilo de Vida
"""

import re

# Leer el archivo actual
with open('usuarios/templates/usuarios/perfil.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Reducir tamaño de sección de verificación - reemplazar p-8 por p-6, border-2 por border, etc
content = re.sub(
    r'<div class="p-8 space-y-4">',
    '<div class="p-6 space-y-3">',
    content, count=1
)

# Reducir tamaño de cards de verificación
content = re.sub(
    r'rounded-2xl border-2',
    'rounded-xl border',
    content
)

content = re.sub(
    r'w-14 h-14 rounded-xl',
    'w-10 h-10 rounded-lg',
    content
)

content = re.sub(
    r'w-7 h-7 text-white',
    'w-5 h-5 text-white',
    content
)

content = re.sub(
    r'font-bold text-gray-900 text-lg',
    'font-semibold text-gray-900 text-sm',
    content
)

content = re.sub(
    r'text-gray-600 font-medium',
    'text-gray-600 text-sm',
    content
)

# Reducir botones
content = re.sub(
    r'px-6 py-3 rounded-xl text-sm font-bold',
    'px-4 py-2 rounded-lg text-xs font-bold',
    content
)

content =re.sub(
    r'px-5 py-2\.5 rounded-xl text-sm font-semibold',
    'px-3 py-1.5 rounded-lg text-xs font-semibold',
    content
)

# 2. Encontrar la sección completa de "Estilo de Vida" y eliminarla
estilo_vida_pattern = r'(\s*<!-- Estilo de Vida - Modernizado -->.*?{% endif %}\s*{% endwith %}\s*</div>\s*</div>\s*</div>\s*{% endif %})'
content = re.sub(estilo_vida_pattern, '', content, flags=re.DOTALL)

print("✓ Template optimizado - cambios aplicados")
print("  - Reducido tamaño de sección de verificación")
print("  - Eliminada sección redundante 'Estilo de Vida'")
print("\nPor favor revisa manualmente:")
print("  - Mover perfil de búsqueda más arriba en template")
print("  - Agregar tooltips a etiquetas usando title attribute")

# Guardar
with open('usuarios/templates/usuarios/perfil_optimizado.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Archivo guardado como: usuarios/templates/usuarios/perfil_optimizado.html")
print("Revisa el archivo y si está correcto, reemplaza perfil.html")
