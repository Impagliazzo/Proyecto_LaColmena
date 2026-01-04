from django.db import models
from django.conf import settings

class Notificacion(models.Model):
    """Notificaciones para usuarios"""
    TIPO_CHOICES = [
        ('favorito', 'Favorito actualizado'),
        ('contacto', 'Nueva solicitud de contacto'),
        ('suscripcion', 'Recordatorio de suscripción'),
        ('valoracion', 'Nueva valoración'),
        ('sistema', 'Notificación del sistema'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    url = models.CharField(max_length=255, blank=True)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f'{self.usuario.username} - {self.titulo}'
    
    def marcar_como_leida(self):
        if not self.leida:
            from django.utils import timezone
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save()
