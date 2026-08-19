from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""
    TIPO_CHOICES = [
        ('usuario', 'Usuario'),
        ('propietario', 'Propietario'),
    ]
    
    TIPO_AVATAR_CHOICES = [
        ('foto', 'Foto'),
        ('icono', 'Icono'),
    ]
    
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='usuario')
    telefono = models.CharField(max_length=15, blank=True)
    telefono_validado = models.BooleanField(default=False)
    email_validado = models.BooleanField(default=False)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    
    # Campos para avatares con iconos
    tipo_avatar = models.CharField(max_length=10, choices=TIPO_AVATAR_CHOICES, default='foto')
    icono_avatar = models.CharField(max_length=10, blank=True, help_text='Emoji o código del icono')
    
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.TextField(blank=True)
    biografia = models.TextField(blank=True, max_length=500)
    recibir_notificaciones = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __str__(self):
        return self.username
    
    def es_propietario(self):
        return self.tipo == 'propietario'
    
    def convertir_a_propietario(self):
        """Convierte un usuario regular a propietario y le asigna el plan Gratis"""
        if self.tipo == 'usuario':
            self.tipo = 'propietario'
            self.save()
            
            # Asignar plan Gratis automáticamente
            from suscripciones.models import PlanSuscripcion, Suscripcion
            from django.utils import timezone
            
            plan_gratis = PlanSuscripcion.objects.filter(nombre='Gratis', activo=True).first()
            if plan_gratis and not Suscripcion.objects.filter(usuario=self, estado='activa').exists():
                Suscripcion.objects.create(
                    usuario=self,
                    plan=plan_gratis,
                    estado='activa',
                    fecha_inicio=timezone.now()
                )
    
    def notificaciones_no_leidas(self):
        """Retorna el número de notificaciones no leídas"""
        return self.notificaciones.filter(leida=False).count()
    
    def tiene_validaciones_completas(self):
        """Verifica si el usuario tiene teléfono y email validados"""
        return self.telefono_validado and self.email_validado
    
    def necesita_validaciones(self):
        """Verifica si el usuario necesita completar validaciones"""
        return not self.tiene_validaciones_completas()


