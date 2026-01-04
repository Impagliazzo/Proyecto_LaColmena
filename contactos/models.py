from django.db import models
from django.conf import settings
from propiedades.models import Propiedad

class SolicitudContacto(models.Model):
    """Solicitudes de contacto de usuarios a propietarios"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('contactado', 'Contactado'),
        ('rechazado', 'Rechazado'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_contacto')
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='solicitudes_contacto')
    mensaje = models.TextField()
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)  # Cuando el propietario responde
    
    class Meta:
        verbose_name = 'Solicitud de contacto'
        verbose_name_plural = 'Solicitudes de contacto'
        ordering = ['-fecha_solicitud']
        
    def __str__(self):
        return f'{self.usuario.username} - {self.propiedad.titulo}'
