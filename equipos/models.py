from django.db import models
from django.core.validators import MinValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


class Equipo(models.Model):
    ESTADOS_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('ARRENDADO', 'Arrendado'),
        ('MANTENCION', 'En Mantención'),
    ]

    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código / Sigla")
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Equipo")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="Categoría")
    
    # Atributo cuantitativo protegido con MinValueValidator (Exigido por pauta)
    tarifa_diaria = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)], 
        verbose_name="Tarifa Diaria ($)"
    )
    
    stock = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Stock Disponible")
    
    # Estado operativo con opciones cerradas (Exigido por pauta)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='DISPONIBLE', verbose_name="Estado Operativo")
    
    # Soporte multimedia (ImageField - Exigido por pauta)
    imagen = models.ImageField(upload_to='equipos/', blank=True, null=True, verbose_name="Imagen del Equipo")
    
    # Control de vigencia / baja lógica (Exigido por pauta)
    activo = models.BooleanField(default=True, verbose_name="Activo / Vigente")

    @property
    def tarifa_formateada(self):
        """Retorna la tarifa formateada como moneda chilena ($12.000)"""
        try:
            valor = int(self.tarifa_diaria)
            return f"${valor:,}".replace(',', '.')
        except (ValueError, TypeError):
            return f"${self.tarifa_diaria}"

    @property
    def is_disponible(self):
        return self.estado == 'DISPONIBLE' and self.stock > 0

    @property
    def estado_badge_info(self):
        """Metadatos visuales del estado para renderizado coherente"""
        mapeo = {
            'DISPONIBLE': {
                'label': 'Disponible',
                'color_dot': '#10b981',
                'badge_class': 'badge-disponible',
                'icon': 'fa-circle-check',
            },
            'ARRENDADO': {
                'label': 'Arrendado',
                'color_dot': '#3b82f6',
                'badge_class': 'badge-arrendado',
                'icon': 'fa-circle-info',
            },
            'MANTENCION': {
                'label': 'En Mantención',
                'color_dot': '#f59e0b',
                'badge_class': 'badge-mantencion',
                'icon': 'fa-circle-exclamation',
            },
        }
        return mapeo.get(self.estado, {
            'label': self.get_estado_display(),
            'color_dot': '#6b7280',
            'badge_class': 'badge-secondary',
            'icon': 'fa-circle-question',
        })

    @property
    def specs_tecnicas(self):
        """Genera especificaciones técnicas realistas adaptadas al tipo de equipo"""
        nombre_lower = self.nombre.lower()

        if 'taladro' in nombre_lower or 'rotomartillo' in nombre_lower:
            return {
                'resumen': 'Taladro inalámbrico de alto rendimiento, ideal para trabajos en madera, metal y concreto. Cuenta con batería de larga duración y diseño ergonómico.',
                'items': [
                    {'icon': 'fa-solid fa-bolt', 'label': 'Potencia', 'value': '18V'},
                    {'icon': 'fa-solid fa-battery-full', 'label': 'Batería', 'value': 'Litio 5.0 Ah'},
                    {'icon': 'fa-solid fa-weight-hanging', 'label': 'Peso', 'value': '1.8 kg'},
                    {'icon': 'fa-solid fa-hammer', 'label': 'Uso', 'value': 'Profesional y doméstico'},
                ],
                'caracteristicas': [
                    'Mandril metálico autoajustable de 13 mm',
                    '2 velocidades mecánicas reversibles',
                    'Luz LED frontal para áreas de baja visibilidad',
                    'Incluye 2 baterías de litio, cargador rápido y maletín de transporte rígido'
                ],
                'tabla': [
                    ('Voltaje / Batería', '18V Li-Ion (5.0 Ah)'),
                    ('Velocidad sin carga', '0-450 / 0-1650 RPM'),
                    ('Capacidad de Mandril', '13 mm (1/2 pulgada)'),
                    ('Torque Máximo', '65 Nm con 15 posiciones de embrague'),
                    ('Capacidad en Madera / Metal', '38 mm / 13 mm'),
                    ('Nivel de Presión Sonora', '76 dB(A)'),
                ]
            }
        elif 'excavadora' in nombre_lower or 'minicargador' in nombre_lower:
            return {
                'resumen': 'Maquinaria pesada para excavación, zanjas y movimiento de tierra en faenas exigentes.',
                'items': [
                    {'icon': 'fa-solid fa-gauge-high', 'label': 'Potencia', 'value': '24.8 HP Diésel'},
                    {'icon': 'fa-solid fa-weight-hanging', 'label': 'Capacidad', 'value': '3.2 Toneladas'},
                    {'icon': 'fa-solid fa-ruler-vertical', 'label': 'Profundidad Máx', 'value': '2.8 metros'},
                    {'icon': 'fa-solid fa-gas-pump', 'label': 'Combustible', 'value': 'Diésel'},
                ],
                'caracteristicas': [
                    'Oruga de goma antideslizante para todo terreno',
                    'Cabina antivuelco certificada ROPS/FOPS',
                    'Línea hidráulica auxiliar para martillo demoledor',
                    'Balde estándar de 0.09 m³ reforzado con dientes intercambiables'
                ],
                'tabla': [
                    ('Motor', 'Yanmar 3TNV88-B Diésel 3 Cilindros'),
                    ('Peso Operativo', '3.200 kg'),
                    ('Profundidad de Excavación', '2.820 mm'),
                    ('Alcance Máximo Horizontal', '4.850 mm'),
                    ('Capacidad del Balde', '0.09 m³'),
                    ('Velocidad de Traslación', '2.5 - 4.5 km/h'),
                ]
            }
        elif 'generador' in nombre_lower or 'torre' in nombre_lower:
            return {
                'resumen': 'Equipo de generación eléctrica continua para obras, eventos e industrias.',
                'items': [
                    {'icon': 'fa-solid fa-bolt', 'label': 'Potencia Nominal', 'value': '6.5 kVA / 5.5 kW'},
                    {'icon': 'fa-solid fa-plug', 'label': 'Voltaje', 'value': '220V Monofásico 50Hz'},
                    {'icon': 'fa-solid fa-gas-pump', 'label': 'Combustible', 'value': 'Gasolina / Diésel'},
                    {'icon': 'fa-solid fa-clock', 'label': 'Autonomía', 'value': '8.5 horas continuas'},
                ],
                'caracteristicas': [
                    'Regulador automático de voltaje digital (AVR)',
                    'Sensor de bajo nivel de aceite con corte automático de seguridad',
                    'Chasis tubular reforzado con ruedas macizas para fácil transporte',
                    'Doble salida Schuko 220V 16A y bornera industrial'
                ],
                'tabla': [
                    ('Potencia Máxima', '7.0 kVA (5.8 kW)'),
                    ('Capacidad Estanque', '25 Litros'),
                    ('Sistema de Arranque', 'Eléctrico con llave y manual retráctil'),
                    ('Nivel de Ruido a 7m', '72 dB(A)'),
                    ('Peso en Seco', '82 kg'),
                ]
            }
        elif 'andamio' in nombre_lower or 'escalera' in nombre_lower:
            return {
                'resumen': 'Estructura certificada de alta resistencia para trabajos seguros en altura.',
                'items': [
                    {'icon': 'fa-solid fa-arrows-up-down', 'label': 'Altura Trabajo', 'value': 'Hasta 6.5 metros'},
                    {'icon': 'fa-solid fa-weight-scale', 'label': 'Carga Máx', 'value': '250 kg/m² Certificado'},
                    {'icon': 'fa-solid fa-layer-group', 'label': 'Material', 'value': 'Acero Galvanizado'},
                    {'icon': 'fa-solid fa-shield-halved', 'label': 'Norma', 'value': 'NCh 998 / NCh 2501'},
                ],
                'caracteristicas': [
                    'Tubos de acero estructural con terminación galvanizada en caliente',
                    'Plataformas metálicas perforadas antideslizantes con traba de seguridad',
                    'Escalera interna con trampilla de acceso seguro',
                    'Bases regulables husillo para nivelación en terrenos irregulares'
                ],
                'tabla': [
                    ('Dimensiones de Base', '1.50 m x 2.00 m'),
                    ('Espesor Tubo Principal', '3.2 mm (diámetro 48.3 mm)'),
                    ('Carga Admisible por Plataforma', '300 kg distribuidos'),
                    ('Certificación', 'CESMEC / IDIEM Vigente'),
                ]
            }
        else:
            return {
                'resumen': f'Equipo profesional de alto rendimiento para faenas de construcción, maestranzas y obras.',
                'items': [
                    {'icon': 'fa-solid fa-bolt', 'label': 'Capacidad', 'value': 'Industrial'},
                    {'icon': 'fa-solid fa-check-double', 'label': 'Calidad', 'value': 'Uso Rudo'},
                    {'icon': 'fa-solid fa-shield', 'label': 'Protección', 'value': 'IP54 Certificado'},
                    {'icon': 'fa-solid fa-handshake', 'label': 'Garantía', 'value': 'Operativa 100%'},
                ],
                'caracteristicas': [
                    'Diseño ergonómico y materiales de alta durabilidad',
                    'Mantenimiento al día con certificación técnica de seguridad',
                    'Apto para faenas continuas en terreno'
                ],
                'tabla': [
                    ('Categoría', self.categoria.nombre),
                    ('Código', self.codigo),
                    ('Estado Actual', self.get_estado_display()),
                    ('Stock Disponible', f'{self.stock} unidades'),
                ]
            }

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"


class ConsultaContacto(models.Model):
    """
    Modelo para registrar consultas y cotizaciones de clientes enviadas desde el formulario.
    """
    nombre = models.CharField(max_length=150, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    tipo_equipo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo de Equipo")
    mensaje = models.TextField(verbose_name="Consulta o Mensaje")
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")
    atendido = models.BooleanField(default=False, verbose_name="Atendido / Contactado")

    def __str__(self):
        return f"{self.nombre} ({self.tipo_equipo or 'Consulta General'}) - {self.fecha_envio.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Consulta de Cotización"
        verbose_name_plural = "Consultas de Cotización"
        ordering = ['-fecha_envio']