class Perfil(models.Model):
    """Información adicional del perfil del usuario"""
    
    TIPO_USUARIO_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('dueno_directo', 'Dueño Directo'),
        ('inmobiliaria', 'Inmobiliaria'),
        ('interesado', 'Interesado en Alquilar/Comprar'),
    ]
    
    OBJETIVO_CHOICES = [
        ('buscar_alquiler', 'Buscar un lugar para alquilar'),
        ('buscar_compra', 'Buscar un lugar para comprar'),
        ('publicar_propiedad', 'Publicar mi propiedad'),
        ('gestionar_propiedades', 'Gestionar varias propiedades'),
        ('solo_explorar', 'Solo estoy explorando'),
    ]
    
    SITUACION_ACTUAL_CHOICES = [
        ('tengo_lugar', 'Ya tengo un lugar y busco compañero/a'),
        ('busco_compartir', 'No tengo lugar, busco con quién compartir'),
    ]
    
    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir'),
    ]
    
    SITUACION_LABORAL_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('trabajador', 'Trabajador/a'),
        ('ambas', 'Estudiante y Trabajador/a'),
        ('otra', 'Otra'),
    ]
    
    MODALIDAD_ESTUDIO_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('hibrida', 'Híbrida'),
    ]
    
    MODALIDAD_TRABAJO_CHOICES = [
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('hibrido', 'Híbrido'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    verificado = models.BooleanField(default=False)
    puntuacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_valoraciones = models.IntegerField(default=0)
    
    # Nuevos campos para perfil progresivo
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, blank=True, null=True)
    objetivo_principal = models.CharField(max_length=30, choices=OBJETIVO_CHOICES, blank=True, null=True)
    perfil_completo = models.BooleanField(default=False)
    
    # --- CAMPOS INTEGRADOS DE BÚSQUEDA DE COMPAÑERO/A ---
    # 1. Situación actual
    situacion_actual = models.CharField(
        max_length=20,
        choices=SITUACION_ACTUAL_CHOICES,
        blank=True,
        null=True,
        verbose_name='Situación actual'
    )
    
    # Presentación personal para búsqueda de compañero/a
    presentacion = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Presentación personal',
        help_text='Contá un poco sobre vos y qué buscás en un compañero/a de vivienda (máx. 500 caracteres)'
    )
    
    # 2. Información personal básica
    edad = models.IntegerField(blank=True, null=True, verbose_name='Edad')
    genero = models.CharField(
        max_length=20,
        choices=GENERO_CHOICES,
        blank=True,
        null=True,
        verbose_name='Género'
    )
    
    # 3. Situación laboral/académica
    situacion_laboral = models.CharField(
        max_length=15,
        choices=SITUACION_LABORAL_CHOICES,
        blank=True,
        null=True,
        verbose_name='Situación laboral/académica'
    )
    
    # Campos condicionales para estudiantes
    universidad = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Universidad'
    )
    modalidad_estudio = models.CharField(
        max_length=15,
        choices=MODALIDAD_ESTUDIO_CHOICES,
        blank=True,
        verbose_name='Modalidad de estudio'
    )
    
    # Campos condicionales para trabajadores
    empresa_rubro = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Empresa o rubro'
    )
    modalidad_trabajo = models.CharField(
        max_length=15,
        choices=MODALIDAD_TRABAJO_CHOICES,
        blank=True,
        verbose_name='Modalidad de trabajo'
    )
    
    # 4. Hábitos y estilo de vida - Sistema de etiquetas por categorías
    habitos_vicios = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Hábitos y Vicios'
    )
    mascotas_tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Mascotas'
    )
    convivencia_limpieza = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Convivencia y Limpieza'
    )
    horarios_trabajo = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Horarios y Trabajo'
    )
    comida_social = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Comida y Social'
    )
    comida_social = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Comida y Social'
    )
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        
    def __str__(self):
        return f'Perfil de {self.usuario.username}'
    
    def porcentaje_completado(self):
        """Calcula el porcentaje de completitud del perfil"""
        campos_totales = 4
        campos_completos = 0
        
        # Datos básicos del usuario
        if self.usuario.first_name:
            campos_completos += 1
        if self.usuario.last_name:
            campos_completos += 1
        
        # Datos del perfil progresivo
        if self.tipo_usuario:
            campos_completos += 1
        if self.objetivo_principal:
            campos_completos += 1
        
        return int((campos_completos / campos_totales) * 100)
    
    def esta_completo(self):
        """Verifica si el perfil básico está completo"""
        return self.porcentaje_completado() == 100
    
    def perfil_busqueda_completo(self):
        """Verifica si el perfil de búsqueda está completo con todos los campos requeridos"""
        campos_obligatorios = [
            self.situacion_actual,
            self.edad,
            self.genero,
            self.situacion_laboral,
        ]
        
        # Verificar campos condicionales según situación laboral
        if self.situacion_laboral in ['estudiante', 'ambas']:
            if not self.universidad or not self.modalidad_estudio:
                return False
        
        if self.situacion_laboral in ['trabajador', 'ambas']:
            if not self.empresa_rubro or not self.modalidad_trabajo:
                return False
        
        # Verificar que todos los campos obligatorios estén completos
        return all(campo for campo in campos_obligatorios)
    
    def actualizar_estado_completitud(self):
        """Actualiza el estado de completitud del perfil"""
        self.perfil_completo = self.esta_completo()
        self.save()
    
    def actualizar_puntuacion(self):
        """Actualiza la puntuación promedio del propietario basado en todas sus valoraciones"""
        from propiedades.models import Valoracion
        # Obtener todas las valoraciones de las propiedades del usuario
        valoraciones = Valoracion.objects.filter(propiedad__propietario=self.usuario)
        
        if valoraciones.exists():
            # Calcular promedio de valoraciones del propietario
            total = sum(v.promedio_propietario() for v in valoraciones)
            self.puntuacion_promedio = total / valoraciones.count()
            self.total_valoraciones = valoraciones.count()
        else:
            self.puntuacion_promedio = 0
            self.total_valoraciones = 0
        
        self.save()
    
    def get_etiquetas_dict(self):
        """Mapeo de valores internos a etiquetas hashtag para mostrar"""
        return {
            # Hábitos y Vicios
            'fumador': '#Fumador',
            'vaper': '#Vaper',
            'drink_friendly': '#DrinkFriendly',
            'abstemio': '#Abstemio',
            'ruidoso_pero_majo': '#RuidosoPeroMajo',
            'modo_silencio': '#ModoSilencio',
            'gamer': '#Gamer',
            # Mascotas
            'dog_lover': '#DogLover',
            'cat_lover': '#CatLover',
            'mascota_exotica': '#MascotaExotica',
            'pet_friendly': '#PetFriendly',
            # Convivencia y Limpieza
            'limpio': '#Limpio',
            'manana_lo_lavo': '#MañanaLoLavo',
            'caos_bajo_control': '#CaosBajoControl',
            'team_limpieza': '#TeamLimpieza',
            'sin_filtros': '#SinFiltros',
            'nudista_light': '#NudistaLight',
            # Horarios y Trabajo
            'home_office': '#HomeOffice',
            'casi_nunca_estoy': '#CasiNuncaEstoy',
            'night_owl': '#NightOwl',
            'early_bird': '#EarlyBird',
            'ronco_un_poco': '#RoncoUnPoco',
            # Comida y Social
            'chef_en_casa': '#ChefEnCasa',
            'rey_del_delivery': '#ReyDelDelivery',
            'vegan_vibes': '#VeganVibes',
            'casa_social': '#CasaSocial',
            'full_privacidad': '#FullPrivacidad',
            'pareja_visitante': '#ParejaVisitante',
        }
    
    def get_etiquetas_descripciones(self):
        """Descripciones de etiquetas para tooltips"""
        return {
            # Hábitos y Vicios
            'fumador': 'A esta persona le gusta fumar',
            'vaper': 'Utiliza vaper o cigarrillos electrónicos',
            'drink_friendly': 'Le gusta tomar alcohol socialmente',
            'abstemio': 'No consume alcohol',
            'ruidoso_pero_majo': 'Puede ser ruidoso pero de buen rollo',
            'modo_silencio': 'Prefiere ambientes tranquilos y silenciosos',
            'gamer': 'Le gusta jugar videojuegos',
            # Mascotas
            'dog_lover': 'Ama a los perros',
            'cat_lover': 'Ama a los gatos',
            'mascota_exotica': 'Tiene mascotas exóticas (reptiles, aves, etc.)',
            'pet_friendly': 'Acepta mascotas en casa',
            # Convivencia y Limpieza
            'limpio': 'Persona ordenada y limpia',
            'manana_lo_lavo': 'Deja las tareas de limpieza para después',
            'caos_bajo_control': 'Un poco desordenado pero organizado',
            'team_limpieza': 'Fan del orden y la limpieza',
            'sin_filtros': 'Es directo y sincero al comunicarse',
            'nudista_light': 'Le gusta andar ligero de ropa en casa',
            # Horarios y Trabajo
            'home_office': 'Trabaja desde casa',
            'casi_nunca_estoy': 'Pasa poco tiempo en casa',
            'night_owl': 'Es nocturno, se acuesta tarde',
            'early_bird': 'Madrugador, se levanta temprano',
            'ronco_un_poco': 'Puede roncar al dormir',
            # Comida y Social
            'chef_en_casa': 'Le gusta cocinar',
            'rey_del_delivery': 'Prefiere pedir comida a domicilio',
            'vegan_vibes': 'Dieta vegana o vegetariana',
            'casa_social': 'Le gusta recibir visitas en casa',
            'full_privacidad': 'Prefiere privacidad, pocas visitas',
            'pareja_visitante': 'Su pareja le visita frecuentemente',
        }
    
    def get_todas_etiquetas(self):
        """Retorna todas las etiquetas seleccionadas como hashtags"""
        etiquetas_dict = self.get_etiquetas_dict()
        todas = []
        
        # Procesar cada categoría
        for tag in (self.habitos_vicios or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        for tag in (self.mascotas_tags or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        for tag in (self.convivencia_limpieza or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        for tag in (self.horarios_trabajo or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        for tag in (self.comida_social or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        return todas
    
    def get_todas_etiquetas_con_descripciones(self):
        """Retorna todas las etiquetas con sus descripciones para tooltips"""
        etiquetas_dict = self.get_etiquetas_dict()
        descripciones = self.get_etiquetas_descripciones()
        todas = []
        
        # Procesar cada categoría
        for tag in (self.habitos_vicios or []):
            if tag in etiquetas_dict:
                todas.append({
                    'tag': etiquetas_dict[tag],
                    'descripcion': descripciones.get(tag, '')
                })
        
        for tag in (self.mascotas_tags or []):
            if tag in etiquetas_dict:
                todas.append({
                    'tag': etiquetas_dict[tag],
                    'descripcion': descripciones.get(tag, '')
                })
        
        for tag in (self.convivencia_limpieza or []):
            if tag in etiquetas_dict:
                todas.append({
                    'tag': etiquetas_dict[tag],
                    'descripcion': descripciones.get(tag, '')
                })
        
        for tag in (self.horarios_trabajo or []):
            if tag in etiquetas_dict:
                todas.append({
                    'tag': etiquetas_dict[tag],
                    'descripcion': descripciones.get(tag, '')
                })
        
        for tag in (self.comida_social or []):
            if tag in etiquetas_dict:
                todas.append({
                    'tag': etiquetas_dict[tag],
                    'descripcion': descripciones.get(tag, '')
                })
        
        return todas
    
    def get_etiquetas_por_categoria(self):
        """Retorna las etiquetas organizadas por categorías con descripciones"""
        etiquetas_dict = self.get_etiquetas_dict()
        descripciones = self.get_etiquetas_descripciones()
        
        def format_tags(tags_list):
            """Convierte lista de tags en lista de diccionarios con tag y descripción"""
            return [
                {
                    'tag': etiquetas_dict.get(tag, f'#{tag}'),
                    'descripcion': descripciones.get(tag, '')
                }
                for tag in (tags_list or [])
            ]
        
        return {
            'habitos_vicios': format_tags(self.habitos_vicios),
            'mascotas': format_tags(self.mascotas_tags),
            'convivencia_limpieza': format_tags(self.convivencia_limpieza),
            'horarios_trabajo': format_tags(self.horarios_trabajo),
            'comida_social': format_tags(self.comida_social),
        }


# MODELO OBSOLETO - Ahora todos los campos están integrados en Perfil
# Mantener por compatibilidad con migraciones existentes, pero no usar
class PerfilBusqueda(models.Model):
    """Perfil extendido para el sistema de búsqueda de compañero/a de vivienda"""
    
    SITUACION_ACTUAL_CHOICES = [
        ('tengo_lugar', 'Ya tengo un lugar y busco compañero/a'),
        ('busco_compartir', 'No tengo lugar, busco con quién compartir'),
    ]
    
    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('prefiero_no_decir', 'Prefiero no decir'),
    ]
    
    SITUACION_LABORAL_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('trabajador', 'Trabajador/a'),
        ('ambas', 'Estudiante y Trabajador/a'),
        ('otra', 'Otra'),
    ]
    
    MODALIDAD_ESTUDIO_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('hibrida', 'Híbrida'),
    ]
    
    MODALIDAD_TRABAJO_CHOICES = [
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('hibrido', 'Híbrido'),
    ]
    
    # Relación con Usuario
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_busqueda')
    
    # 1. Situación actual
    situacion_actual = models.CharField(
        max_length=20,
        choices=SITUACION_ACTUAL_CHOICES,
        verbose_name='Situación actual'
    )
    
    # 2. Información personal básica
    edad = models.IntegerField(verbose_name='Edad')
    genero = models.CharField(
        max_length=20,
        choices=GENERO_CHOICES,
        verbose_name='Género'
    )
    
    # 3. Situación laboral/académica
    situacion_laboral = models.CharField(
        max_length=15,
        choices=SITUACION_LABORAL_CHOICES,
        verbose_name='Situación laboral/académica'
    )
    
    # Campos condicionales para estudiantes
    universidad = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Universidad'
    )
    modalidad_estudio = models.CharField(
        max_length=15,
        choices=MODALIDAD_ESTUDIO_CHOICES,
        blank=True,
        verbose_name='Modalidad de estudio'
    )
    
    # Campos condicionales para trabajadores
    empresa_rubro = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Empresa o rubro'
    )
    modalidad_trabajo = models.CharField(
        max_length=15,
        choices=MODALIDAD_TRABAJO_CHOICES,
        blank=True,
        verbose_name='Modalidad de trabajo'
    )
    
    # 4. Hábitos y estilo de vida - Sistema de etiquetas por categorías
    # Almacenamos las etiquetas seleccionadas como listas en formato JSON
    habitos_vicios = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Hábitos y Vicios'
    )
    mascotas_tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Mascotas'
    )
    convivencia_limpieza = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Convivencia y Limpieza'
    )
    horarios_trabajo = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Horarios y Trabajo'
    )
    comida_social = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Comida y Social'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Búsqueda'
        verbose_name_plural = 'Perfiles de Búsqueda'
    
    def __str__(self):
        return f'Perfil de búsqueda de {self.usuario.username}'
    
    def esta_completo(self):
        """Verifica si el perfil está completo con todos los campos requeridos"""
        campos_obligatorios = [
            self.situacion_actual,
            self.edad,
            self.genero,
            self.situacion_laboral,
        ]
        
        # Verificar campos condicionales según situación laboral
        if self.situacion_laboral in ['estudiante', 'ambas']:
            if not self.universidad or not self.modalidad_estudio:
                return False
        
        if self.situacion_laboral in ['trabajador', 'ambas']:
            if not self.empresa_rubro or not self.modalidad_trabajo:
                return False
        
        # Verificar que todos los campos obligatorios estén completos
        return all(campo for campo in campos_obligatorios)
    
    def get_etiquetas_dict(self):
        """Mapeo de valores internos a etiquetas hashtag para mostrar"""
        return {
            # Hábitos y Vicios
            'fumador': '#Fumador',
            'vaper': '#Vaper',
            'drink_friendly': '#DrinkFriendly',
            'abstemio': '#Abstemio',
            'ruidoso_pero_majo': '#RuidosoPeroMajo',
            'modo_silencio': '#ModoSilencio',
            'gamer': '#Gamer',
            # Mascotas
            'dog_lover': '#DogLover',
            'cat_lover': '#CatLover',
            'mascota_exotica': '#MascotaExotica',
            'pet_friendly': '#PetFriendly',
            # Convivencia y Limpieza
            'limpio': '#Limpio',
            'manana_lo_lavo': '#MañanaLoLavo',
            'caos_bajo_control': '#CaosBajoControl',
            'team_limpieza': '#TeamLimpieza',
            'sin_filtros': '#SinFiltros',
            'nudista_light': '#NudistaLight',
            # Horarios y Trabajo
            'home_office': '#HomeOffice',
            'casi_nunca_estoy': '#CasiNuncaEstoy',
            'night_owl': '#NightOwl',
            'early_bird': '#EarlyBird',
            'ronco_un_poco': '#RoncoUnPoco',
            # Comida y Social
            'chef_en_casa': '#ChefEnCasa',
            'rey_del_delivery': '#ReyDelDelivery',
            'vegan_vibes': '#VeganVibes',
            'casa_social': '#CasaSocial',
            'full_privacidad': '#FullPrivacidad',
            'pareja_visitante': '#ParejaVisitante',
        }
    
    def get_todas_etiquetas(self):
        """Retorna todas las etiquetas seleccionadas como hashtags"""
        etiquetas_dict = self.get_etiquetas_dict()
        todas = []
        
        # Procesar cada categoría
        for tag in (self.habitos_vicios or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        for tag in (self.mascotas_tags or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        for tag in (self.convivencia_limpieza or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        for tag in (self.horarios_trabajo or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        for tag in (self.comida_social or []):
            if tag in etiquetas_dict:
                todas.append(etiquetas_dict[tag])
        
        return todas
    
    def get_etiquetas_por_categoria(self):
        """Retorna las etiquetas organizadas por categorías"""
        etiquetas_dict = self.get_etiquetas_dict()
        
        return {
            'habitos_vicios': [etiquetas_dict.get(tag, f'#{tag}') for tag in (self.habitos_vicios or [])],
            'mascotas': [etiquetas_dict.get(tag, f'#{tag}') for tag in (self.mascotas_tags or [])],
            'convivencia_limpieza': [etiquetas_dict.get(tag, f'#{tag}') for tag in (self.convivencia_limpieza or [])],
            'horarios_trabajo': [etiquetas_dict.get(tag, f'#{tag}') for tag in (self.horarios_trabajo or [])],
            'comida_social': [etiquetas_dict.get(tag, f'#{tag}') for tag in (self.comida_social or [])],
        }


class PublicacionCompanero(models.Model):
    """Publicación de departamento para buscar compañero/a de piso.
    Diferente de Propiedad - esto NO es para alquiler/venta, sino para compartir vivienda"""
    
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('completada', 'Completada - Ya encontré compañero/a'),
        ('inactiva', 'Inactiva'),
    ]
    
    # Relación con el usuario
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='publicacion_companero',
        help_text='Usuario que tiene lugar y busca compañero/a'
    )
    
    # Información del departamento
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título de la publicación',
        help_text='Ej: Busco compañero/a para compartir depto 2 ambientes en Palermo'
    )
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Contá más sobre el departamento y qué buscás en un compañero/a'
    )
    
    # Ubicación
    provincia = models.CharField(max_length=100, default='Buenos Aires')
    ciudad = models.CharField(max_length=100, verbose_name='Ciudad')
    distrito = models.CharField(max_length=100, verbose_name='Barrio/Distrito')
    direccion = models.CharField(
        max_length=255, 
        verbose_name='Dirección aproximada',
        help_text='No es necesario dar la dirección exacta por seguridad'
    )
    
    # Características del espacio
    habitaciones_totales = models.IntegerField(
        default=1,
        verbose_name='Habitaciones totales',
        help_text='Habitaciones totales del departamento'
    )
    habitaciones_disponibles = models.IntegerField(
        default=1,
        verbose_name='Habitaciones disponibles',
        help_text='Habitaciones disponibles para el/la compañero/a'
    )
    banos = models.IntegerField(default=1, verbose_name='Baños')
    amoblado = models.BooleanField(default=False, verbose_name='Habitación amoblada')
    
    # Comodidades
    balcon = models.BooleanField(default=False, verbose_name='Tiene balcón o terraza')
    cocina = models.BooleanField(default=True, verbose_name='Cocina equipada')
    wifi = models.BooleanField(default=True, verbose_name='WiFi')
    lavarropas = models.BooleanField(default=False, verbose_name='Lavarropas')
    aire_acondicionado = models.BooleanField(default=False, verbose_name='Aire acondicionado')
    calefaccion = models.BooleanField(default=False, verbose_name='Calefacción')
    
    # Información económica
    precio_mensual = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Precio mensual por persona',
        help_text='Precio que pagaría cada persona por mes'
    )
    expensas_incluidas = models.BooleanField(
        default=False,
        verbose_name='Expensas incluidas en el precio'
    )
    servicios_incluidos = models.BooleanField(
        default=False,
        verbose_name='Servicios incluidos',
        help_text='Luz, gas, agua, internet'
    )
    
    # Preferencias para el compañero/a
    preferencia_genero = models.CharField(
        max_length=20,
        choices=[
            ('indiferente', 'Indiferente'),
            ('masculino', 'Preferentemente masculino'),
            ('femenino', 'Preferentemente femenino'),
        ],
        default='indiferente',
        verbose_name='Preferencia de género'
    )
    acepta_mascotas = models.BooleanField(
        default=False,
        verbose_name='Acepta mascotas'
    )
    fumador_acepto = models.BooleanField(
        default=False,
        verbose_name='Acepta fumadores'
    )
    
    # Estado y metadatos
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='activa',
        verbose_name='Estado de la publicación'
    )
    fecha_disponibilidad = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de disponibilidad',
        help_text='¿Desde cuándo está disponible?'
    )
    vistas = models.IntegerField(default=0, verbose_name='Vistas')
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Publicación de Compañero/a'
        verbose_name_plural = 'Publicaciones de Compañero/a'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'{self.titulo} - {self.usuario.username}'
    
    def incrementar_vistas(self):
        """Incrementa el contador de vistas"""
        self.vistas += 1
        self.save(update_fields=['vistas'])
    
    def get_precio_display(self):
        """Retorna el precio formateado"""
        precio = f'${self.precio_mensual:,.0f}'
        if self.expensas_incluidas and self.servicios_incluidos:
            return f'{precio} (todo incluido)'
        elif self.expensas_incluidas:
            return f'{precio} (expensas incluidas)'
        elif self.servicios_incluidos:
            return f'{precio} (servicios incluidos)'
        return f'{precio}/mes'

    @property
    def imagen_principal(self):
        """Retorna la primera imagen o None"""
        return self.imagenes.first()


class ImagenPublicacionCompanero(models.Model):
    """Imágenes de la publicación de compañero/a"""
    publicacion = models.ForeignKey(
        PublicacionCompanero,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(
        upload_to='publicaciones_companero/',
        verbose_name='Imagen'
    )
    orden = models.IntegerField(default=0, verbose_name='Orden de visualización')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Imagen de Publicación'
        verbose_name_plural = 'Imágenes de Publicación'
        ordering = ['orden', 'fecha_subida']
    
    def __str__(self):
        return f'Imagen {self.orden} de {self.publicacion.titulo}'
