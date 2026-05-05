import datetime
import random
import json
import os
# ─────────────────────────────────────────────────────────────
# MÓDULO 1: GESTIÓN DE CLIENTES
# ─────────────────────────────────────────────────────────────
class Cliente:
    """Representa un cliente del banco."""
    # DEFECTO DOCUMENTACIÓN: el parámetro 'tipo' no está documentado
    def __init__(self, nombre, cedula, email, telefono, tipo="natural"):
        self.nombre = nombre
        self.cedula = cedula
        self.email = email
        self.telefono = telefono
        self.tipo = tipo
        self.cuentas = []          # DEFECTO DATOS: lista inicializada pero nunca validada al agregar
        self.fecha_registro = datetime.datetime.now()
        self.activo = True
        self.historial_cambios = []
    def actualizar_email(self, nuevo_email):
        # DEFECTO LÓGICO: no valida formato de email antes de actualizar
        self.historial_cambios.append(("email", self.email, nuevo_email))
        self.email = nuevo_email
    def actualizar_telefono(self, nuevo_telefono):
        # DEFECTO INTERFAZ: no valida que el teléfono sea numérico
        self.telefono = nuevo_telefono
    def desactivar(self):
        self.activo = False
    def agregar_cuenta(self, cuenta):
        self.cuentas.append(cuenta)
    def obtener_resumen(self):
        total = sum(c.saldo for c in self.cuentas)
        return {
            "nombre": self.nombre,
            "cedula": self.cedula,
            "cuentas": len(self.cuentas),
            "saldo_total": total,
            "activo": self.activo
        }
    def __str__(self):
        return f"Cliente: {self.nombre} | Cédula: {self.cedula} | Email: {self.email}"
class GestorClientes:
    """Administra el registro y consulta de clientes."""
    def __init__(self):
        self.clientes = {}
        self.total_registrados = 0
    def registrar_cliente(self, nombre, cedula, email, telefono, tipo="natural"):
        # DEFECTO LÓGICO: permite registrar cédulas duplicadas sin advertencia
        cliente = Cliente(nombre, cedula, email, telefono, tipo)
        self.clientes[cedula] = cliente
        self.total_registrados += 1
        print(f"Cliente {nombre} registrado exitosamente.")
        return cliente
    def buscar_cliente(self, cedula):
        # DEFECTO INTERFAZ: no maneja el caso cuando cedula es None
        return self.clientes.get(cedula)
    def eliminar_cliente(self, cedula):
        cliente = self.buscar_cliente(cedula)
        if cliente:
            # DEFECTO LÓGICO: elimina el cliente aunque tenga cuentas activas con saldo
            del self.clientes[cedula]
            return True
        return False
    def listar_clientes_activos(self):
        return [c for c in self.clientes.values() if c.activo]
    def total_clientes(self):
        return len(self.clientes)
# ─────────────────────────────────────────────────────────────
# MÓDULO 2: GESTIÓN DE CUENTAS
# ─────────────────────────────────────────────────────────────
class Cuenta:
    """
    Representa una cuenta bancaria.
    Tipos soportados: ahorros, corriente
    """
    INTERES_AHORROS = 0.03   # DEFECTO DOCUMENTACIÓN: comentario dice 3% pero antes era 5%, no actualizado en docs externos
    INTERES_CORRIENTE = 0.0
    def __init__(self, numero, tipo, cliente, saldo_inicial=0):
        self.numero = numero
        self.tipo = tipo
        self.cliente = cliente
        self.saldo = saldo_inicial
        self.transacciones = []
        self.fecha_apertura = datetime.datetime.now()
        self.activa = True
        self.bloqueada = False
    def depositar(self, monto):
        # DEFECTO LÓGICO: no verifica que el monto sea positivo
        self.saldo += monto
        self._registrar_transaccion("deposito", monto)
        print(f"Depósito de {monto} realizado. Saldo actual: {self.saldo}")
    def retirar(self, monto):
        # DEFECTO LÓGICO: permite retiros mayores al saldo (saldo negativo)
        self.saldo -= monto
        self._registrar_transaccion("retiro", monto)
        print(f"Retiro de {monto} realizado. Saldo actual: {self.saldo}")
    def consultar_saldo(self):
        return self.saldo
    def aplicar_interes(self):
        """Aplica interés mensual según tipo de cuenta."""
        if self.tipo == "ahorros":
            # DEFECTO DOCUMENTACIÓN: el método dice mensual pero calcula anual
            interes = self.saldo * self.INTERES_AHORROS
            self.saldo += interes
            self._registrar_transaccion("interes", interes)
    def bloquear(self):
        self.bloqueada = True
    def desbloquear(self):
        self.bloqueada = False
    def _registrar_transaccion(self, tipo, monto):
        self.transacciones.append({
            "tipo": tipo,
            "monto": monto,
            "fecha": datetime.datetime.now().isoformat(),
            "saldo_posterior": self.saldo
        })
    def historial(self):
        return self.transacciones
    def __str__(self):
        return f"Cuenta {self.numero} | Tipo: {self.tipo} | Saldo: {self.saldo}"
