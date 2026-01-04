from django.core.management.base import BaseCommand
from propiedades.models import Propiedad
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea 3 propiedades de ejemplo destacadas'

    def handle(self, *args, **kwargs):
        # Obtener o crear un usuario propietario
        propietario = Usuario.objects.filter(tipo='propietario').first()
        if not propietario:
            propietario = Usuario.objects.create_user(
                username='propietario_demo',
                email='propietario@demo.com',
                password='demo123',
                tipo='propietario',
                nombre='Juan',
                apellido='Pérez'
            )
            self.stdout.write(self.style.SUCCESS(f'Usuario propietario creado: {propietario.username}'))

        # Crear 3 propiedades destacadas
        propiedades_data = [
            {
                'titulo': 'Hermoso Departamento en San Isidro',
                'descripcion': 'Acogedor departamento de 2 habitaciones con vista al parque. Totalmente amoblado, incluye cocina equipada, sala amplia y 2 baños completos. Excelente ubicación cerca de centros comerciales y transporte público.',
                'tipo': 'departamento',
                'precio': 1200,
                'ciudad': 'Lima',
                'distrito': 'San Isidro',
                'direccion': 'Av. República de Panamá 3452',
                'area': 85,
                'habitaciones': 2,
                'banos': 2,
                'estacionamiento': True,
                'amoblado': True,
                'mascotas': False,
                'destacada': True
            },
            {
                'titulo': 'Casa Espaciosa en Miraflores',
                'descripcion': 'Moderna casa de 3 pisos con jardín privado. Cuenta con 4 habitaciones, 3 baños, cocina amplia, sala y comedor espacioso. Garage para 2 autos. Perfecta para familias.',
                'tipo': 'casa',
                'precio': 2500,
                'ciudad': 'Lima',
                'distrito': 'Miraflores',
                'direccion': 'Calle Los Pinos 567',
                'area': 180,
                'habitaciones': 4,
                'banos': 3,
                'estacionamiento': True,
                'amoblado': False,
                'mascotas': True,
                'destacada': True
            },
            {
                'titulo': 'Cuarto Confortable en Barranco',
                'descripcion': 'Habitación acogedora en zona tranquila y bohemia de Barranco. Baño privado, escritorio y closet incluidos. Internet de alta velocidad. Ideal para estudiantes o profesionales jóvenes.',
                'tipo': 'cuarto',
                'precio': 450,
                'ciudad': 'Lima',
                'distrito': 'Barranco',
                'direccion': 'Jr. Colina 234',
                'area': 25,
                'habitaciones': 1,
                'banos': 1,
                'estacionamiento': False,
                'amoblado': True,
                'mascotas': False,
                'destacada': True
            }
        ]

        for prop_data in propiedades_data:
            propiedad = Propiedad.objects.create(propietario=propietario, **prop_data)
            self.stdout.write(self.style.SUCCESS(f'✓ Propiedad creada: {propiedad.titulo}'))

        self.stdout.write(self.style.SUCCESS('\n¡3 propiedades destacadas creadas exitosamente!'))
