from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Categoria, Equipo, ConsultaContacto

def format_clp(amount):
    """Formatea un número a pesos chilenos ($XX.XXX)"""
    try:
        val = int(round(amount))
        return f"${val:,}".replace(',', '.')
    except (ValueError, TypeError):
        return f"${amount}"


def get_cotizador_data(request):
    """
    Calcula los valores transitorios de la sesión del usuario (Criterio 2.1.4):
    Subtotal neto, cálculo legal de IVA (19%), garantía reembolsable y total final.
    """
    cotizador = request.session.get('cotizador', {})
    items_procesados = []
    subtotal_neto = 0.0
    garantia_total = 0.0

    for item_id, item in cotizador.items():
        tarifa = float(item.get('tarifa_diaria', 0))
        dias = int(item.get('dias', 1))
        cantidad = int(item.get('cantidad', 1))
        garantia_unitaria = float(item.get('garantia_unitaria', 15000.0))

        subtotal_item = tarifa * dias * cantidad
        garantia_item = garantia_unitaria * cantidad

        subtotal_neto += subtotal_item
        garantia_total += garantia_item

        item_copy = dict(item)
        item_copy['subtotal_item'] = subtotal_item
        item_copy['subtotal_item_formateado'] = format_clp(subtotal_item)
        item_copy['tarifa_diaria_formateada'] = format_clp(tarifa)
        item_copy['garantia_unitaria_formateada'] = format_clp(garantia_unitaria)
        item_copy['garantia_item_formateada'] = format_clp(garantia_item)
        items_procesados.append(item_copy)

    # Cálculo legal de IVA (19% en Chile) exigido por pauta
    iva = subtotal_neto * 0.19
    subtotal_con_iva = subtotal_neto + iva
    total_final = subtotal_con_iva + garantia_total

    totales = {
        'subtotal_neto': subtotal_neto,
        'subtotal_neto_formateado': format_clp(subtotal_neto),
        'iva': iva,
        'iva_formateado': format_clp(iva),
        'subtotal_con_iva': subtotal_con_iva,
        'subtotal_con_iva_formateado': format_clp(subtotal_con_iva),
        'garantia_total': garantia_total,
        'garantia_total_formateada': format_clp(garantia_total),
        'total_final': total_final,
        'total_final_formateado': format_clp(total_final),
        'total_items': sum(i['cantidad'] for i in items_procesados),
    }

    return items_procesados, totales


def home(request):
    """
    Vista 1: Landing Page RentEquip.
    """
    search_query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    orden = request.GET.get('orden', '').strip()

    equipos_qs = Equipo.objects.filter(activo=True).select_related('categoria')

    if search_query:
        equipos_qs = equipos_qs.filter(
            Q(nombre__icontains=search_query) | Q(codigo__icontains=search_query)
        )

    if categoria_id and categoria_id.isdigit():
        equipos_qs = equipos_qs.filter(categoria_id=int(categoria_id))

    if estado_filtro in ['DISPONIBLE', 'ARRENDADO', 'MANTENCION']:
        equipos_qs = equipos_qs.filter(estado=estado_filtro)

    if orden == 'precio_asc':
        equipos_qs = equipos_qs.order_by('tarifa_diaria')
    elif orden == 'precio_desc':
        equipos_qs = equipos_qs.order_by('-tarifa_diaria')
    elif orden == 'stock_desc':
        equipos_qs = equipos_qs.order_by('-stock')
    else:
        equipos_qs = equipos_qs.order_by('id')

    equipos_destacados = equipos_qs[:4]

    total_equipos = Equipo.objects.filter(activo=True).count()
    total_disponibles = Equipo.objects.filter(activo=True, estado='DISPONIBLE').count()
    total_arrendados = Equipo.objects.filter(activo=True, estado='ARRENDADO').count()
    total_mantencion = Equipo.objects.filter(activo=True, estado='MANTENCION').count()

    categorias = Categoria.objects.annotate(
        total_equipos=Count('equipo', filter=Q(equipo__activo=True))
    ).order_by('nombre')

    context = {
        'equipos': equipos_destacados,
        'categorias': categorias,
        'search_query': search_query,
        'categoria_seleccionada': int(categoria_id) if categoria_id.isdigit() else None,
        'estado_filtro': estado_filtro,
        'orden': orden,
        'kpi': {
            'total': total_equipos,
            'disponibles': total_disponibles,
            'arrendados': total_arrendados,
            'mantencion': total_mantencion,
        }
    }
    return render(request, 'equipos/home.html', context)


