from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""
    TIPO_CHOICES = [
        ('usuario', 'Usuario'),
        ('propietario', 'Propietario'),
    ]
    
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='usuario')
    telefono = models.CharField(max_length=15, blank=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
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
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    verificado = models.BooleanField(default=False)
    puntuacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_valoraciones = models.IntegerField(default=0)
    
    # Nuevos campos para perfil progresivo
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, blank=True, null=True)
    objetivo_principal = models.CharField(max_length=30, choices=OBJETIVO_CHOICES, blank=True, null=True)
    perfil_completo = models.BooleanField(default=False)
    
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
        """Verifica si el perfil está completo"""
        return self.porcentaje_completado() == 100
    
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