class GestorCuentas:
    """Administra la creación y operación de cuentas bancarias."""
    def __init__(self):
        self.cuentas = {}
        self.contador = 1000
    def _generar_numero(self):
        self.contador += 1
        return f"BP-{self.contador}"
    def abrir_cuenta(self, cliente, tipo="ahorros", saldo_inicial=0):
        # DEFECTO INTERFAZ: no valida que el tipo sea 'ahorros' o 'corriente'
        numero = self._generar_numero()
        cuenta = Cuenta(numero, tipo, cliente, saldo_inicial)
        self.cuentas[numero] = cuenta
        cliente.agregar_cuenta(cuenta)
        print(f"Cuenta {numero} abierta para {cliente.nombre}.")
        return cuenta
    def cerrar_cuenta(self, numero):
        cuenta = self.cuentas.get(numero)
        if cuenta:
            # DEFECTO LÓGICO: cierra la cuenta sin devolver el saldo al cliente
            cuenta.activa = False
            return True
        return False
    def transferir(self, origen_num, destino_num, monto):
        origen = self.cuentas.get(origen_num)
        destino = self.cuentas.get(destino_num)
        # DEFECTO LÓGICO: no verifica si alguna cuenta está bloqueada antes de transferir
        if not origen or not destino:
            print("Una o ambas cuentas no existen.")
            return False
        if origen.saldo < monto:
            print("Saldo insuficiente.")
            return False
        origen.retirar(monto)
        destino.depositar(monto)
        print(f"Transferencia de {monto} de {origen_num} a {destino_num} completada.")
        return True
    def buscar_cuenta(self, numero):
        return self.cuentas.get(numero)
    def listar_cuentas_activas(self):
        return [c for c in self.cuentas.values() if c.activa]
# ─────────────────────────────────────────────────────────────
# MÓDULO 3: GESTIÓN DE PRÉSTAMOS
# ─────────────────────────────────────────────────────────────
class Prestamo:
    """Representa un préstamo bancario."""
    TASA_INTERES = 0.12   # 12% anual
    def __init__(self, cliente, monto, plazo_meses):
        self.id = random.randint(10000, 99999)
        self.cliente = cliente
        self.monto_original = monto
        self.monto_pendiente = monto
        self.plazo_meses = plazo_meses
        self.cuota_mensual = self._calcular_cuota()
        self.fecha_inicio = datetime.datetime.now()
        self.pagos = []
        self.activo = True
    def _calcular_cuota(self):
        # Fórmula de amortización francesa
        tasa_mensual = self.TASA_INTERES / 12
        n = self.plazo_meses
        cuota = self.monto_original * (tasa_mensual * (1 + tasa_mensual) ** n) / ((1 + tasa_mensual) ** n - 1)
        return round(cuota, 2)
    def registrar_pago(self, monto):
        # DEFECTO LÓGICO: permite pagar más del monto pendiente sin advertencia
        self.monto_pendiente -= monto
        self.pagos.append({
            "monto": monto,
            "fecha": datetime.datetime.now().isoformat(),
            "saldo_restante": self.monto_pendiente
        })
        if self.monto_pendiente <= 0:
            self.activo = False
            print("Préstamo cancelado completamente.")
    def estado(self):
        return {
            "id": self.id,
            "cliente": self.cliente.nombre,
            "monto_original": self.monto_original,
            "monto_pendiente": self.monto_pendiente,
            "cuota_mensual": self.cuota_mensual,
            "pagos_realizados": len(self.pagos),
            "activo": self.activo
        }
    def __str__(self):
        return f"Préstamo #{self.id} | Cliente: {self.cliente.nombre} | Pendiente: {self.monto_pendiente}"
