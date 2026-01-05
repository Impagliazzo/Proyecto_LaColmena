# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator

class Categoria(models.Model):
    """Categorías de propiedades"""
    nombre = models.CharField(max_length=50, unique=True)
    icono = models.CharField(max_length=50, blank=True)  # Clase de icono
    color = models.CharField(max_length=20, default='blue')
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']
        
    def __str__(self):
        return self.nombre


class Propiedad(models.Model):
    """Modelo de propiedad/inmueble"""
    TIPO_CHOICES = [
        ('departamento', 'Departamento'),
        ('casa', 'Casa'),
        ('cuarto', 'Cuarto'),
        ('local', 'Local Comercial'),
        ('terreno', 'Terreno'),
        ('oficina', 'Oficina'),
    ]
    
    OPERACION_CHOICES = [
        ('alquiler', 'Alquiler'),
        ('venta', 'Venta'),
    ]
    
    TIPO_CONTACTO_CHOICES = [
        ('dueno', 'Dueño Directo'),
        ('inmobiliaria', 'Inmobiliaria'),
    ]
    
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('suspendida', 'Suspendida'),
        ('alquilada', 'Alquilada'),
        ('inactiva', 'Inactiva'),
    ]
    
    # Relaciones
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publicaciones')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='propiedades')
    
    # Información básica
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    operacion = models.CharField(max_length=20, choices=OPERACION_CHOICES, default='alquiler')
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    incluye_expensas = models.BooleanField(default=False, help_text='¿El precio incluye gastos de expensas?')
    tipo_contacto = models.CharField(max_length=20, choices=TIPO_CONTACTO_CHOICES, default='dueno')
    
    # Ubicación
    ciudad = models.CharField(max_length=100)
    distrito = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Características
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text='Área en m²')
    habitaciones = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    banos = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    estacionamiento = models.BooleanField(default=False)
    amoblado = models.BooleanField(default=False)
    mascotas = models.BooleanField(default=False)
    
    # Inmueble
    piso = models.IntegerField(null=True, blank=True, help_text='Número de piso', validators=[MinValueValidator(-5)])
    
    # Comodidades
    balcon = models.BooleanField(default=False, help_text='Tiene balcón o terraza')
    patio = models.BooleanField(default=False, help_text='Tiene patio o jardín')
    parrilla = models.BooleanField(default=False, help_text='Tiene parrilla')
    aire_acondicionado = models.BooleanField(default=False)
    calefaccion = models.BooleanField(default=False)
    ascensor = models.BooleanField(default=False)
    
    # Edificio
    seguridad = models.BooleanField(default=False, help_text='Tiene seguridad o portero')
    amenities = models.BooleanField(default=False, help_text='Tiene amenities (pileta, gym, SUM)')
    accesibilidad = models.BooleanField(default=False, help_text='Apto para movilidad reducida')
    
    # Estado y estadísticas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    motivo_suspension = models.CharField(max_length=255, blank=True, help_text='Motivo por el cual la propiedad fue suspendida')
    vistas = models.IntegerField(default=0)
    destacada = models.BooleanField(default=False)
    especial_estudiantes = models.BooleanField(default=False, help_text='Propiedad especial para estudiantes')
    
    # Fechas
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Propiedad'
        verbose_name_plural = 'Propiedades'
        ordering = ['-fecha_publicacion']
        
    def __str__(self):
        return self.titulo
    
    def incrementar_vistas(self):
        """Incrementa el contador de vistas"""
        self.vistas += 1
        self.save(update_fields=['vistas'])
    
    @property
    def imagen_principal(self):
        """Retorna la primera imagen o None"""
        return self.imagenes.first()
    
    def puntuacion_promedio(self):
        """Calcula la puntuación promedio de las valoraciones"""
        valoraciones = self.valoraciones.all()
        if valoraciones:
            return sum(v.puntuacion for v in valoraciones) / len(valoraciones)
    
    def tiene_destacado_activo(self):
        """Verifica si la propiedad tiene un destacado activo"""
        from django.utils import timezone
        return self.destacados.filter(
            activo=True,
            fecha_fin__gt=timezone.now()
        ).exists()
    
    def obtener_destacado_activo(self):
        """Obtiene el destacado activo actual de la propiedad"""
        from django.utils import timezone
        return self.destacados.filter(
            activo=True,
            fecha_fin__gt=timezone.now()
        ).first()
        return 0
    
    def total_valoraciones(self):
        """Retorna el total de valoraciones"""
        return self.valoraciones.count()


class ImagenPropiedad(models.Model):
    """Imágenes de una propiedad"""
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='propiedades/')
    orden = models.IntegerField(default=0)
    es_principal = models.BooleanField(default=False)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Imagen de propiedad'
        verbose_name_plural = 'Imágenes de propiedades'
        ordering = ['orden', '-es_principal']
        
    def __str__(self):
        return f'Imagen {self.orden} de {self.propiedad.titulo}'


