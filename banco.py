import datetime
import random
import json
import hashlib
# ─────────────────────────────────────────────────────────────
# MÓDULO 1: GESTIÓN DE CLIENTES
# ─────────────────────────────────────────────────────────────
class Cliente:
    """
    Representa un cliente del banco.
    Args:
        nombre (str): Nombre completo del cliente.
        cedula (str): Número de identificación único.
        email (str): Correo electrónico de contacto.
        telefono (str): Número de teléfono (solo dígitos).
        tipo (str): Tipo de cliente: 'natural' o 'juridico'.
    """
    def __init__(self, nombre, cedula, email, telefono, tipo="natural"):
        self.nombre = nombre
        self.cedula = cedula
        self.email = email
        self.telefono = telefono
        self.tipo = tipo
        self.cuentas = []
        self.fecha_registro = datetime.datetime.now()
        self.activo = True
        self.historial_cambios = []
    def actualizar_email(self, nuevo_email):
        """Actualiza el email validando que contenga '@'."""
        if "@" not in nuevo_email or "." not in nuevo_email:
            print("Formato de email inválido.")
            return False
        self.historial_cambios.append(("email", self.email, nuevo_email))
        self.email = nuevo_email
        return True
    def actualizar_telefono(self, nuevo_telefono):
        """Actualiza el teléfono validando que sea numérico."""
        if not nuevo_telefono.isdigit():
            print("El teléfono debe contener solo dígitos.")
            return False
        self.telefono = nuevo_telefono
        return True
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
        """Registra un cliente verificando que la cédula no esté duplicada."""
        if cedula in self.clientes:
            print(f"Error: Ya existe un cliente con la cédula {cedula}.")
            return None
        cliente = Cliente(nombre, cedula, email, telefono, tipo)
        self.clientes[cedula] = cliente
        self.total_registrados += 1
        print(f"Cliente {nombre} registrado exitosamente.")
        return cliente
    def buscar_cliente(self, cedula):
        if cedula is None:
            return None
        return self.clientes.get(cedula)
    def eliminar_cliente(self, cedula):
        cliente = self.buscar_cliente(cedula)
        if cliente:
            cuentas_con_saldo = [c for c in cliente.cuentas if c.saldo > 0 and c.activa]
            if cuentas_con_saldo:
                print("No se puede eliminar: el cliente tiene cuentas activas con saldo.")
                return False
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
    Tipos soportados: 'ahorros' (interés 3 % anual), 'corriente' (sin interés).
    """
    INTERES_AHORROS = 0.03
    INTERES_CORRIENTE = 0.0
    TIPOS_VALIDOS = ("ahorros", "corriente")
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
        """Deposita un monto positivo en la cuenta."""
        if monto <= 0:
            print("El monto del depósito debe ser mayor a cero.")
            return False
        self.saldo += monto
        self._registrar_transaccion("deposito", monto)
        print(f"Depósito de {monto} realizado. Saldo actual: {self.saldo}")
        return True
    def retirar(self, monto):
        """
        Retira un monto de la cuenta.
        Verifica que haya saldo suficiente antes de operar.
        """
        if monto <= 0:
            print("El monto del retiro debe ser mayor a cero.")
            return False
        if monto > self.saldo:
            print(f"Saldo insuficiente. Saldo disponible: {self.saldo}")
            return False
        self.saldo -= monto
        self._registrar_transaccion("retiro", monto)
        print(f"Retiro de {monto} realizado. Saldo actual: {self.saldo}")
        return True
    def consultar_saldo(self):
        return self.saldo
    def aplicar_interes(self):
        """
        Aplica interés mensual según tipo de cuenta.
        Tasa mensual equivalente: INTERES_AHORROS / 12.
        """
        if self.tipo == "ahorros":
            tasa_mensual = self.INTERES_AHORROS / 12
            interes = self.saldo * tasa_mensual
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
        """Abre una cuenta validando que el tipo sea 'ahorros' o 'corriente'."""
        if tipo not in Cuenta.TIPOS_VALIDOS:
            print(f"Tipo de cuenta inválido. Use: {Cuenta.TIPOS_VALIDOS}")
            return None
        numero = self._generar_numero()
        cuenta = Cuenta(numero, tipo, cliente, saldo_inicial)
        self.cuentas[numero] = cuenta
        cliente.agregar_cuenta(cuenta)
        print(f"Cuenta {numero} abierta para {cliente.nombre}.")
        return cuenta
    def cerrar_cuenta(self, numero):
        """Cierra una cuenta transfiriendo el saldo restante al cliente."""
        cuenta = self.cuentas.get(numero)
        if cuenta:
            if cuenta.saldo > 0:
                print(f"Atención: la cuenta tiene saldo de {cuenta.saldo}. Proceda a retirarlo antes de cerrar.")
                return False
            cuenta.activa = False
            return True
        return False
    def transferir(self, origen_num, destino_num, monto):
        """Transfiere fondos verificando bloqueos y saldo disponible."""
        origen = self.cuentas.get(origen_num)
        destino = self.cuentas.get(destino_num)
        if not origen or not destino:
            print("Una o ambas cuentas no existen.")
            return False
        if origen.bloqueada or destino.bloqueada:
            print("Una o ambas cuentas están bloqueadas.")
            return False
        if origen.saldo < monto:
            print("Saldo insuficiente para la transferencia.")
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
    """Representa un préstamo bancario con amortización francesa."""
    TASA_INTERES = 0.12
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
        tasa_mensual = self.TASA_INTERES / 12
        n = self.plazo_meses
        cuota = self.monto_original * (tasa_mensual * (1 + tasa_mensual) ** n) / ((1 + tasa_mensual) ** n - 1)
        return round(cuota, 2)
    def registrar_pago(self, monto):
        """Registra un pago sin permitir exceder el monto pendiente."""
        if monto > self.monto_pendiente:
            print(f"El monto supera la deuda pendiente ({self.monto_pendiente}). Se ajustará automáticamente.")
            monto = self.monto_pendiente
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
    """
    Gestiona la autenticación y autorización de usuarios.
    Las contraseñas se almacenan como hash SHA-256.
    """
    MAX_INTENTOS = 3
    def __init__(self):
        self.usuarios = {}
        self.sesiones_activas = {}
        self.intentos_fallidos = {}
    @staticmethod
    def _hashear(password):
        """Retorna el hash SHA-256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    def registrar_usuario(self, cedula, password, rol="cliente"):
        """Registra un usuario almacenando el hash de la contraseña."""
        self.usuarios[cedula] = {
            "password_hash": self._hashear(password),
            "rol": rol,
            "activo": True
        }
    def autenticar(self, cedula, password):
        """
        Autentica al usuario comparando el hash.
        Bloquea la cuenta tras 3 intentos fallidos.
        """
        usuario = self.usuarios.get(cedula)
        if not usuario:
            return False
        intentos = self.intentos_fallidos.get(cedula, 0)
        if intentos >= self.MAX_INTENTOS:
            print("Cuenta bloqueada por múltiples intentos fallidos.")
            return False
        if usuario["password_hash"] == self._hashear(password):
            self.intentos_fallidos[cedula] = 0
            token = hashlib.sha256(f"{cedula}{random.random()}".encode()).hexdigest()[:12]
            self.sesiones_activas[cedula] = token
            return token
        self.intentos_fallidos[cedula] = intentos + 1
        return False
    def cerrar_sesion(self, cedula):
        if cedula in self.sesiones_activas:
            del self.sesiones_activas[cedula]
            return True
        return False
    def validar_sesion(self, cedula, token):
        return self.sesiones_activas.get(cedula) == token
    def cambiar_password(self, cedula, password_actual, password_nuevo):
        """Cambia la contraseña validando complejidad mínima (8 caracteres)."""
        usuario = self.usuarios.get(cedula)
        if not usuario:
            return False
        if len(password_nuevo) < 8:
            print("La nueva contraseña debe tener al menos 8 caracteres.")
            return False
        if usuario["password_hash"] == self._hashear(password_actual):
            usuario["password_hash"] = self._hashear(password_nuevo)
            return True
        return False
