"""
Script para migrar datos de PerfilBusqueda a Perfil unificado
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Proyecto_BuscoTecho.settings')
django.setup()

from usuarios.models import Usuario, Perfil, PerfilBusqueda

def migrar_perfiles():
    """Migra los datos de PerfilBusqueda al modelo Perfil unificado"""
    perfiles_migrados = 0
    
    for perfil_busqueda in PerfilBusqueda.objects.all():
        usuario = perfil_busqueda.usuario
        perfil = usuario.perfil
        
        # Copiar todos los campos
        perfil.situacion_actual = perfil_busqueda.situacion_actual
        perfil.edad = perfil_busqueda.edad
        perfil.genero = perfil_busqueda.genero
        perfil.situacion_laboral = perfil_busqueda.situacion_laboral
        perfil.universidad = perfil_busqueda.universidad
        perfil.modalidad_estudio = perfil_busqueda.modalidad_estudio
        perfil.empresa_rubro = perfil_busqueda.empresa_rubro
        perfil.modalidad_trabajo = perfil_busqueda.modalidad_trabajo
        perfil.habitos_vicios = perfil_busqueda.habitos_vicios
        perfil.mascotas_tags = perfil_busqueda.mascotas_tags
        perfil.convivencia_limpieza = perfil_busqueda.convivencia_limpieza
        perfil.horarios_trabajo = perfil_busqueda.horarios_trabajo
        perfil.comida_social = perfil_busqueda.comida_social
        
        perfil.save()
        perfiles_migrados += 1
        print(f'✓ Migrado perfil de {usuario.username}')
    
    print(f'\n✅ Total de perfiles migrados: {perfiles_migrados}')

if __name__ == '__main__':
    print('Iniciando migración de perfiles de búsqueda...\n')
    migrar_perfiles()
    print('\n¡Migración completada!')