class GestorPrestamos:
    """Administra el ciclo de vida de préstamos bancarios."""
    MONTO_MAXIMO = 50000
    PLAZO_MAXIMO = 60
    def __init__(self):
        self.prestamos = {}
    def solicitar_prestamo(self, cliente, monto, plazo_meses):
        # DEFECTO LÓGICO: no verifica historial crediticio del cliente
        # DEFECTO LÓGICO: no verifica si el cliente ya tiene préstamos activos
        if monto > self.MONTO_MAXIMO:
            print(f"El monto supera el límite permitido de {self.MONTO_MAXIMO}.")
            return None
        if plazo_meses > self.PLAZO_MAXIMO:
            print(f"El plazo supera el máximo de {self.PLAZO_MAXIMO} meses.")
            return None
        prestamo = Prestamo(cliente, monto, plazo_meses)
        self.prestamos[prestamo.id] = prestamo
        print(f"Préstamo #{prestamo.id} aprobado por {monto}. Cuota: {prestamo.cuota_mensual}/mes.")
        return prestamo
    def pagar_cuota(self, prestamo_id, monto):
        prestamo = self.prestamos.get(prestamo_id)
        if not prestamo:
            print("Préstamo no encontrado.")
            return False
        if not prestamo.activo:
            print("El préstamo ya está cancelado.")
            return False
        prestamo.registrar_pago(monto)
        return True
    def prestamos_activos(self):
        return [p for p in self.prestamos.values() if p.activo]
    def prestamos_por_cliente(self, cedula):
        return [p for p in self.prestamos.values() if p.cliente.cedula == cedula]
# ─────────────────────────────────────────────────────────────
# MÓDULO 4: SEGURIDAD Y ACCESO
# ─────────────────────────────────────────────────────────────
class SistemaSeguridad:
    """Gestiona la autenticación y autorización de usuarios."""
    def __init__(self):
        self.usuarios = {}
        self.sesiones_activas = {}
        self.intentos_fallidos = {}
    def registrar_usuario(self, cedula, password, rol="cliente"):
        # DEFECTO SEGURIDAD: contraseña almacenada en texto plano
        self.usuarios[cedula] = {
            "password": password,
            "rol": rol,
            "activo": True
        }
    def autenticar(self, cedula, password):
        # DEFECTO SEGURIDAD: no limita intentos fallidos de login
        usuario = self.usuarios.get(cedula)
        if not usuario:
            return False
        # DEFECTO LÓGICO: comparación directa sin hashing
        if usuario["password"] == password:
            token = str(random.randint(100000, 999999))
            self.sesiones_activas[cedula] = token
            return token
        return False
    def cerrar_sesion(self, cedula):
        if cedula in self.sesiones_activas:
            del self.sesiones_activas[cedula]
            return True
        return False
    def validar_sesion(self, cedula, token):
        return self.sesiones_activas.get(cedula) == token
    def cambiar_password(self, cedula, password_actual, password_nuevo):
        usuario = self.usuarios.get(cedula)
        if not usuario:
            return False
        # DEFECTO LÓGICO: no valida complejidad de la nueva contraseña
        if usuario["password"] == password_actual:
            usuario["password"] = password_nuevo
            return True
        return False