class Favorito(models.Model):
    """Propiedades marcadas como favoritas por usuarios"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favoritos')
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='favoritos')
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together = ['usuario', 'propiedad']
        ordering = ['-fecha_agregado']
        
    def __str__(self):
        return f'{self.usuario.username} - {self.propiedad.titulo}'


class Valoracion(models.Model):
    """Valoraciones de propiedades y propietarios"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='valoraciones')
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='valoraciones')
    
    # Valoración de la PUBLICACIÓN (1-5 estrellas cada una)
    # Estas valoraciones solo se habilitan 24h después de la respuesta del propietario
    claridad_informacion = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Claridad de la información')
    coincidencia_fotos = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Coincidencia fotos/realidad')
    ubicacion_correcta = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Ubicación correcta')
    
    # Valoración del PROPIETARIO (1-5 estrellas cada una)
    tiempo_respuesta = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Tiempo de respuesta')
    trato = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Trato y predisposición')
    confiabilidad = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='Confiabilidad')
    
    # Comentarios opcionales
    comentario = models.TextField(blank=True)
    fecha_valoracion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_edicion = models.DateTimeField(auto_now=True)
    
    # Control de reportes
    reportada = models.BooleanField(default=False)
    total_reportes = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Valoración'
        verbose_name_plural = 'Valoraciones'
        unique_together = ['usuario', 'propiedad']
        ordering = ['-fecha_valoracion']
        
    def __str__(self):
        return f'{self.usuario.username} - {self.propiedad.titulo} - {self.promedio_total():.1f}⭐'
    
    def promedio_publicacion(self):
        """Promedio de valoración de la publicación (solo si tiene valores)"""
        campos = [self.claridad_informacion, self.coincidencia_fotos, self.ubicacion_correcta]
        valores = [v for v in campos if v is not None]
        if not valores:
            return None
        return sum(valores) / len(valores)
    
    def promedio_propietario(self):
        """Promedio de valoración del propietario"""
        return (self.tiempo_respuesta + self.trato + self.confiabilidad) / 3
    
    def promedio_total(self):
        """Promedio total de la valoración (solo propietario si no hay publicación)"""
        promedio_pub = self.promedio_publicacion()
        promedio_prop = self.promedio_propietario()
        
        if promedio_pub is None:
            return promedio_prop
        return (promedio_pub + promedio_prop) / 2
    
    def puede_editar(self):
        """Verifica si la valoración aún puede ser editada (30 días desde creación)"""
        from django.utils import timezone
        from datetime import timedelta
        dias_limite = 30
        return timezone.now() - self.fecha_valoracion < timedelta(days=dias_limite)


class ReporteValoracion(models.Model):
    """Reportes de valoraciones injustas o inapropiadas"""
    MOTIVO_CHOICES = [
        ('falsa', 'Información falsa'),
        ('ofensiva', 'Contenido ofensivo'),
        ('spam', 'Spam o irrelevante'),
        ('venganza', 'Valoración vengativa'),
        ('otro', 'Otro motivo'),
    ]
    
    valoracion = models.ForeignKey(Valoracion, on_delete=models.CASCADE, related_name='reportes')
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportes_realizados')
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES)
    descripcion = models.TextField()
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Reporte de Valoración'
        verbose_name_plural = 'Reportes de Valoraciones'
        unique_together = ['valoracion', 'reportado_por']
        ordering = ['-fecha_reporte']
        
    def __str__(self):
        return f'Reporte de {self.reportado_por.username} sobre valoración de {self.valoracion.propiedad.titulo}'


class Destacado(models.Model):
    """Gestión de propiedades destacadas con compra y prioridad"""
    TIPO_CHOICES = [
        ('premium', 'Premium'),
        ('normal', 'Normal'),
    ]
    
    DURACION_CHOICES = [
        (7, '7 días'),
        (15, '15 días'),
        (30, '30 días'),
    ]
    
    # Precios por duración para cada tipo
    PRECIOS = {
        'normal': {7: 29.90, 15: 49.90, 30: 79.90},
        'premium': {7: 59.90, 15: 99.90, 30: 149.90},
    }
    
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='destacados')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='normal')
    duracion_dias = models.IntegerField(choices=DURACION_CHOICES)
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    fecha_compra = models.DateTimeField(auto_now_add=True)
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Destacado'
        verbose_name_plural = 'Destacados'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['activo', 'fecha_fin']),
            models.Index(fields=['tipo', 'fecha_inicio']),
        ]
    
    def __str__(self):
        return f'{self.propiedad.titulo} - {self.get_tipo_display()} ({self.duracion_dias} días)'
    
    def esta_activo(self):
        """Verifica si el destacado está activo y vigente"""
        from django.utils import timezone
        return self.activo and self.fecha_fin > timezone.now()
    
    def dias_restantes(self):
        """Retorna días restantes del destacado"""
        from django.utils import timezone
        if self.esta_activo():
            return (self.fecha_fin - timezone.now()).days
        return 0
    
    @classmethod
    def get_precio(cls, tipo, duracion):
        """Obtiene el precio para un tipo y duración específicos"""
        return cls.PRECIOS.get(tipo, {}).get(duracion, 0)
    
    def calcular_prioridad(self):
        """
        Calcula la prioridad de la propiedad para el algoritmo de ordenamiento.
        Mayor número = mayor prioridad
        """
        from suscripciones.models import Suscripcion
        
        prioridad = 0
        
        # 1. Prioridad por Plan (más peso)
        suscripcion = Suscripcion.objects.filter(
            usuario=self.propiedad.propietario,
            estado='activa'
        ).first()
        
        if suscripcion and suscripcion.esta_activa():
            plan_nombre = suscripcion.plan.nombre
            if plan_nombre == 'Avanzado':
                prioridad += 1000
            elif plan_nombre == 'Intermedio':
                prioridad += 500
            elif plan_nombre == 'Básico':
                prioridad += 100
        
        # 2. Prioridad por Tipo de Destacado
        if self.tipo == 'premium':
            prioridad += 50
        else:
            prioridad += 25
        
        # 3. Prioridad por fecha de compra (más reciente = más prioridad)
        # Usamos timestamp en segundos para tener granularidad fina
        prioridad += int(self.fecha_compra.timestamp() / 1000)
        
        return prioridad
