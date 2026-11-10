from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from equipos.models import Categoria, Equipo

class Command(BaseCommand):
    help = 'Carga inicial de clasificadores (categorías/tipos de faena), 8 equipos coherentes y usuarios de prueba (Criterio 2.1.1)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('=== INICIANDO CARGA INICIAL DE DATOS (RentEquip) ==='))

        # 1. USUARIOS DE PRUEBA (Admin y Estándar)
        self.stdout.write('\n1. Creando / Verificando usuarios de prueba...')

        # Superusuario Administrador
        admin_user, created_admin = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@rentequip.cl',
                'first_name': 'Administrador',
                'last_name': 'RentEquip',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('Admin123!')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        if created_admin:
            self.stdout.write(self.style.SUCCESS('   [+] Superusuario creado: admin / Admin123!'))
        else:
            self.stdout.write(self.style.SUCCESS('   [*] Superusuario actualizado: admin / Admin123!'))

        # Usuario Administrador Isaac (si existe o para facilitar su acceso)
        isaac_user, created_isaac = User.objects.get_or_create(
            username='admin_isaac',
            defaults={
                'email': 'isaac.molina@rentequip.cl',
                'first_name': 'Isaac',
                'last_name': 'Molina',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        isaac_user.set_password('Admin123!')
        isaac_user.is_staff = True
        isaac_user.is_superuser = True
        isaac_user.save()
        if created_isaac:
            self.stdout.write(self.style.SUCCESS('   [+] Superusuario creado: admin_isaac / Admin123!'))

        # Usuario Estándar (Cliente de arriendo)
        std_user, created_std = User.objects.get_or_create(
            username='cliente_estandar',
            defaults={
                'email': 'cliente@constructora.cl',
                'first_name': 'Cliente',
                'last_name': 'Estándar',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        std_user.set_password('Cliente123!')
        std_user.save()
        if created_std:
            self.stdout.write(self.style.SUCCESS('   [+] Usuario estándar creado: cliente_estandar / Cliente123!'))
        else:
            self.stdout.write(self.style.SUCCESS('   [*] Usuario estándar actualizado: cliente_estandar / Cliente123!'))

        # 2. CLASIFICADORES (Categorías / Tipos de Faena)
        self.stdout.write('\n2. Creando clasificadores (Categorías / Tipos de Faena)...')
        categorias_data = [
            {
                'nombre': 'Herramientas Eléctricas',
                'descripcion': 'Faena: Instalaciones, carpintería, maestranza y taller. Equipos portátiles y cableados.'
            },
            {
                'nombre': 'Maquinaria Pesada',
                'descripcion': 'Faena: Movimiento de tierras, excavaciones, zanjas y demolición en obras viales y civiles.'
            },
            {
                'nombre': 'Generación y Energía',
                'descripcion': 'Faena: Iluminación, faenas aisladas sin red eléctrica y respaldo en industrias y eventos.'
            },
            {
                'nombre': 'Construcción y Altura',
                'descripcion': 'Faena: Obras civiles, hormigonado, enfierradura y estructuras seguras para trabajos en altura.'
            },
            {
                'nombre': 'Herramientas de Jardinería',
                'descripcion': 'Faena: Mantención de áreas verdes, desmalezado, podas, paisajismo y desbroce de parcelas.'
            },
        ]

        categorias_map = {}
        for cdata in categorias_data:
            cat_obj, created = Categoria.objects.update_or_create(
                nombre=cdata['nombre'],
                defaults={'descripcion': cdata['descripcion']}
            )
            categorias_map[cat_obj.nombre] = cat_obj
            prefix = '[+]' if created else '[*]'
            self.stdout.write(self.style.SUCCESS(f'   {prefix} Categoría: {cat_obj.nombre}'))

        # 3. LOS 8 EQUIPOS COHERENTES DEL DOMINIO
        self.stdout.write('\n3. Creando los 8 equipos coherentes de arriendo...')
        equipos_8 = [
            {
                'codigo': 'TAL-001',
                'nombre': 'Taladro Inalámbrico',
                'categoria': categorias_map['Herramientas Eléctricas'],
                'tarifa_diaria': 12000.00,
                'stock': 10,
                'estado': 'DISPONIBLE',
                'imagen': 'equipos/taladro.png',
                'activo': True,
            },
            {
                'codigo': 'EXC-003',
                'nombre': 'Excavadora 3 Ton',
                'categoria': categorias_map['Maquinaria Pesada'],
                'tarifa_diaria': 90000.00,
                'stock': 2,
                'estado': 'ARRENDADO',
                'imagen': 'equipos/excavadora.png',
                'activo': True,
            },
            {
                'codigo': 'GEN-002',
                'nombre': 'Generador Eléctrico',
                'categoria': categorias_map['Generación y Energía'],
                'tarifa_diaria': 18000.00,
                'stock': 6,
                'estado': 'DISPONIBLE',
                'imagen': 'equipos/generador.png',
                'activo': True,
            },
            {
                'codigo': 'AND-001',
                'nombre': 'Andamio Metálico',
                'categoria': categorias_map['Construcción y Altura'],
                'tarifa_diaria': 15000.00,
                'stock': 8,
                'estado': 'DISPONIBLE',
                'imagen': 'equipos/andamio.png',
                'activo': True,
            },
            {
                'codigo': 'HOR-001',
                'nombre': 'Hormigonera',
                'categoria': categorias_map['Construcción y Altura'],
                'tarifa_diaria': 14000.00,
                'stock': 5,
                'estado': 'DISPONIBLE',
                'imagen': 'equipos/hormigonera.png',
                'activo': True,
            },
            {
                'codigo': 'COM-001',
                'nombre': 'Compactadora',
                'categoria': categorias_map['Maquinaria Pesada'],
                'tarifa_diaria': 20000.00,
                'stock': 4,
                'estado': 'DISPONIBLE',
                'imagen': 'equipos/compactadora.png',
                'activo': True,
            },
            {
                'codigo': 'ESC-001',
                'nombre': 'Escalera Telescópica',
                'categoria': categorias_map['Construcción y Altura'],
                'tarifa_diaria': 10000.00,
                'stock': 7,
                'estado': 'DISPONIBLE',
                'imagen': 'equipos/escalera.png',
                'activo': True,
            },
            {
                'codigo': 'SOL-001',
                'nombre': 'Soldadora Inverter',
                'categoria': categorias_map['Herramientas Eléctricas'],
                'tarifa_diaria': 22000.00,
                'stock': 3,
                'estado': 'ARRENDADO',
                'imagen': 'equipos/soldadora.png',
                'activo': True,
            },
        ]

        for edata in equipos_8:
            eq_obj, created = Equipo.objects.update_or_create(
                codigo=edata['codigo'],
                defaults=edata
            )
            prefix = '[+]' if created else '[*]'
            self.stdout.write(self.style.SUCCESS(
                f'   {prefix} {eq_obj.codigo} - {eq_obj.nombre} | Tarifa: {eq_obj.tarifa_formateada} | Stock: {eq_obj.stock} | Estado: {eq_obj.estado}'
            ))

        # Equipos adicionales para faenas y jardinería
        equipos_adicionales = [
            ('ESM-001', 'Esmeril Angular', categorias_map['Herramientas Eléctricas'], 10000, 5, 'DISPONIBLE', 'equipos/esmeril.png'),
            ('SIE-002', 'Sierra Circular', categorias_map['Herramientas Eléctricas'], 14000, 4, 'DISPONIBLE', 'equipos/sierra.png'),
            ('ROT-002', 'Rotomartillo', categorias_map['Herramientas Eléctricas'], 16000, 6, 'DISPONIBLE', 'equipos/rotomartillo.png'),
            ('JAR-001', 'Cortacésped a Gasolina 5.5 HP', categorias_map['Herramientas de Jardinería'], 16000, 4, 'DISPONIBLE', 'equipos/generador.png'),
            ('JAR-002', 'Desbrozadora Profesional 52cc', categorias_map['Herramientas de Jardinería'], 12000, 6, 'DISPONIBLE', 'equipos/taladro.png'),
        ]

        for code, name, cat, price, stock, st, img in equipos_adicionales:
            Equipo.objects.update_or_create(
                codigo=code,
                defaults={
                    'nombre': name,
                    'categoria': cat,
                    'tarifa_diaria': price,
                    'stock': stock,
                    'estado': st,
                    'imagen': img,
                    'activo': True,
                }
            )

        self.stdout.write('\n' + self.style.SUCCESS('=== CARGA DE DATOS COMPLETADA CON ÉXITO ==='))
        self.stdout.write(f'Total Categorías: {Categoria.objects.count()}')
        self.stdout.write(f'Total Equipos: {Equipo.objects.count()}')
        self.stdout.write(f'Total Usuarios: {User.objects.count()}')
