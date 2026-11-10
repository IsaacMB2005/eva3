from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('equipos/', views.catalogo_equipos, name='catalogo'),
    path('equipo/<int:pk>/', views.detalle_equipo, name='detalle_equipo'),
    path('contacto/', views.contacto, name='contacto'),

    # Funcionalidad de Sesión: Cotizador / Canasta de Arriendo (Criterio 2.1.4)
    path('cotizador/', views.resumen_cotizacion, name='cotizador'),
    path('canasta/', views.resumen_cotizacion, name='canasta'),
    path('cotizador/agregar/<int:pk>/', views.agregar_a_cotizacion, name='agregar_a_cotizacion'),
    path('cotizador/actualizar/<int:pk>/', views.actualizar_cotizacion, name='actualizar_cotizacion'),
    path('cotizador/eliminar/<int:pk>/', views.eliminar_de_cotizacion, name='eliminar_de_cotizacion'),
    path('cotizador/vaciar/', views.vaciar_cotizacion, name='vaciar_cotizacion'),
    path('cotizador/confirmar/', views.confirmar_solicitud_cotizacion, name='confirmar_cotizacion'),

    # Acciones operativas y control
    path('arrendar/<int:pk>/', views.solicitar_arriendo, name='solicitar_arriendo'),
    path('cambiar-estado/<int:pk>/', views.cambiar_estado, name='cambiar_estado'),
]