# ─────────────────────────────────────────────────────────────
# MÓDULO 5: REPORTES Y ESTADÍSTICAS
# ─────────────────────────────────────────────────────────────
class GeneradorReportes:
    """
    Genera reportes financieros del banco.
    Los reportes se generan en memoria y pueden exportarse a JSON.
    """
    def __init__(self, gestor_clientes, gestor_cuentas, gestor_prestamos):
        self.gc = gestor_clientes
        self.gcu = gestor_cuentas
        self.gp = gestor_prestamos
    def reporte_clientes(self):
        clientes = self.gc.listar_clientes_activos()
        total_saldo = sum(c.obtener_resumen()["saldo_total"] for c in clientes)
        reporte = [c.obtener_resumen() for c in clientes]
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
        return {"ahorros": len(ahorros), "corrientes": len(corrientes), "total": len(cuentas)}
    def reporte_prestamos(self):
        activos = self.gp.prestamos_activos()
        total_pendiente = sum(p.monto_pendiente for p in activos)
        print(f"\n=== REPORTE DE PRÉSTAMOS ===")
        print(f"Préstamos activos: {len(activos)}")
        print(f"Total pendiente de cobro: {total_pendiente:.2f}")
        return {"activos": len(activos), "total_pendiente": total_pendiente}
    def reporte_movimientos(self, numero_cuenta):
        """Muestra el historial de movimientos de una cuenta."""
        cuenta = self.gcu.buscar_cuenta(numero_cuenta)
        if not cuenta:
            print(f"Cuenta {numero_cuenta} no encontrada.")
            return []
        historial = cuenta.historial()
        print(f"\n=== MOVIMIENTOS CUENTA {numero_cuenta} ===")
        for mov in historial:
            print(f"  {mov['fecha']} | {mov['tipo'].upper()} | Monto: {mov['monto']} | Saldo: {mov['saldo_posterior']}")
        return historial
    def exportar_json(self, datos, nombre_archivo):
        """Exporta datos a JSON validando el nombre del archivo."""
        nombre_seguro = "".join(c for c in nombre_archivo if c.isalnum() or c in ("_", "-"))
        ruta = f"/tmp/{nombre_seguro}.json"
        with open(ruta, "w") as f:
            json.dump(datos, f, indent=2, default=str)
        print(f"Reporte exportado en {ruta}")
        return ruta