# ─────────────────────────────────────────────────────────────
# MÓDULO 5: REPORTES Y ESTADÍSTICAS
# ─────────────────────────────────────────────────────────────
class GeneradorReportes:
    """
    Genera reportes financieros del banco.
    Nota: los reportes se generan en memoria, no se persisten.
    """
    def __init__(self, gestor_clientes, gestor_cuentas, gestor_prestamos):
        self.gc = gestor_clientes
        self.gcu = gestor_cuentas
        self.gp = gestor_prestamos
    def reporte_clientes(self):
        clientes = self.gc.listar_clientes_activos()
        total_saldo = 0
        reporte = []
        for c in clientes:
            resumen = c.obtener_resumen()
            total_saldo += resumen["saldo_total"]
            reporte.append(resumen)
        print(f"\n=== REPORTE DE CLIENTES ===")
        print(f"Total clientes activos: {len(clientes)}")
        print(f"Saldo total en el banco: {total_saldo:.2f}")
        return reporte
    def reporte_cuentas(self):
        cuentas = self.gcu.listar_cuentas_activas()
        ahorros = [c for c in cuentas if c.tipo == "ahorros"]
        corrientes = [c for c in cuentas if c.tipo == "corriente"]
        print(f"\n=== REPORTE DE CUENTAS ===")
        print(f"Cuentas de ahorros: {len(ahorros)}")
        print(f"Cuentas corrientes: {len(corrientes)}")
        print(f"Total cuentas activas: {len(cuentas)}")
        return {
            "ahorros": len(ahorros),
            "corrientes": len(corrientes),
            "total": len(cuentas)
        }
    def reporte_prestamos(self):
        activos = self.gp.prestamos_activos()
        total_pendiente = sum(p.monto_pendiente for p in activos)
        print(f"\n=== REPORTE DE PRÉSTAMOS ===")
        print(f"Préstamos activos: {len(activos)}")
        print(f"Total pendiente de cobro: {total_pendiente:.2f}")
        return {
            "activos": len(activos),
            "total_pendiente": total_pendiente
        }
    def reporte_movimientos(self, numero_cuenta):
        cuenta = self.gcu.buscar_cuenta(numero_cuenta)
        # DEFECTO INTERFAZ: no maneja el caso cuando la cuenta no existe
        historial = cuenta.historial()
        print(f"\n=== MOVIMIENTOS CUENTA {numero_cuenta} ===")
        for mov in historial:
            print(f"  {mov['fecha']} | {mov['tipo'].upper()} | Monto: {mov['monto']} | Saldo: {mov['saldo_posterior']}")
        return historial
    def exportar_json(self, datos, nombre_archivo):
        # DEFECTO SEGURIDAD: no valida el nombre del archivo (path traversal)
        ruta = f"/tmp/{nombre_archivo}.json"
        with open(ruta, "w") as f:
            json.dump(datos, f, indent=2, default=str)
        print(f"Reporte exportado en {ruta}")
        return ruta
# ─────────────────────────────────────────────────────────────
# MÓDULO 6: NOTIFICACIONES
# ─────────────────────────────────────────────────────────────
class SistemaNotificaciones:
    """Envía notificaciones a los clientes por distintos canales."""
    def __init__(self):
        self.notificaciones_enviadas = []
        self.canal_default = "email"
    def enviar_email(self, destinatario, asunto, cuerpo):
        # DEFECTO DOCUMENTACIÓN: se menciona que conecta con SMTP pero no hay implementación real
        print(f"[EMAIL] Para: {destinatario} | Asunto: {asunto}")
        self.notificaciones_enviadas.append({
            "canal": "email",
            "destinatario": destinatario,
            "asunto": asunto,
            "fecha": datetime.datetime.now().isoformat()
        })
    def enviar_sms(self, telefono, mensaje):
        # DEFECTO INTERFAZ: no valida que el teléfono tenga formato correcto
        print(f"[SMS] Para: {telefono} | Mensaje: {mensaje}")
        self.notificaciones_enviadas.append({
            "canal": "sms",
            "destinatario": telefono,
            "mensaje": mensaje,
            "fecha": datetime.datetime.now().isoformat()
        })
    def notificar_transaccion(self, cliente, tipo, monto):
        asunto = f"Transacción registrada: {tipo}"
        cuerpo = f"Se registró un {tipo} de {monto} en su cuenta. Fecha: {datetime.datetime.now()}"
        self.enviar_email(cliente.email, asunto, cuerpo)
        self.enviar_sms(cliente.telefono, f"{tipo.upper()} de {monto} registrado.")
    def notificar_alerta(self, cliente, mensaje):
        self.enviar_email(cliente.email, "Alerta de seguridad", mensaje)
    def historial_notificaciones(self):
        return self.notificaciones_enviadas
