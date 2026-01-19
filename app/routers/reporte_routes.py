from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from app.config import get_db
from app.esquemas.factura_schema import ReporteDiario, ReporteDetalladoSchema

router = APIRouter(
    prefix="/api/reportes",
    tags=["Reportes"]
)

@router.get("/diario", response_model=ReporteDiario)
def obtener_reporte_diario(fecha: str = None, db: Session = Depends(get_db)):
    """
    Obtener reporte de ingresos diarios
    - Total vehículos: Los que ENTRARON ese día
    - Ingresos: Los que SALIERON ese día (finalizados)
    """
    try:
        if fecha is None:
            fecha_actual = date.today()
        else:
            fecha_actual = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        inicio_dia = datetime.combine(fecha_actual, datetime.min.time())
        fin_dia = datetime.combine(fecha_actual + timedelta(days=1), datetime.min.time())
        
        from app.modelos.vehiculo_estacionado import VehiculoEstacionado
        
        # Total vehículos: Los que ENTRARON este día
        vehiculos_entraron = db.query(VehiculoEstacionado).filter(
            VehiculoEstacionado.fecha_hora_entrada >= inicio_dia,
            VehiculoEstacionado.fecha_hora_entrada < fin_dia
        ).count()
        
        # Ingresos: Solo de los que SALIERON este día
        vehiculos_salieron = db.query(VehiculoEstacionado).filter(
            VehiculoEstacionado.estado == "finalizado",
            VehiculoEstacionado.fecha_hora_salida.isnot(None),
            VehiculoEstacionado.fecha_hora_salida >= inicio_dia,
            VehiculoEstacionado.fecha_hora_salida < fin_dia
        ).all()
        
        ingresos_total = sum(v.costo_total or 0 for v in vehiculos_salieron)
        
        return ReporteDiario(
            fecha=fecha_actual.strftime("%Y-%m-%d"),
            total_vehiculos=vehiculos_entraron,
            ingresos_total=float(ingresos_total)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detallado", response_model=ReporteDetalladoSchema)
def obtener_reporte_detallado(fecha: str = None, db: Session = Depends(get_db)):
    """
    Reporte detallado para gráficos con DATOS REALES
    - Estadísticas de vehículos: Los que ENTRARON ese día
    - Ingresos: Los que SALIERON ese día
    """
    try:
        if fecha is None:
            fecha_actual = date.today()
        else:
            fecha_actual = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        inicio_dia = datetime.combine(fecha_actual, datetime.min.time())
        fin_dia = datetime.combine(fecha_actual + timedelta(days=1), datetime.min.time())
        
        from app.modelos.vehiculo_estacionado import VehiculoEstacionado
        
        # Vehículos que ENTRARON este día (para estadísticas)
        vehiculos_entraron = db.query(VehiculoEstacionado).filter(
            VehiculoEstacionado.fecha_hora_entrada >= inicio_dia,
            VehiculoEstacionado.fecha_hora_entrada < fin_dia
        ).all()
        
        # Vehículos que SALIERON este día (para ingresos)
        vehiculos_salieron = db.query(VehiculoEstacionado).filter(
            VehiculoEstacionado.estado == "finalizado",
            VehiculoEstacionado.fecha_hora_salida.isnot(None),
            VehiculoEstacionado.fecha_hora_salida >= inicio_dia,
            VehiculoEstacionado.fecha_hora_salida < fin_dia
        ).all()
        
        # ===== CALCULAR ESTADÍSTICAS =====
        
        # 1. Nocturnos vs Diurnos (de los que ENTRARON)
        nocturnos = sum(1 for v in vehiculos_entraron if v.es_nocturno)
        diurnos = len(vehiculos_entraron) - nocturnos
        
        # Ingresos (de los que SALIERON)
        ingresos_nocturnos = sum(
            v.costo_total or 0 
            for v in vehiculos_salieron 
            if v.es_nocturno
        )
        ingresos_diurnos = sum(
            v.costo_total or 0 
            for v in vehiculos_salieron 
            if not v.es_nocturno
        )
        
        # 2. Horas pico (por hora de ENTRADA)
        horas_pico_dict = {}
        for v in vehiculos_entraron:
            hora = v.fecha_hora_entrada.strftime("%H:00")
            horas_pico_dict[hora] = horas_pico_dict.get(hora, 0) + 1
        
        horas_pico = [
            {"hora": hora, "cantidad": cantidad}
            for hora, cantidad in sorted(horas_pico_dict.items())
        ]
        
        # 3. Espacios más utilizados (de los que ENTRARON)
        espacios_dict = {}
        for v in vehiculos_entraron:
            espacios_dict[v.espacio_numero] = espacios_dict.get(v.espacio_numero, 0) + 1
        
        espacios_mas_utilizados = [
            {"espacio": espacio, "usos": usos}
            for espacio, usos in sorted(espacios_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # 4. Distribución de tiempo (solo de los que SALIERON)
        distribucion = {
            "menos_1h": 0,
            "entre_1h_3h": 0,
            "entre_3h_6h": 0,
            "mas_6h": 0,
            "nocturnos": 0
        }
        
        for v in vehiculos_salieron:
            if v.es_nocturno:
                distribucion["nocturnos"] += 1
                continue
                
            if v.fecha_hora_salida:
                minutos = (v.fecha_hora_salida - v.fecha_hora_entrada).total_seconds() / 60
                
                if minutos < 60:
                    distribucion["menos_1h"] += 1
                elif minutos < 180:
                    distribucion["entre_1h_3h"] += 1
                elif minutos < 360:
                    distribucion["entre_3h_6h"] += 1
                else:
                    distribucion["mas_6h"] += 1
        
        return ReporteDetalladoSchema(
            fecha=fecha_actual.strftime("%Y-%m-%d"),
            vehiculos_nocturnos=nocturnos,
            vehiculos_diurnos=diurnos,
            ingresos_nocturnos=float(ingresos_nocturnos),
            ingresos_diurnos=float(ingresos_diurnos),
            horas_pico=horas_pico,
            espacios_mas_utilizados=espacios_mas_utilizados,
            distribucion_tiempo=distribucion
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    return {
        "success": True,
        "message": "📊 Servicio de reportes funcionando correctamente"
    }