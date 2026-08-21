# -*- coding: utf-8 -*-
"""
Fuente única de verdad para nombre/ícono/color de cada tipo de propiedad.
Usado por la sección "Buscar por categoría" del inicio y por la etiqueta de
categoría que se muestra sobre la foto de cada propiedad, para que el mismo
tipo tenga siempre el mismo color en toda la web.
"""

CATEGORIAS = {
    'departamento': {'nombre': 'Departamento', 'nombre_plural': 'Departamentos', 'icono': 'fa-building', 'color': '#2563EB'},
    'casa': {'nombre': 'Casa', 'nombre_plural': 'Casas', 'icono': 'fa-home', 'color': '#16A34A'},
    'local': {'nombre': 'Local', 'nombre_plural': 'Locales', 'icono': 'fa-store', 'color': '#9333EA'},
    'oficina': {'nombre': 'Oficina', 'nombre_plural': 'Oficinas', 'icono': 'fa-briefcase', 'color': '#EA580C'},
    'terreno': {'nombre': 'Terreno', 'nombre_plural': 'Terrenos', 'icono': 'fa-map', 'color': '#CA8A04'},
    'cuarto': {'nombre': 'Cuarto', 'nombre_plural': 'Cuartos', 'icono': 'fa-door-open', 'color': '#DB2777'},
}

CATEGORIA_DEFAULT = {'nombre': 'Propiedad', 'nombre_plural': 'Propiedades', 'icono': 'fa-building', 'color': '#6B7280'}


def info_categoria(tipo):
    """Devuelve el dict nombre/icono/color de un tipo, con respaldo neutro si no está mapeado."""
    return CATEGORIAS.get(tipo, CATEGORIA_DEFAULT)
