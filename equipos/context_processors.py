def cotizador_context(request):
    """
    Context processor para exponer el contador de la canasta transitoria de sesión
    en todas las plantillas del sitio (Criterio 2.1.4).
    """
    cotizador = request.session.get('cotizador', {})
    count = sum(item.get('cantidad', 1) for item in cotizador.values())
    return {
        'cotizador_count': count,
        'cotizador_tiene_items': count > 0,
    }
