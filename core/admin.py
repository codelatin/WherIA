from django.contrib import admin
from .models import Categoria, Comercio, Resena


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activa']
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'categoria', 'ciudad',
        'estado', 'plan', 'destacado',
        'rating_promedio', 'total_resenas'
    ]
    list_filter = ['estado', 'plan', 'destacado', 'categoria']
    search_fields = ['nombre', 'ciudad', 'direccion']
    prepopulated_fields = {'slug': ('nombre',)}
    actions = ['aprobar_comercios', 'rechazar_comercios']

    def aprobar_comercios(self, request, queryset):
        queryset.update(estado='activo')
        self.message_user(request, f'{queryset.count()} comercio(s) aprobado(s).')
    aprobar_comercios.short_description = 'Aprobar comercios seleccionados'

    def rechazar_comercios(self, request, queryset):
        queryset.update(estado='inactivo')
        self.message_user(request, f'{queryset.count()} comercio(s) rechazado(s).')
    rechazar_comercios.short_description = 'Rechazar comercios seleccionados'


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['autor', 'comercio', 'calificacion', 'aprobada', 'creado_en']
    list_filter = ['aprobada', 'calificacion']