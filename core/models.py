from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icono = models.CharField(max_length=50, blank=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Comercio(models.Model):

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('pendiente', 'Pendiente de verificación'),
    ]

    PLAN_CHOICES = [
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('premium', 'Premium'),
    ]

    # Información básica
    propietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comercios'
    )
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comercios'
    )

    # Contacto
    telefono = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    sitio_web = models.URLField(blank=True)

    # Ubicación (sin PostGIS por ahora — lat/lng simples)
    direccion = models.CharField(max_length=300, blank=True)
    ciudad = models.CharField(max_length=100, default='Bogotá')
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Horarios
    horario_apertura = models.TimeField(null=True, blank=True)
    horario_cierre = models.TimeField(null=True, blank=True)
    dias_atencion = models.CharField(
        max_length=100,
        blank=True,
        help_text='Ej: Lun-Vie, Sáb'
    )

    # Estado y plan
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='basico'
    )
    destacado = models.BooleanField(default=False)
    verificado = models.BooleanField(default=False)

    # Métricas
    total_visualizaciones = models.PositiveIntegerField(default=0)
    total_clics_contacto = models.PositiveIntegerField(default=0)

    # Timestamps
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comercio'
        verbose_name_plural = 'Comercios'
        ordering = ['-destacado', '-total_visualizaciones']

    def __str__(self):
        return self.nombre

    @property
    def rating_promedio(self):
        resenas = self.resenas.filter(aprobada=True)
        if not resenas.exists():
            return 0
        total = sum(r.calificacion for r in resenas)
        return round(total / resenas.count(), 1)

    @property
    def total_resenas(self):
        return self.resenas.filter(aprobada=True).count()

    @property
    def esta_abierto(self):
        from datetime import datetime
        if not self.horario_apertura or not self.horario_cierre:
            return None
        ahora = datetime.now().time()
        return self.horario_apertura <= ahora <= self.horario_cierre


class Resena(models.Model):
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True)
    respuesta = models.TextField(blank=True)
    respuesta_fecha = models.DateTimeField(null=True, blank=True)
    aprobada = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-creado_en']
        # Un usuario solo puede reseñar un comercio una vez
        unique_together = ['comercio', 'autor']

    def __str__(self):
        return f'{self.autor.username} → {self.comercio.nombre} ({self.calificacion}★)'