import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from usuarios.models import Usuario, PublicacionCompanero
from decimal import Decimal

# Buscar un usuario que tenga situacion_actual = 'tengo_lugar'
usuarios = Usuario.objects.all()
print(f"Total usuarios: {usuarios.count()}")

for user in usuarios:
    if hasattr(user, 'perfil'):
        print(f"\nUsuario: {user.username}")
        print(f"  Situación actual: {user.perfil.situacion_actual}")
        print(f"  Perfil búsqueda completo: {user.perfil.perfil_busqueda_completo()}")
        
        if user.perfil.situacion_actual == 'tengo_lugar':
            print(f"\n✅ Usuario {user.username} tiene lugar! Intentando crear publicación...")
            
            # Intentar crear publicación
            try:
                pub, created = PublicacionCompanero.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'titulo': 'Departamento 2 ambientes en Palermo',
                        'descripcion': 'Busco compañero/a para compartir depto luminoso',
                        'provincia': 'Buenos Aires',
                        'ciudad': 'Ciudad de Buenos Aires',
                        'distrito': 'Palermo',
                        'direccion': 'Cerca de Av. Santa Fe',
                        'habitaciones_totales': 2,
                        'habitaciones_disponibles': 1,
                        'banos': 1,
                        'precio_mensual': Decimal('50000.00'),
                        'preferencia_genero': 'indiferente',
                    }
                )
                
                if created:
                    print(f"✅ Publicación creada exitosamente!")
                    print(f"   ID: {pub.id}")
                    print(f"   Título: {pub.titulo}")
                    print(f"   Precio: ${pub.precio_mensual}")
                else:
                    print(f"⚠️ Ya existía una publicación para este usuario")
                    print(f"   ID: {pub.id}")
                    print(f"   Título: {pub.titulo}")
                    print(f"   Precio: ${pub.precio_mensual}")
                    
            except Exception as e:
                print(f"❌ Error al crear publicación: {e}")
                import traceback
                traceback.print_exc()
            
            break
else:
    print("\n❌ No se encontró ningún usuario con situacion_actual='tengo_lugar'")
    print("   Necesitas primero completar el perfil de búsqueda de un usuario")
