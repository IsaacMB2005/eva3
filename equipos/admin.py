from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Equipo, ConsultaContacto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 
        'nombre', 
        'categoria', 
        'tarifa_diaria_display', 
        'stock', 
        'estado', 
        'activo'
    )
    list_filter = ('estado', 'categoria', 'activo')
    search_fields = ('codigo', 'nombre')
    list_editable = ('stock', 'estado', 'activo')
    ordering = ('id',)

    fieldsets = (
        ('Identificación del Equipo', {
            'fields': ('codigo', 'nombre', 'categoria', 'imagen')
        }),
        ('Control de Arriendo y Disponibilidad', {
            'fields': ('tarifa_diaria', 'stock', 'estado', 'activo'),
            'description': 'Campos clave para el control de inventario y tarificación.'
        }),
    )

    @admin.display(description='Tarifa Diaria')
    def tarifa_diaria_display(self, obj):
        return obj.tarifa_formateada


@admin.register(ConsultaContacto)
class ConsultaContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'tipo_equipo', 'fecha_envio', 'atendido')
    list_filter = ('atendido', 'tipo_equipo', 'fecha_envio')
    search_fields = ('nombre', 'email', 'telefono', 'mensaje')
    list_editable = ('atendido',)
    ordering = ('-fecha_envio',)
