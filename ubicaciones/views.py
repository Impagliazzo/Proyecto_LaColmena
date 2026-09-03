import unicodedata

from django.db.models import Count, Q
from django.http import JsonResponse

from .models import Localidad, Provincia

MAX_SUGERENCIAS = 50


def _normalizar(texto):
    """Minúsculas y sin acentos: SQLite no ignora tildes en LIKE/icontains,
    así que sin esto buscar "sae" no encontraría "Sáenz Peña"."""
    sin_acentos = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    return sin_acentos.lower()


def provincias_sugerencias(request):
    """Todas las provincias que coincidan con `q` (o todas si no hay `q`).

    Son solo 24, así que se devuelven completas para que el campo pueda
    mostrar el listado entero al hacer click, con scroll, como se pidió.
    """
    q = request.GET.get('q', '').strip()
    provincias = list(Provincia.objects.order_by('nombre').values('id', 'nombre'))
    if q:
        q_norm = _normalizar(q)
        provincias = [p for p in provincias if q_norm in _normalizar(p['nombre'])]
    return JsonResponse({'resultados': provincias})


def localidades_sugerencias(request):
    """Localidades que coincidan con `q`, opcionalmente acotadas a una provincia.

    No es un catálogo cerrado: esta lista es solo de sugerencias, el campo
    Localidad en los formularios sigue aceptando texto libre.

    `provincia_id` es opcional: los formularios de propiedad/publicación
    (selector Provincia -> Localidad) siempre lo mandan, pero cuando se omite
    la búsqueda es nacional - lo usa el buscador de "Mi ubicación" del navbar
    para poder tipear cualquier localidad del país sin elegir provincia antes.
    """
    provincia_id = request.GET.get('provincia_id', '').strip()
    q = request.GET.get('q', '').strip()

    if not provincia_id and not q:
        return JsonResponse({'resultados': [], 'mensaje': 'Elegí primero una provincia.'})

    qs = Localidad.objects.select_related('provincia')
    if provincia_id:
        qs = qs.filter(provincia_id=provincia_id)
    # El filtro por texto se hace en Python (no con icontains de SQLite) para
    # que ignore acentos - "sae" tiene que encontrar "Sáenz Peña" igual.
    localidades = list(qs.order_by('nombre').values('id', 'nombre', 'departamento', 'provincia__nombre'))
    if q:
        q_norm = _normalizar(q)
        localidades = [loc for loc in localidades if q_norm in _normalizar(loc['nombre'])]
        # Los nombres que empiezan con lo tipeado van primero (ej: "mer" ->
        # "Merlo" antes que "Villa Mercedes"), y dentro de cada grupo, orden alfabético.
        localidades.sort(key=lambda loc: not _normalizar(loc['nombre']).startswith(q_norm))
    resultados = [
        {
            'id': loc['id'],
            'nombre': loc['nombre'],
            'departamento': loc['departamento'],
            'provincia': loc['provincia__nombre'],
        }
        for loc in localidades[:MAX_SUGERENCIAS]
    ]
    return JsonResponse({'resultados': resultados})


def distritos_sugerencias(request):
    """Barrios/distritos ya cargados en el sitio (propiedades y publicaciones
    de compañero) que coincidan con `q`, opcionalmente acotados a `ciudad`.

    Sin catálogo fijo: es un campo todavía más flexible que Localidad, las
    sugerencias solo existen si ya hay datos cargados con ese texto.

    `q` vacío solo se permite si se pasa `ciudad`: en ese caso se devuelven
    los barrios más frecuentes de esa ciudad (sin filtrar texto) - lo usa el
    buscador del home para mostrar sugerencias apenas se hace click, antes
    de escribir nada (ver inicio.html + static/js/mi_ubicacion.js).
    """
    # Import diferido para evitar dependencias circulares entre apps a nivel
    # de módulo (ubicaciones no debe importar otros modelos al cargarse).
    from propiedades.models import Propiedad
    from usuarios.models import PublicacionCompanero

    q = request.GET.get('q', '').strip()
    ciudad = request.GET.get('ciudad', '').strip()

    if len(q) < 1 and not ciudad:
        return JsonResponse({'resultados': []})

    conteo = {}

    def acumular(queryset, campo_ciudad):
        filtros = Q(distrito__icontains=q) if q else Q()
        if ciudad:
            filtros &= Q(**{f'{campo_ciudad}__icontains': ciudad})
        valores = (
            queryset.filter(filtros)
            .exclude(distrito='')
            .values('distrito')
            .annotate(total=Count('id'))
        )
        for fila in valores:
            clave = fila['distrito'].strip()
            if not clave:
                continue
            conteo[clave] = conteo.get(clave, 0) + fila['total']

    acumular(Propiedad.objects.filter(estado='activa'), 'ciudad')
    acumular(PublicacionCompanero.objects.filter(estado='activa'), 'ciudad')

    resultados = sorted(conteo.items(), key=lambda item: -item[1])[:MAX_SUGERENCIAS]
    return JsonResponse({'resultados': [{'distrito': nombre} for nombre, _ in resultados]})
