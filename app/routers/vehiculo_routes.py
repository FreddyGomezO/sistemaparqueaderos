from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config import get_db
from app.servicios.vehiculo_service import VehiculoService
from app.esquemas.vehiculo_schema import (
    VehiculoEntrada, 
    VehiculoSalida, 
    VehiculoResponse,
    VehiculoConEstimacion,
    EspacioResponse
)
from app.esquemas.factura_schema import FacturaDetallada

router = APIRouter(
    prefix="/api/vehiculos",
    tags=["Vehículos"]
)

@router.get("/espacios", response_model=List[EspacioResponse])
def obtener_espacios(db: Session = Depends(get_db)):
    """
    Obtener el estado de los 15 espacios de estacionamiento
    
    Retorna una lista con el estado de cada espacio (ocupado/libre)
    """
    try:
        espacios = VehiculoService.obtener_espacios(db)
        return espacios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/entrada", response_model=VehiculoResponse, status_code=201)
def registrar_entrada(datos: VehiculoEntrada, db: Session = Depends(get_db)):
    """
    Registrar la entrada de un vehículo
    
    Args:
        datos: Placa, número de espacio y si es nocturno
    
    Returns:
        Información del vehículo registrado
    """
    try:
        vehiculo = VehiculoService.registrar_entrada(
            db, 
            datos.placa, 
            datos.espacio_numero,
            datos.es_nocturno  # NUEVO
        )
        return vehiculo.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/salida")
def registrar_salida(datos: VehiculoSalida, db: Session = Depends(get_db)):
    """
    Registrar la salida de un vehículo y generar factura
    
    Args:
        datos: Placa del vehículo
    
    Returns:
        Factura con el costo total y detalles
    """
    try:
        resultado = VehiculoService.registrar_salida(db, datos.placa)
        
        return {
            "success": True,
            "message": "Salida registrada exitosamente",
            "factura": {
                "placa": resultado['vehiculo'].placa,
                "espacio": resultado['vehiculo'].espacio_numero,
                "entrada": resultado['vehiculo'].fecha_hora_entrada.isoformat(),
                "salida": resultado['vehiculo'].fecha_hora_salida.isoformat(),
                "tiempo_total": resultado['tiempo_formateado'],
                "costo_total": float(resultado['vehiculo'].costo_total),
                "detalles": resultado['factura'].detalles_cobro
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/buscar/{placa}")
def buscar_vehiculo(placa: str, db: Session = Depends(get_db)):
    """
    Buscar un vehículo activo y mostrar costo estimado
    
    Args:
        placa: Placa del vehículo a buscar
    
    Returns:
        Información del vehículo con costo estimado actual
    """
    try:
        resultado = VehiculoService.buscar_vehiculo(db, placa)
        
        return {
            "success": True,
            "data": {
                **resultado['vehiculo'].to_dict(),
                "costo_estimado": resultado['costo_estimado'],
                "tiempo_estimado": resultado['tiempo_estimado'],
                "detalles": resultado['detalles']
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historial")
def obtener_historial(fecha: str = None, limite: int = 50, db: Session = Depends(get_db)):
    """
    Obtener el historial de facturas
    
    Args:
        fecha: Fecha en formato YYYY-MM-DD (opcional)
        limite: Número máximo de registros a retornar (default: 50)
    
    Returns:
        Lista de facturas del historial
    """
    try:
        historial = VehiculoService.obtener_historial(db, fecha, limite)
        return {
            "success": True,
            "data": [factura.to_dict() for factura in historial]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    """Verificar que el servicio de vehículos está funcionando"""
    return {
        "success": True,
        "message": "🚗 Servicio de vehículos funcionando correctamente"
    }