from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

class PlanSuscripcion(models.Model):
    """Planes de suscripción para propietarios"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_dias = models.IntegerField(help_text='Duración en días')
    max_publicaciones = models.IntegerField(help_text='Número máximo de publicaciones activas')
    destacar_publicaciones = models.BooleanField(default=False)
    destacados_incluidos_mes = models.IntegerField(default=0, help_text='Número de destacados incluidos por mes')
    puede_comprar_destacados = models.BooleanField(default=False, help_text='¿Puede comprar destacados adicionales?')
    soporte_prioritario = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Plan de suscripción'
        verbose_name_plural = 'Planes de suscripción'
        ordering = ['orden', 'precio']
        
    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    """Suscripciones de usuarios"""
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suscripciones')
    plan = models.ForeignKey(PlanSuscripcion, on_delete=models.PROTECT, related_name='suscripciones')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='activa')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateTimeField()
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
    auto_renovar = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
        ordering = ['-fecha_inicio']
        
    def __str__(self):
        return f'{self.usuario.username} - {self.plan.nombre}'
    
    def save(self, *args, **kwargs):
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = timezone.now() + timedelta(days=self.plan.duracion_dias)
        super().save(*args, **kwargs)
    
    def esta_activa(self):
        return self.estado == 'activa' and self.fecha_vencimiento > timezone.now()
    
    def dias_restantes(self):
        if self.esta_activa():
            return (self.fecha_vencimiento - timezone.now()).days
        return 0
    
    def esta_por_vencer(self):
        """Retorna True si faltan 7 días o menos para vencer"""
        return self.esta_activa() and self.dias_restantes() <= 7


class Pago(models.Model):
    """Registro de pagos de suscripciones"""
    METODO_CHOICES = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('paypal', 'PayPal'),
        ('efectivo', 'Efectivo'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('rechazado', 'Rechazado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    referencia = models.CharField(max_length=100, blank=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']
        
    def __str__(self):
        return f'{self.suscripcion.usuario.username} - ${self.monto} - {self.estado}'