def catalogo_equipos(request):
    """
    Vista 2: Catálogo Completo de Equipos (/equipos/).
    """
    search_query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    precio_min = request.GET.get('precio_min', '').strip()
    precio_max = request.GET.get('precio_max', '').strip()
    stock_filtro = request.GET.get('stock', '').strip()
    orden = request.GET.get('orden', 'recientes').strip()

    equipos_qs = Equipo.objects.filter(activo=True).select_related('categoria')

    if search_query:
        equipos_qs = equipos_qs.filter(
            Q(nombre__icontains=search_query) | Q(codigo__icontains=search_query)
        )

    if categoria_id and categoria_id.isdigit():
        equipos_qs = equipos_qs.filter(categoria_id=int(categoria_id))

    if estado_filtro in ['DISPONIBLE', 'ARRENDADO', 'MANTENCION']:
        equipos_qs = equipos_qs.filter(estado=estado_filtro)

    if precio_min and precio_min.isdigit():
        equipos_qs = equipos_qs.filter(tarifa_diaria__gte=float(precio_min))
    if precio_max and precio_max.isdigit():
        equipos_qs = equipos_qs.filter(tarifa_diaria__lte=float(precio_max))

    if stock_filtro == 'con_stock':
        equipos_qs = equipos_qs.filter(stock__gt=0)
    elif stock_filtro == 'sin_stock':
        equipos_qs = equipos_qs.filter(stock=0)

    if orden == 'precio_asc':
        equipos_qs = equipos_qs.order_by('tarifa_diaria')
    elif orden == 'precio_desc':
        equipos_qs = equipos_qs.order_by('-tarifa_diaria')
    elif orden == 'stock_desc':
        equipos_qs = equipos_qs.order_by('-stock')
    elif orden == 'nombre_asc':
        equipos_qs = equipos_qs.order_by('nombre')
    else:
        equipos_qs = equipos_qs.order_by('id')

    paginator = Paginator(equipos_qs, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.annotate(
        total_equipos=Count('equipo', filter=Q(equipo__activo=True))
    ).order_by('nombre')

    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    filter_params = params.urlencode()

    context = {
        'equipos': page_obj,
        'page_obj': page_obj,
        'categorias': categorias,
        'search_query': search_query,
        'categoria_seleccionada': int(categoria_id) if categoria_id.isdigit() else None,
        'estado_filtro': estado_filtro if estado_filtro else 'TODOS',
        'precio_min': precio_min if precio_min else '0',
        'precio_max': precio_max if precio_max else '100000',
        'stock_filtro': stock_filtro if stock_filtro else 'todos',
        'orden': orden,
        'filter_params': filter_params,
        'total_equipos_filtrados': paginator.count,
    }
    return render(request, 'equipos/catalogo.html', context)


def detalle_equipo(request, pk):
    """
    Vista 3: Detalle del Equipo (/equipo/<id>/).
    """
    equipo = get_object_or_404(Equipo, pk=pk, activo=True)

    equipos_relacionados = list(Equipo.objects.filter(
        activo=True,
        categoria=equipo.categoria
    ).exclude(pk=equipo.pk)[:3])

    if len(equipos_relacionados) < 3:
        faltantes = 3 - len(equipos_relacionados)
        adicionales = list(Equipo.objects.filter(activo=True).exclude(
            pk__in=[equipo.pk] + [e.pk for e in equipos_relacionados]
        )[:faltantes])
        equipos_relacionados += adicionales

    categorias = Categoria.objects.annotate(
        total_equipos=Count('equipo', filter=Q(equipo__activo=True))
    ).order_by('nombre')

    context = {
        'equipo': equipo,
        'equipos_relacionados': equipos_relacionados,
        'categorias': categorias,
        'specs': equipo.specs_tecnicas,
    }
    return render(request, 'equipos/detalle_equipo.html', context)


def contacto(request):
    """
    Vista 4: Contacto / Cotización (/contacto/).
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        tipo_equipo = request.POST.get('tipo_equipo', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()

        if not nombre or not email or not mensaje:
            messages.error(request, 'Por favor completa todos los campos obligatorios (*).')
        else:
            ConsultaContacto.objects.create(
                nombre=nombre,
                email=email,
                telefono=telefono,
                tipo_equipo=tipo_equipo,
                mensaje=mensaje
            )
            messages.success(
                request,
                f'¡Muchas gracias, {nombre}! Tu solicitud de cotización para "{tipo_equipo or "equipos"}" fue enviada con éxito. '
                'Nuestro equipo de arriendos se contactará contigo a la brevedad.'
            )
            return redirect('contacto')

    categorias = Categoria.objects.all().order_by('nombre')
    context = {
        'categorias': categorias,
    }
    return render(request, 'equipos/contacto.html', context)


# ============================================================================
# FUNCIONALIDAD DE SESIÓN: COTIZADOR / CANASTA DE ARRIENDO (Criterio 2.1.4)
# ============================================================================

def agregar_a_cotizacion(request, pk):
    """
    Guarda temporalmente un equipo en la sesión del usuario (request.session) (Criterio 2.1.4).
    Permite seleccionar días y cantidad para cotizador con IVA y garantía.
    """
    equipo = get_object_or_404(Equipo, pk=pk, activo=True)

    if equipo.estado == 'MANTENCION':
        messages.error(request, f'El equipo "{equipo.nombre}" está en mantención preventiva.')
        return redirect(request.META.get('HTTP_REFERER') or 'home')

    if equipo.stock <= 0:
        messages.error(request, f'El equipo "{equipo.nombre}" no cuenta con stock disponible.')
        return redirect(request.META.get('HTTP_REFERER') or 'home')

    try:
        dias = max(1, min(90, int(request.POST.get('dias', request.GET.get('dias', 1)))))
    except (ValueError, TypeError):
        dias = 1

    try:
        cantidad = max(1, min(equipo.stock, int(request.POST.get('cantidad', request.GET.get('cantidad', 1)))))
    except (ValueError, TypeError):
        cantidad = 1

    # Colección transitoria en sesión
    cotizador = request.session.get('cotizador', {})
    equipo_key = str(equipo.id)

    # Definir garantía unitaria comercial según rubro
    if 'maquinaria' in equipo.categoria.nombre.lower():
        garantia_unitaria = 50000.0
    elif 'altura' in equipo.categoria.nombre.lower():
        garantia_unitaria = 25000.0
    else:
        garantia_unitaria = 15000.0

    cotizador[equipo_key] = {
        'id': equipo.id,
        'codigo': equipo.codigo,
        'nombre': equipo.nombre,
        'categoria': equipo.categoria.nombre,
        'tarifa_diaria': float(equipo.tarifa_diaria),
        'dias': dias,
        'cantidad': cantidad,
        'garantia_unitaria': garantia_unitaria,
        'imagen_url': equipo.imagen.url if equipo.imagen else '',
        'stock_max': equipo.stock,
    }

    request.session['cotizador'] = cotizador
    request.session.modified = True

    messages.success(
        request,
        f'¡"{equipo.nombre}" guardado en tu sesión de cotización! ({dias} día(s) x {cantidad} unidad(es)).'
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        _, totales = get_cotizador_data(request)
        return JsonResponse({
            'status': 'ok',
            'message': 'Equipo agregado al cotizador transitorio.',
            'count': sum(item['cantidad'] for item in cotizador.values()),
            'totales': totales,
        })

    return redirect('cotizador')


def resumen_cotizacion(request):
    """
    Vista de Canasta / Resumen de Solicitud de Arriendo (Criterio 2.1.4).
    Muestra la colección transitoria en sesión con cálculo de subtotal, IVA (19%) y garantía.
    """
    items, totales = get_cotizador_data(request)
    categorias = Categoria.objects.all().order_by('nombre')

    context = {
        'items': items,
        'totales': totales,
        'categorias': categorias,
    }
    return render(request, 'equipos/cotizador.html', context)


def actualizar_cotizacion(request, pk):
    """
    Permite modificar los días y cantidad de un equipo en la sesión (Criterio 2.1.4).
    """
    cotizador = request.session.get('cotizador', {})
    equipo_key = str(pk)

    if equipo_key in cotizador:
        try:
            dias = max(1, min(90, int(request.POST.get('dias', 1))))
            cotizador[equipo_key]['dias'] = dias
        except (ValueError, TypeError):
            pass

        try:
            stock_max = cotizador[equipo_key].get('stock_max', 10)
            cantidad = max(1, min(stock_max, int(request.POST.get('cantidad', 1))))
            cotizador[equipo_key]['cantidad'] = cantidad
        except (ValueError, TypeError):
            pass

        request.session['cotizador'] = cotizador
        request.session.modified = True
        messages.success(request, f'Cotización actualizada para {cotizador[equipo_key]["nombre"]}.')

    return redirect('cotizador')


def eliminar_de_cotizacion(request, pk):
    """
    Elimina un equipo de la colección transitoria en sesión (Criterio 2.1.4).
    """
    cotizador = request.session.get('cotizador', {})
    equipo_key = str(pk)

    if equipo_key in cotizador:
        nombre = cotizador[equipo_key].get('nombre', 'Equipo')
        del cotizador[equipo_key]
        request.session['cotizador'] = cotizador
        request.session.modified = True
        messages.info(request, f'"{nombre}" eliminado de tu cotización.')

    return redirect('cotizador')


def vaciar_cotizacion(request):
    """
    Vacía toda la colección transitoria en sesión (Criterio 2.1.4).
    """
    if 'cotizador' in request.session:
        request.session['cotizador'] = {}
        request.session.modified = True
        messages.info(request, 'Tu cotizador ha sido vaciado.')

    return redirect('cotizador')


def confirmar_solicitud_cotizacion(request):
    """
    Procesa la solicitud final desde la canasta/resumen de sesión (Criterio 2.1.4).
    Descuenta stock en BD, crea el registro formal y limpia la sesión.
    """
    if request.method == 'POST':
        items, totales = get_cotizador_data(request)

        if not items:
            messages.warning(request, 'No tienes equipos en tu cotizador para confirmar.')
            return redirect('cotizador')

        cliente_nombre = request.POST.get('cliente_nombre', 'Cliente General').strip()
        cliente_rut = request.POST.get('cliente_rut', '').strip()
        cliente_email = request.POST.get('cliente_email', '').strip()
        cliente_telefono = request.POST.get('cliente_telefono', '').strip()
        direccion_faena = request.POST.get('direccion_faena', '').strip()

        # Descontar stock de cada equipo en la base de datos
        resumen_equipos = []
        for it in items:
            try:
                eq = Equipo.objects.get(pk=it['id'])
                qty = it['cantidad']
                if eq.stock >= qty:
                    eq.stock -= qty
                    if eq.stock == 0:
                        eq.estado = 'ARRENDADO'
                    eq.save()
                    resumen_equipos.append(f"{qty}x {eq.nombre} ({it['dias']} días)")
                else:
                    messages.error(request, f'Stock insuficiente al momento de confirmar para {eq.nombre}.')
                    return redirect('cotizador')
            except Equipo.DoesNotExist:
                continue

        # Registrar la solicitud en la base de datos
        detalle_mensaje = (
            f"SOLICITUD DE ARRIENDO FORMAL\n"
            f"RUT/Cédula: {cliente_rut}\n"
            f"Dirección Faena: {direccion_faena}\n"
            f"Equipos: {', '.join(resumen_equipos)}\n\n"
            f"DESGLOSE FINANCIERO LEGAL:\n"
            f"- Subtotal Neto: {totales['subtotal_neto_formateado']}\n"
            f"- IVA (19% Legal): {totales['iva_formateado']}\n"
            f"- Garantía Reembolsable: {totales['garantia_total_formateada']}\n"
            f"- TOTAL FINAL A PAGAR: {totales['total_final_formateado']}"
        )

        ConsultaContacto.objects.create(
            nombre=cliente_nombre,
            email=cliente_email or 'cliente@correo.cl',
            telefono=cliente_telefono,
            tipo_equipo='Solicitud Arriendo Múltiple (Sesión)',
            mensaje=detalle_mensaje
        )

        # Vaciar la colección en sesión
        request.session['cotizador'] = {}
        request.session.modified = True

        mensaje_exito = (
            f'¡Solicitud de arriendo confirmada con éxito para {cliente_nombre}! '
            f'Neto: {totales["subtotal_neto_formateado"]} + IVA (19%): {totales["iva_formateado"]} '
            f'+ Garantía: {totales["garantia_total_formateada"]}. TOTAL: {totales["total_final_formateado"]}.'
        )
        messages.success(request, mensaje_exito)
        return redirect('cotizador')

    return redirect('cotizador')


# Mantener compatibilidad directa con solicitar_arriendo unitario
def solicitar_arriendo(request, pk):
    """
    Procesa la acción de 'Arrendar Ahora' guardando temporalmente el equipo
    en la colección transitoria de sesión (request.session) (Criterio 2.1.4),
    y redirigiendo a la vista de cotizador / canasta con cálculo legal de IVA (19%) y garantía.
    """
    return agregar_a_cotizacion(request, pk)


def cambiar_estado(request, pk):
    """
    Permite alternar o asignar el estado directamente para pruebas y control del inventario.
    """
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'home'
    if request.method == 'POST':
        equipo = get_object_or_404(Equipo, pk=pk)
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in ['DISPONIBLE', 'ARRENDADO', 'MANTENCION']:
            equipo.estado = nuevo_estado
            if nuevo_estado == 'DISPONIBLE' and equipo.stock == 0:
                equipo.stock = 1
            equipo.save()
            messages.success(request, f'Estado de "{equipo.nombre}" actualizado a {equipo.get_estado_display()}.')
    return redirect(next_url)