# ─────────────────────────────────────────────────────────────
# MÓDULO 7: AUDITORÍA INTERNA
# ─────────────────────────────────────────────────────────────
class AuditoriaInterna:
    """
    Registra eventos críticos del sistema para fines de auditoría.
    Todos los eventos se almacenan en memoria durante la sesión.
    """
    NIVELES = ["INFO", "ADVERTENCIA", "ERROR", "CRITICO"]
    def __init__(self):
        self.log = []
        self.errores_criticos = 0
    def registrar(self, nivel, modulo, descripcion, usuario=None):
        # DEFECTO LÓGICO: no valida que el nivel sea uno de los permitidos
        evento = {
            "id": len(self.log) + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "nivel": nivel,
            "modulo": modulo,
            "descripcion": descripcion,
            "usuario": usuario
        }
        self.log.append(evento)
        if nivel == "CRITICO":
            self.errores_criticos += 1
        print(f"[AUDITORIA][{nivel}] {modulo}: {descripcion}")
    def obtener_errores(self):
        return [e for e in self.log if e["nivel"] in ("ERROR", "CRITICO")]
    def obtener_log_completo(self):
        return self.log
    def resumen(self):
        conteo = {nivel: 0 for nivel in self.NIVELES}
        for evento in self.log:
            if evento["nivel"] in conteo:
                conteo[evento["nivel"]] += 1
        return conteo
    def limpiar_log(self):
        # DEFECTO LÓGICO: limpiar el log elimina evidencia de auditoría permanentemente
        self.log = []
        self.errores_criticos = 0
# ─────────────────────────────────────────────────────────────
# MÓDULO 8: SISTEMA PRINCIPAL (BANCO)
# ─────────────────────────────────────────────────────────────
class BancoPlus:
    """
    Sistema principal del banco BancoPlus.
    Integra todos los módulos: clientes, cuentas, préstamos, seguridad,
    notificaciones, reportes y auditoría.
    """
    VERSION = "1.0.0"
    def __init__(self):
        self.nombre = "BancoPlus"
        self.gestor_clientes = GestorClientes()
        self.gestor_cuentas = GestorCuentas()
        self.gestor_prestamos = GestorPrestamos()
        self.seguridad = SistemaSeguridad()
        self.notificaciones = SistemaNotificaciones()
        self.auditoria = AuditoriaInterna()
        self.reportes = GeneradorReportes(
            self.gestor_clientes,
            self.gestor_cuentas,
            self.gestor_prestamos
        )
        self.auditoria.registrar("INFO", "SISTEMA", f"{self.nombre} v{self.VERSION} iniciado.")
    def registrar_cliente(self, nombre, cedula, email, telefono, password):
        cliente = self.gestor_clientes.registrar_cliente(nombre, cedula, email, telefono)
        self.seguridad.registrar_usuario(cedula, password)
        self.auditoria.registrar("INFO", "CLIENTES", f"Nuevo cliente registrado: {cedula}")
        self.notificaciones.enviar_email(
            email,
            "Bienvenido a BancoPlus",
            f"Hola {nombre}, tu cuenta ha sido creada exitosamente."
        )
        return cliente
    def abrir_cuenta(self, cedula, tipo="ahorros", saldo_inicial=0):
        cliente = self.gestor_clientes.buscar_cliente(cedula)
        if not cliente:
            print("Cliente no encontrado.")
            self.auditoria.registrar("ADVERTENCIA", "CUENTAS", f"Intento abrir cuenta para cliente inexistente: {cedula}")
            return None
        cuenta = self.gestor_cuentas.abrir_cuenta(cliente, tipo, saldo_inicial)
        self.auditoria.registrar("INFO", "CUENTAS", f"Cuenta {cuenta.numero} abierta para {cedula}")
        return cuenta
    def depositar(self, numero_cuenta, monto, cedula_usuario):
        cuenta = self.gestor_cuentas.buscar_cuenta(numero_cuenta)
        if not cuenta:
            print("Cuenta no encontrada.")
            return False
        cuenta.depositar(monto)
        self.notificaciones.notificar_transaccion(cuenta.cliente, "depósito", monto)
        self.auditoria.registrar("INFO", "TRANSACCIONES", f"Depósito {monto} en cuenta {numero_cuenta}", cedula_usuario)
        return True
    def retirar(self, numero_cuenta, monto, cedula_usuario):
        cuenta = self.gestor_cuentas.buscar_cuenta(numero_cuenta)
        if not cuenta:
            print("Cuenta no encontrada.")
            return False
        # DEFECTO LÓGICO: no verifica cuenta bloqueada antes de retirar
        cuenta.retirar(monto)
        self.notificaciones.notificar_transaccion(cuenta.cliente, "retiro", monto)
        self.auditoria.registrar("INFO", "TRANSACCIONES", f"Retiro {monto} de cuenta {numero_cuenta}", cedula_usuario)
        return True
    def solicitar_prestamo(self, cedula, monto, plazo):
        cliente = self.gestor_clientes.buscar_cliente(cedula)
        if not cliente:
            print("Cliente no encontrado.")
            return None
        prestamo = self.gestor_prestamos.solicitar_prestamo(cliente, monto, plazo)
        if prestamo:
            self.auditoria.registrar("INFO", "PRESTAMOS", f"Préstamo #{prestamo.id} aprobado para {cedula}")
        return prestamo
    def generar_reportes(self):
        self.reportes.reporte_clientes()
        self.reportes.reporte_cuentas()
        self.reportes.reporte_prestamos()
        self.auditoria.registrar("INFO", "REPORTES", "Reportes generales ejecutados.")
