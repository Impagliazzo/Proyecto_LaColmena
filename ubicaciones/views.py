from django.db.models import Count, Q
from django.http import JsonResponse

from .models import Localidad, Provincia

MAX_SUGERENCIAS = 50


def provincias_sugerencias(request):
    """Todas las provincias que coincidan con `q` (o todas si no hay `q`).

    Son solo 24, así que se devuelven completas para que el campo pueda
    mostrar el listado entero al hacer click, con scroll, como se pidió.
    """
    q = request.GET.get('q', '').strip()
    qs = Provincia.objects.all()
    if q:
        qs = qs.filter(nombre__icontains=q)
    provincias = list(qs.order_by('nombre').values('id', 'nombre'))
    return JsonResponse({'resultados': provincias})


def localidades_sugerencias(request):
    """Localidades de una provincia que coincidan con `q`.

    No es un catálogo cerrado: esta lista es solo de sugerencias, el campo
    Localidad en los formularios sigue aceptando texto libre.
    """
    provincia_id = request.GET.get('provincia_id', '').strip()
    q = request.GET.get('q', '').strip()

    if not provincia_id:
        return JsonResponse({'resultados': [], 'mensaje': 'Elegí primero una provincia.'})

    qs = Localidad.objects.filter(provincia_id=provincia_id)
    if q:
        qs = qs.filter(nombre__icontains=q)
    # Los nombres que empiezan con lo tipeado van primero (ej: "mer" -> "Merlo"
    # antes que "Villa Mercedes"), y dentro de cada grupo, orden alfabético.
    localidades = list(qs.order_by('nombre').values('id', 'nombre', 'departamento'))
    if q:
        q_lower = q.lower()
        localidades.sort(key=lambda loc: not loc['nombre'].lower().startswith(q_lower))
    return JsonResponse({'resultados': localidades[:MAX_SUGERENCIAS]})


def distritos_sugerencias(request):
    """Barrios/distritos ya cargados en el sitio (propiedades y publicaciones
    de compañero) que coincidan con `q`, opcionalmente acotados a `ciudad`.

    Sin catálogo fijo: es un campo todavía más flexible que Localidad, las
    sugerencias solo existen si ya hay datos cargados con ese texto.
    """
    # Import diferido para evitar dependencias circulares entre apps a nivel
    # de módulo (ubicaciones no debe importar otros modelos al cargarse).
    from propiedades.models import Propiedad
    from usuarios.models import PublicacionCompanero

    q = request.GET.get('q', '').strip()
    ciudad = request.GET.get('ciudad', '').strip()

    if len(q) < 1:
        return JsonResponse({'resultados': []})

    conteo = {}

    def acumular(queryset, campo_ciudad):
        filtros = Q(distrito__icontains=q)
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
