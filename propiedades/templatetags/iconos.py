# -*- coding: utf-8 -*-
"""
Sistema unico de iconos de LaColmena.

Los iconos son los de la libreria Lucide (lucide.dev, ISC license), para
que toda la app use exactamente el mismo lenguaje visual (linea
redondeada, 2px de grosor, amarillo #F2B705) en vez de mezclar Font
Awesome u otras librerias, y sin depender de dibujos a mano.

Uso en cualquier template (disponible en todos lados via TEMPLATES.OPTIONS.builtins,
no hace falta {% load %}):

    {% icono "cochera" %}
    {% icono "cochera" clase="mr-2" %}
    {% icono "cochera" clase="text-2xl" color="currentColor" %}
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Cada valor es el contenido interno del <svg> (paths/shapes) de un icono
# de Lucide, en un viewBox de 24x24, pensado para trazo (stroke), no relleno.
ICONOS = {
    # --- Datos principales de la propiedad ---
    'superficie': '''
        <path d="M8 3H5a2 2 0 0 0-2 2v3"/>
        <path d="M21 8V5a2 2 0 0 0-2-2h-3"/>
        <path d="M3 16v3a2 2 0 0 0 2 2h3"/>
        <path d="M16 21h3a2 2 0 0 0 2-2v-3"/>
    ''',
    'dormitorios': '''
        <path d="M2 4v16"/>
        <path d="M2 8h18a2 2 0 0 1 2 2v10"/>
        <path d="M2 17h20"/>
        <path d="M6 8v9"/>
    ''',
    'banos': '''
        <path d="M10 4 8 6"/>
        <path d="M17 19v2"/>
        <path d="M2 12h20"/>
        <path d="M7 19v2"/>
        <path d="M9 5 7.621 3.621A2.121 2.121 0 0 0 4 5v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/>
    ''',
    'mascotas': '''
        <path d="M11.25 16.25h1.5L12 17z"/>
        <path d="M16 14v.5"/>
        <path d="M4.42 11.247A13.152 13.152 0 0 0 4 14.556C4 18.728 7.582 21 12 21s8-2.272 8-6.444a11.702 11.702 0 0 0-.493-3.309"/>
        <path d="M8 14v.5"/>
        <path d="M8.5 8.5c-.384 1.05-1.083 2.028-2.344 2.5-1.931.722-3.576-.297-3.656-1-.113-.994 1.177-6.53 4-7 1.923-.321 3.651.845 3.651 2.235A7.497 7.497 0 0 1 14 5.277c0-1.39 1.844-2.598 3.767-2.277 2.823.47 4.113 6.006 4 7-.08.703-1.725 1.722-3.656 1-1.261-.472-1.855-1.45-2.239-2.5"/>
    ''',
    'cochera': '''
        <rect width="18" height="18" x="3" y="3" rx="2"/>
        <path d="M9 17V7h4a3 3 0 0 1 0 6H9"/>
    ''',

    # --- Caracteristicas ---
    'amoblado': '''
        <path d="M20 9V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v3"/>
        <path d="M2 16a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-5a2 2 0 0 0-4 0v1.5a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5V11a2 2 0 0 0-4 0z"/>
        <path d="M4 18v2"/>
        <path d="M20 18v2"/>
        <path d="M12 4v9"/>
    ''',
    'estacionamiento': '''
        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/>
        <circle cx="7" cy="17" r="2"/>
        <path d="M9 17h6"/>
        <circle cx="17" cy="17" r="2"/>
    ''',
    'expensas': '''
        <path d="M12 17V7"/>
        <path d="M16 8h-6a2 2 0 0 0 0 4h4a2 2 0 0 1 0 4H8"/>
        <path d="M4 3a1 1 0 0 1 1-1 1.3 1.3 0 0 1 .7.2l.933.6a1.3 1.3 0 0 0 1.4 0l.934-.6a1.3 1.3 0 0 1 1.4 0l.933.6a1.3 1.3 0 0 0 1.4 0l.933-.6a1.3 1.3 0 0 1 1.4 0l.934.6a1.3 1.3 0 0 0 1.4 0l.933-.6A1.3 1.3 0 0 1 19 2a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1 1.3 1.3 0 0 1-.7-.2l-.933-.6a1.3 1.3 0 0 0-1.4 0l-.934.6a1.3 1.3 0 0 1-1.4 0l-.933-.6a1.3 1.3 0 0 0-1.4 0l-.933.6a1.3 1.3 0 0 1-1.4 0l-.934-.6a1.3 1.3 0 0 0-1.4 0l-.933.6a1.3 1.3 0 0 1-.7.2 1 1 0 0 1-1-1z"/>
    ''',

    # --- Comodidades ---
    'balcon': '''
        <path d="M3 10h18"/>
        <path d="M3 21h18"/>
        <path d="M6 21v-9.5"/>
        <path d="M10.5 21v-9.5"/>
        <path d="M15 21v-9.5"/>
        <path d="M19.5 21v-9.5"/>
    ''',
    'patio': '''
        <path d="M12 5a3 3 0 1 1 3 3m-3-3a3 3 0 1 0-3 3m3-3v1M9 8a3 3 0 1 0 3 3M9 8h1m5 0a3 3 0 1 1-3 3m3-3h-1m-2 3v-1"/>
        <circle cx="12" cy="8" r="2"/>
        <path d="M12 10v12"/>
        <path d="M12 22c4.2 0 7-1.667 7-5-4.2 0-7 1.667-7 5Z"/>
        <path d="M12 22c-4.2 0-7-1.667-7-5 4.2 0 7 1.667 7 5Z"/>
    ''',
    'parrilla': '''
        <path d="M8 8c-1.2 -1 -1.2 -2 0 -3s1.2 -2 0 -3"/>
        <path d="M12 8c-1.2 -1 -1.2 -2 0 -3s1.2 -2 0 -3"/>
        <path d="M16 8c-1.2 -1 -1.2 -2 0 -3s1.2 -2 0 -3"/>
        <path d="M4 9h16"/>
        <path d="M4 9a8 6 0 0 0 16 0"/>
        <path d="M1 11h4"/>
        <path d="M8 11q1 2 3 2"/>
        <path d="M9 15 4 21"/>
        <path d="M15 15 20 21"/>
        <path d="M6 18h12"/>
        <circle cx="20" cy="21" r="1.3"/>
    ''',
    'aire_acondicionado': '''
        <path d="m10 20-1.25-2.5L6 18"/>
        <path d="M10 4 8.75 6.5 6 6"/>
        <path d="m14 20 1.25-2.5L18 18"/>
        <path d="m14 4 1.25 2.5L18 6"/>
        <path d="m17 21-3-6h-4"/>
        <path d="m17 3-3 6 1.5 3"/>
        <path d="M2 12h6.5L10 9"/>
        <path d="m20 10-1.5 2 1.5 2"/>
        <path d="M22 12h-6.5L14 15"/>
        <path d="m4 10 1.5 2L4 14"/>
        <path d="m7 21 3-6-1.5-3"/>
        <path d="m7 3 3 6h4"/>
    ''',
    'calefaccion': '''
        <path d="M12 3q1 4 4 6.5t3 5.5a1 1 0 0 1-14 0 5 5 0 0 1 1-3 1 1 0 0 0 5 0c0-2-1.5-3-1.5-5q0-2 2.5-4"/>
    ''',
    'ascensor': '''
        <path d="M12 2v20"/>
        <path d="m8 18 4 4 4-4"/>
        <path d="m8 6 4-4 4 4"/>
    ''',
    'wifi': '''
        <path d="M12 20h.01"/>
        <path d="M2 8.82a15 15 0 0 1 20 0"/>
        <path d="M5 12.859a10 10 0 0 1 14 0"/>
        <path d="M8.5 16.429a5 5 0 0 1 7 0"/>
    ''',
    'lavanderia': '''
        <path d="M3 6h3"/>
        <path d="M17 6h.01"/>
        <rect width="18" height="20" x="3" y="2" rx="2"/>
        <circle cx="12" cy="13" r="5"/>
        <path d="M12 18a2.5 2.5 0 0 0 0-5 2.5 2.5 0 0 1 0-5"/>
    ''',
    'terraza': '''
        <circle cx="12" cy="12" r="4"/>
        <path d="M12 3v1"/>
        <path d="M12 20v1"/>
        <path d="M3 12h1"/>
        <path d="M20 12h1"/>
        <path d="m18.364 5.636-.707.707"/>
        <path d="m6.343 17.657-.707.707"/>
        <path d="m5.636 5.636.707.707"/>
        <path d="m17.657 17.657.707.707"/>
    ''',

    # --- Edificio ---
    'seguridad': '''
        <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>
        <path d="m9 12 2 2 4-4"/>
    ''',
    'accesibilidad': '''
        <circle cx="16" cy="4" r="1"/>
        <path d="m18 19 1-7-6 1"/>
        <path d="m5 8 3-3 5.5 3-2.36 3.5"/>
        <path d="M4.24 14.5a5 5 0 0 0 6.88 6"/>
        <path d="M13.76 17.5a5 5 0 0 0-6.88-6"/>
    ''',
    'piscina': '''
        <path d="M19 5a2 2 0 0 0-2 2v11"/>
        <path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>
        <path d="M7 13h10"/>
        <path d="M7 9h10"/>
        <path d="M9 5a2 2 0 0 0-2 2v11"/>
    ''',
    'gimnasio': '''
        <path d="M17.596 12.768a2 2 0 1 0 2.829-2.829l-1.768-1.767a2 2 0 0 0 2.828-2.829l-2.828-2.828a2 2 0 0 0-2.829 2.828l-1.767-1.768a2 2 0 1 0-2.829 2.829z"/>
        <path d="m2.5 21.5 1.4-1.4"/>
        <path d="m20.1 3.9 1.4-1.4"/>
        <path d="M5.343 21.485a2 2 0 1 0 2.829-2.828l1.767 1.768a2 2 0 1 0 2.829-2.829l-6.364-6.364a2 2 0 1 0-2.829 2.829l1.768 1.767a2 2 0 0 0-2.828 2.829z"/>
        <path d="m9.6 14.4 4.8-4.8"/>
    ''',
    'sauna': '''
        <path d="M12 2v2"/>
        <path d="M12 8a4 4 0 0 0-1.645 7.647"/>
        <path d="M2 12h2"/>
        <path d="M20 14.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0z"/>
        <path d="m4.93 4.93 1.41 1.41"/>
        <path d="m6.34 17.66-1.41 1.41"/>
    ''',
    'jacuzzi': '''
        <path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z"/>
        <path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97"/>
    ''',
    'quincho': '''
        <path d="M3.5 21 14 3"/>
        <path d="M20.5 21 10 3"/>
        <path d="M15.5 21 12 15l-3.5 6"/>
        <path d="M2 21h20"/>
    ''',
    'solarium': '''
        <path d="M12 2v8"/>
        <path d="m4.93 10.93 1.41 1.41"/>
        <path d="M2 18h2"/>
        <path d="M20 18h2"/>
        <path d="m19.07 10.93-1.41 1.41"/>
        <path d="M22 22H2"/>
        <path d="m8 6 4-4 4 4"/>
        <path d="M16 18a4 4 0 0 0-8 0"/>
    ''',
    'area_deportiva': '''
        <path d="M11 7a16 16 20 0 1 10.98 4.362"/>
        <path d="M12 12a13 13 0 0 1-8.66 5"/>
        <path d="M16.83 13.634a16 16 0 0 1-9.267 7.328"/>
        <path d="M20.66 17A13 13 0 0 0 12 12a13 13 0 0 1 0-10"/>
        <path d="M8.17 15.366a16 16 0 0 1-1.713-11.69"/>
        <circle cx="12" cy="12" r="10"/>
    ''',

    # --- Opciones especiales ---
    'ideal_estudiantes': '''
        <path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/>
        <path d="M22 10v6"/>
        <path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>
    ''',
    'destacada': '''
        <path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/>
        <path d="m9 12 2 2 4-4"/>
    ''',
    'alquiler_temporal': '''
        <path d="M16 14v2.2l1.6 1"/>
        <path d="M16 2v3"/>
        <path d="M21 7.338V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h2.338"/>
        <path d="M3 9h5.859"/>
        <path d="M8 2v3"/>
        <circle cx="16" cy="16" r="6"/>
    ''',
    'energia_solar': '''
        <path d="M11 2h2"/>
        <path d="m14.28 14-4.56 8"/>
        <path d="m21 22-1.558-4H4.558"/>
        <path d="M3 10v2"/>
        <path d="M6.245 15.04A2 2 0 0 1 8 14h12a1 1 0 0 1 .864 1.505l-3.11 5.457A2 2 0 0 1 16 22H4a1 1 0 0 1-.863-1.506z"/>
        <path d="M7 2a4 4 0 0 1-4 4"/>
        <path d="m8.66 7.66 1.41 1.41"/>
    ''',
}


@register.simple_tag
def icono(nombre, clase='', color='#F2B705'):
    """Renderiza un icono del sistema unico de LaColmena (trazo redondeado, 2px)."""
    contenido = ICONOS.get(nombre)
    if contenido is None:
        return ''
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" class="icono-lacolmena {clase}" '
        'style="width:1em;height:1em;display:inline-block;vertical-align:-0.125em;flex-shrink:0;">'
        '{contenido}'
        '</svg>'
    ).format(color=color, clase=clase, contenido=contenido)
    return mark_safe(svg)
