import json
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ubicaciones.models import Localidad, Provincia

GEOREF_BASE = 'https://apis.datos.gob.ar/georef/api'
TIMEOUT = 20
PAGE_SIZE = 5000


class Command(BaseCommand):
    help = (
        'Importa provincias y localidades censales desde el Georef '
        '(Ministerio del Interior, apis.datos.gob.ar/georef) a las tablas '
        'propias de este proyecto. Re-ejecutable: actualiza los registros '
        'existentes en vez de duplicarlos.'
    )

    def _get(self, path, params):
        url = f'{GEOREF_BASE}/{path}?{urllib.parse.urlencode(params)}'
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
                return json.loads(resp.read())
        except Exception as exc:
            raise CommandError(f'No se pudo consultar el Georef ({url}): {exc}')

    def handle(self, *args, **options):
        self.stdout.write('Importando provincias...')
        data = self._get('provincias', {'campos': 'id,nombre', 'max': 30})
        provincias_creadas = 0
        with transaction.atomic():
            for p in data['provincias']:
                _, creada = Provincia.objects.update_or_create(
                    id=p['id'], defaults={'nombre': p['nombre']}
                )
                provincias_creadas += creada
        self.stdout.write(self.style.SUCCESS(
            f'  {len(data["provincias"])} provincias procesadas ({provincias_creadas} nuevas).'
        ))

        self.stdout.write('Importando localidades censales (puede tardar un minuto)...')
        inicio = 0
        total = None
        procesadas = 0
        nuevas = 0
        campos = 'id,nombre,provincia.id,provincia.nombre,departamento.nombre'
        while total is None or inicio < total:
            data = self._get('localidades-censales', {
                'campos': campos, 'max': PAGE_SIZE, 'inicio': inicio,
            })
            total = data['total']
            lote = data['localidades_censales']
            if not lote:
                break

            with transaction.atomic():
                for loc in lote:
                    provincia_id = loc['provincia']['id']
                    try:
                        provincia = Provincia.objects.get(pk=provincia_id)
                    except Provincia.DoesNotExist:
                        self.stderr.write(
                            f'  Localidad "{loc["nombre"]}" con provincia '
                            f'desconocida (id {provincia_id}), se omite.'
                        )
                        continue
                    _, creada = Localidad.objects.update_or_create(
                        id=loc['id'],
                        defaults={
                            'nombre': loc['nombre'],
                            'provincia': provincia,
                            'departamento': (loc.get('departamento') or {}).get('nombre') or '',
                        },
                    )
                    nuevas += creada
            procesadas += len(lote)
            inicio += len(lote)
            self.stdout.write(f'  {procesadas}/{total} procesadas...')

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {Provincia.objects.count()} provincias, '
            f'{Localidad.objects.count()} localidades ({nuevas} nuevas en esta corrida).'
        ))