# ─────────────────────────────────────────────────────────────
# DEMO / EJECUCIÓN DE PRUEBA
# ─────────────────────────────────────────────────────────────
def demo():
    print("=" * 60)
    print("       SISTEMA BANCARIO BANCOPLUS - DEMO")
    print("=" * 60)
    banco = BancoPlus()
    # Registrar clientes
    c1 = banco.registrar_cliente("Ana García", "1234567890", "ana@email.com", "0991234567", "pass123")
    c2 = banco.registrar_cliente("Luis Pérez", "0987654321", "luis@email.com", "0987654321", "clave456")
    c3 = banco.registrar_cliente("María López", "1122334455", "maria@email.com", "0961122334", "secreto789")
    # Abrir cuentas
    cuenta1 = banco.abrir_cuenta("1234567890", "ahorros", 1000)
    cuenta2 = banco.abrir_cuenta("1234567890", "corriente", 500)
    cuenta3 = banco.abrir_cuenta("0987654321", "ahorros", 2500)
    cuenta4 = banco.abrir_cuenta("1122334455", "ahorros", 800)
    # Operaciones
    banco.depositar(cuenta1.numero, 500, "1234567890")
    banco.retirar(cuenta1.numero, 200, "1234567890")
    banco.gestor_cuentas.transferir(cuenta3.numero, cuenta1.numero, 300)
    # Interés
    cuenta1.aplicar_interes()
    cuenta3.aplicar_interes()
    # Préstamos
    p1 = banco.solicitar_prestamo("1234567890", 5000, 24)
    p2 = banco.solicitar_prestamo("0987654321", 15000, 48)
    if p1:
        banco.gestor_prestamos.pagar_cuota(p1.id, p1.cuota_mensual)
    # Reportes
    banco.generar_reportes()
    # Auditoría
    print("\n=== RESUMEN DE AUDITORÍA ===")
    resumen = banco.auditoria.resumen()
    for nivel, conteo in resumen.items():
        print(f"  {nivel}: {conteo} eventos")
    print("\n" + "=" * 60)
    print("Demo completado exitosamente.")
    print("=" * 60)
if __name__ == "__main__":
    demo()
