from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.orm import joinedload  # ¡¡¡NUEVO IMPORT!!!
from datetime import datetime
from app.modelos.vehiculo_estacionado import VehiculoEstacionado
from app.modelos.historial_factura import HistorialFactura
from app.servicios.configuracion_service import ConfiguracionService
from app.servicios.calculo_service import CalculoService

class VehiculoService:
    """Servicio para manejar vehículos estacionados"""
    
    @staticmethod
    def obtener_espacios(db: Session):
        """
        Obtener el estado de los 15 espacios
        
        Returns:
            Lista de diccionarios con el estado de cada espacio
        """
        vehiculos_activos = db.query(VehiculoEstacionado).filter_by(estado='activo').all()
        espacios = []
        for i in range(1, 16):
            vehiculo = next((v for v in vehiculos_activos if v.espacio_numero == i), None)
            
            # 🐛 DEBUG de cada espacio
            espacio_debug = {
                'numero': i,
                'ocupado': vehiculo is not None,
                'placa': vehiculo.placa if vehiculo else None,
                'entrada': vehiculo.fecha_hora_entrada.isoformat() if vehiculo else None,
                'es_nocturno': vehiculo.es_nocturno if vehiculo else False  # ✅ IMPORTANTE
            }
            
            print(f"  Espacio {i}: ocupado={espacio_debug['ocupado']}, " +
                  f"placa={espacio_debug['placa']}, " +
                  f"es_nocturno={espacio_debug['es_nocturno']}")
            
            espacios.append(espacio_debug)
        
        return espacios
    
    @staticmethod
    def registrar_entrada(db: Session, placa: str, espacio_numero: int, es_nocturno: bool = False):
        """
        Registrar la entrada de un vehículo
        
        Args:
            db: Sesión de base de datos
            placa: Placa del vehículo
            espacio_numero: Número del espacio (1-15)
            es_nocturno: Si el vehículo pagará tarifa nocturna
        """
        placa = placa.upper().strip()
        
        # Validar espacio
        if not (1 <= espacio_numero <= 15):
            raise ValueError('El número de espacio debe estar entre 1 y 15')
        
        # Verificar si el espacio está ocupado
        espacio_ocupado = db.query(VehiculoEstacionado).filter_by(
            espacio_numero=espacio_numero,
            estado='activo'
        ).first()
        
        if espacio_ocupado:
            raise ValueError(f'El espacio {espacio_numero} ya está ocupado')
        
        # Verificar si el vehículo ya está estacionado
        vehiculo_activo = db.query(VehiculoEstacionado).filter_by(
            placa=placa,
            estado='activo'
        ).first()
        
        if vehiculo_activo:
            raise ValueError(f'El vehículo {placa} ya está estacionado en el espacio {vehiculo_activo.espacio_numero}')
        
        # Crear nuevo registro CON EL CAMPO es_nocturno
        vehiculo = VehiculoEstacionado(
            placa=placa,
            espacio_numero=espacio_numero,
            fecha_hora_entrada=datetime.now(),
            estado='activo',
            es_nocturno=es_nocturno  # NUEVO
        )
        
        db.add(vehiculo)
        db.commit()
        db.refresh(vehiculo)
        
        return vehiculo
    
    @staticmethod
    def registrar_salida(db: Session, placa: str):
        """
        Registrar la salida de un vehículo y calcular el costo
        """
        placa = placa.upper().strip()
        
        # Buscar vehículo activo
        vehiculo = db.query(VehiculoEstacionado).filter_by(
            placa=placa,
            estado='activo'
        ).first()
        
        if not vehiculo:
            raise ValueError('Vehículo no encontrado o ya salió')
        
        # Obtener configuración
        config = ConfiguracionService.obtener_configuracion(db)
        
        # Calcular costo (pasar es_nocturno)
        fecha_salida = datetime.now()
        calculo = CalculoService.calcular_costo(
            vehiculo.fecha_hora_entrada,
            fecha_salida,
            config,
            vehiculo.es_nocturno  # NUEVO: pasar si es nocturno
        )
        
        # Actualizar vehículo
        vehiculo.fecha_hora_salida = fecha_salida
        vehiculo.costo_total = calculo['costo']
        vehiculo.estado = 'finalizado'
        
        # Crear factura en historial
        factura = HistorialFactura(
            vehiculo_id=vehiculo.id,
            placa=vehiculo.placa,
            espacio_numero=vehiculo.espacio_numero,
            fecha_hora_entrada=vehiculo.fecha_hora_entrada,
            fecha_hora_salida=fecha_salida,
            tiempo_total_minutos=calculo['minutos'],
            costo_total=calculo['costo'],
            detalles_cobro=calculo['detalles']
        )
        
        db.add(factura)
        db.commit()
        db.refresh(vehiculo)
        db.refresh(factura)
        
        return {
            'vehiculo': vehiculo,
            'factura': factura,
            'tiempo_formateado': CalculoService.formatear_tiempo(calculo['minutos'])
        }
    
    @staticmethod
    def buscar_vehiculo(db: Session, placa: str):
        """
        Buscar un vehículo activo y calcular costo estimado
        
        Args:
            db: Sesión de base de datos
            placa: Placa del vehículo
        
        Returns:
            Diccionario con vehiculo y costo estimado
        
        Raises:
            ValueError: Si el vehículo no está encontrado
        """
        placa = placa.upper().strip()
        
        vehiculo = db.query(VehiculoEstacionado).filter_by(
            placa=placa,
            estado='activo'
        ).first()
        
        if not vehiculo:
            raise ValueError('Vehículo no encontrado')
        
        # Calcular costo estimado
        config = ConfiguracionService.obtener_configuracion(db)
        print(f"Configuración precio_nocturno: {config.precio_nocturno}")
        
        # 🔍 IMPORTANTE: Pasar es_nocturno al cálculo
        calculo = CalculoService.calcular_costo(
            vehiculo.fecha_hora_entrada,
            datetime.now(),
            config,
            vehiculo.es_nocturno  # ✅ ¡AQUÍ ESTÁ EL CAMBIO!
        )
        
        
        return {
            'vehiculo': vehiculo,
            'costo_estimado': calculo['costo'],
            'tiempo_estimado': CalculoService.formatear_tiempo(calculo['minutos']),
            'detalles': calculo['detalles']
        }
    
    @staticmethod
    def obtener_historial(db: Session, fecha: str = None, limite: int = 50):
        """
        Obtener el historial de facturas
        
        Args:
            db: Sesión de base de datos
            fecha: Fecha en formato YYYY-MM-DD (opcional)
            limite: Número máximo de registros
        
        Returns:
            Lista de HistorialFactura
        """
        # ¡¡¡CORRECCIÓN: Usar joinedload para cargar la relación!!!
        query = db.query(HistorialFactura).options(
            joinedload(HistorialFactura.vehiculo)  # ¡¡¡ESTO ES LO QUE FALTABA!!!
        )
        
        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                query = query.filter(func.date(HistorialFactura.fecha_generacion) == fecha_obj)
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")
        
        historial = query.order_by(HistorialFactura.fecha_generacion.desc()).limit(limite).all()
        
        # Depuración: Verificar si se cargó la relación
        if historial:
            print(f"🔍 Depuración Historial - Primer registro:")
            print(f"   Factura ID: {historial[0].id}")
            print(f"   Placa: {historial[0].placa}")
            print(f"   Vehículo cargado: {historial[0].vehiculo is not None}")
            if historial[0].vehiculo:
                print(f"   es_nocturno: {historial[0].vehiculo.es_nocturno}")
                print(f"   to_dict() incluye es_nocturno?: {'es_nocturno' in historial[0].to_dict()}")
            else:
                print(f"   ⚠️ ERROR: Vehículo NO cargado para factura {historial[0].id}")
        
        return historial
    
    @staticmethod
    def obtener_reporte_diario(db: Session, fecha: str = None):
        """
        Obtener reporte de ingresos del día
        
        Args:
            db: Sesión de base de datos
            fecha: Fecha en formato YYYY-MM-DD (opcional)
        
        Returns:
            Diccionario con total de vehículos e ingresos
        """
        if fecha:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        else:
            fecha_obj = datetime.now().date()
        
        resultado = db.query(
            func.count(HistorialFactura.id).label('total_vehiculos'),
            func.sum(HistorialFactura.costo_total).label('ingresos_total')
        ).filter(
            func.date(HistorialFactura.fecha_generacion) == fecha_obj
        ).first()
        
        return {
            'fecha': fecha_obj.isoformat(),
            'total_vehiculos': resultado.total_vehiculos or 0,
            'ingresos_total': float(resultado.ingresos_total or 0)
        }