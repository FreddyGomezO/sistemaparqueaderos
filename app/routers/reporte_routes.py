from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios.vehiculo_service import VehiculoService
from app.esquemas.factura_schema import ReporteDiario

router = APIRouter(
    prefix="/api/reportes",
    tags=["Reportes"]
)

@router.get("/diario", response_model=ReporteDiario)
def obtener_reporte_diario(fecha: str = None, db: Session = Depends(get_db)):
    """
    Obtener reporte de ingresos diarios
    
    Args:
        fecha: Fecha en formato YYYY-MM-DD (opcional, por defecto hoy)
    """
    try:
        reporte = VehiculoService.obtener_reporte_diario(db, fecha)
        return reporte
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    """Verificar que el servicio de reportes está funcionando"""
    return {
        "success": True,
        "message": "📊 Servicio de reportes funcionando correctamente"
    }