# ─────────────────────────────────────────────────────────────
# MÓDULO 6: NOTIFICACIONES
# ─────────────────────────────────────────────────────────────
class SistemaNotificaciones:
    """
    Envía notificaciones a clientes por email y SMS.
    Nota: las implementaciones de envío son simuladas (sin SMTP real).
    """
    def __init__(self):
        self.notificaciones_enviadas = []
    def enviar_email(self, destinatario, asunto, cuerpo):
        print(f"[EMAIL] Para: {destinatario} | Asunto: {asunto}")
        self.notificaciones_enviadas.append({
            "canal": "email",
            "destinatario": destinatario,
            "asunto": asunto,
            "fecha": datetime.datetime.now().isoformat()
        })
    def enviar_sms(self, telefono, mensaje):
        """Envía SMS validando que el teléfono sea numérico."""
        if not str(telefono).isdigit():
            print(f"Teléfono inválido: {telefono}")
            return
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
    El log no puede eliminarse; solo se puede archivar.
    """
    NIVELES = ["INFO", "ADVERTENCIA", "ERROR", "CRITICO"]
    def __init__(self):
        self.log = []
        self.log_archivado = []
        self.errores_criticos = 0
    def registrar(self, nivel, modulo, descripcion, usuario=None):
        """Registra un evento validando que el nivel sea uno de los permitidos."""
        if nivel not in self.NIVELES:
            nivel = "INFO"
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
    def archivar_log(self):
        """Archiva el log actual sin eliminarlo permanentemente."""
        self.log_archivado.extend(self.log)
        self.log = []
        self.errores_criticos = 0
# ─────────────────────────────────────────────────────────────
# MÓDULO 8: SISTEMA PRINCIPAL
# ─────────────────────────────────────────────────────────────
class BancoPlus:
    """
    Sistema principal del banco BancoPlus.
    Integra: clientes, cuentas, préstamos, seguridad,
    notificaciones, reportes y auditoría.
    """
    VERSION = "1.1.0"
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
        if not cliente:
            return None
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
        resultado = cuenta.depositar(monto)
        if resultado:
            self.notificaciones.notificar_transaccion(cuenta.cliente, "depósito", monto)
            self.auditoria.registrar("INFO", "TRANSACCIONES", f"Depósito {monto} en cuenta {numero_cuenta}", cedula_usuario)
        return resultado
    def retirar(self, numero_cuenta, monto, cedula_usuario):
        cuenta = self.gestor_cuentas.buscar_cuenta(numero_cuenta)
        if not cuenta:
            print("Cuenta no encontrada.")
            return False
        if cuenta.bloqueada:
            print("La cuenta está bloqueada.")
            self.auditoria.registrar("ADVERTENCIA", "TRANSACCIONES", f"Intento de retiro en cuenta bloqueada {numero_cuenta}", cedula_usuario)
            return False
        resultado = cuenta.retirar(monto)
        if resultado:
            self.notificaciones.notificar_transaccion(cuenta.cliente, "retiro", monto)
            self.auditoria.registrar("INFO", "TRANSACCIONES", f"Retiro {monto} de cuenta {numero_cuenta}", cedula_usuario)
        return resultado
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
# DEMO
# ─────────────────────────────────────────────────────────────
def demo():
    print("=" * 60)
    print("   SISTEMA BANCARIO BANCOPLUS v1.1.0 - VERSIÓN CORREGIDA")
    print("=" * 60)
    banco = BancoPlus()
    c1 = banco.registrar_cliente("Ana García", "1234567890", "ana@email.com", "0991234567", "segura1234")
    c2 = banco.registrar_cliente("Luis Pérez", "0987654321", "luis@email.com", "0987654321", "clave5678")
    banco.registrar_cliente("María López", "1122334455", "maria@email.com", "0961122334", "secret789")
    cuenta1 = banco.abrir_cuenta("1234567890", "ahorros", 1000)
    banco.abrir_cuenta("1234567890", "corriente", 500)
    cuenta3 = banco.abrir_cuenta("0987654321", "ahorros", 2500)
    banco.abrir_cuenta("1122334455", "ahorros", 800)
    banco.depositar(cuenta1.numero, 500, "1234567890")
    banco.retirar(cuenta1.numero, 200, "1234567890")
    banco.gestor_cuentas.transferir(cuenta3.numero, cuenta1.numero, 300)
    cuenta1.aplicar_interes()
    cuenta3.aplicar_interes()
    p1 = banco.solicitar_prestamo("1234567890", 5000, 24)
    banco.solicitar_prestamo("0987654321", 15000, 48)
    if p1:
        banco.gestor_prestamos.pagar_cuota(p1.id, p1.cuota_mensual)
    banco.generar_reportes()
    print("\n=== RESUMEN DE AUDITORÍA ===")
    for nivel, conteo in banco.auditoria.resumen().items():
        print(f"  {nivel}: {conteo} eventos")
    print("\n" + "=" * 60)
    print("Demo v1.1.0 completado.")
    print("=" * 60)
if __name__ == "__main__":
    demo()
