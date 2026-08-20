from django.db import models


class Provincia(models.Model):
    """Las 24 jurisdicciones de la Argentina (23 provincias + CABA).

    Se usa el id oficial del Georef (Ministerio del Interior) como PK para
    que reimportar los datos sea idempotente (mismo id -> mismo registro).
    """
    id = models.CharField(max_length=2, primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'

    def __str__(self):
        return self.nombre


class Localidad(models.Model):
    """Localidades censales del Georef, para sugerir "Localidad" según la
    Provincia elegida. No es un campo cerrado: Propiedad.ciudad y
    PublicacionCompanero.ciudad siguen siendo texto libre, esta tabla solo
    alimenta las sugerencias.

    `departamento` (partido/municipio) se guarda solo como dato interno de
    contexto -no es un campo que el usuario vea ni complete- para poder
    reimportar/depurar y, a futuro, desambiguar localidades homónimas dentro
    de una misma provincia.
    """
    id = models.CharField(max_length=20, primary_key=True)
    nombre = models.CharField(max_length=150)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='localidades')
    departamento = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Localidad'
        verbose_name_plural = 'Localidades'
        indexes = [
            models.Index(fields=['provincia', 'nombre']),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.provincia.nombre})'
