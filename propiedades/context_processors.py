# -*- coding: utf-8 -*-
"""
Preferencia de ubicación del navbar ("Mi ubicación"): se guarda 100% del
lado del cliente en una cookie (ver static/js/mi_ubicacion.js), nunca la
escribe el backend. Este módulo es el único lugar que la lee/parsea, tanto
para pintar el botón del navbar (vía el context processor) como para el
ranking geográfico en propiedades/views.py (inicio, listado_propiedades).
"""
import json
from urllib.parse import unquote

COOKIE_UBICACION = 'lc_ubicacion'


def obtener_ubicacion_cookie(request):
    """
    Devuelve {'ciudad': str|None, 'provincia': str|None} según la cookie
    lc_ubicacion, o None si no hay ubicación elegida (o la cookie está
    corrupta/manipulada).
    """
    crudo = request.COOKIES.get(COOKIE_UBICACION)
    if not crudo:
        return None
    try:
        # mi_ubicacion.js escribe la cookie con encodeURIComponent (necesario
        # porque el JSON tiene comas/espacios/tildes) - Django NO decodifica
        # el valor de una cookie automáticamente, así que hay que revertirlo acá.
        datos = json.loads(unquote(crudo))
    except (ValueError, TypeError):
        return None
    ciudad = (datos.get('ciudad') or '').strip() or None
    provincia = (datos.get('provincia') or '').strip() or None
    if not ciudad and not provincia:
        return None
    # 'etiqueta' se precalcula acá (y no con varios |default encadenados en
    # el template) porque Django resuelve el argumento de un filtro de forma
    # estricta: si ubicacion_actual fuera None, "ubicacion_actual.provincia"
    # usado como argumento de |default rompe en vez de devolver vacío.
    return {'ciudad': ciudad, 'provincia': provincia, 'etiqueta': ciudad or provincia}


def ubicacion(request):
    """Context processor: expone la ubicación elegida a todos los templates."""
    return {'ubicacion_actual': obtener_ubicacion_cookie(request)}
