from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios.configuracion_service import ConfiguracionService
from app.esquemas.configuracion_schema import ConfiguracionResponse, ConfiguracionUpdate

router = APIRouter(
    prefix="/api/configuracion",
    tags=["Configuración"]
)

@router.get("/", response_model=ConfiguracionResponse)
def obtener_configuracion(db: Session = Depends(get_db)):
    """Obtener la configuración actual de precios"""
    try:
        config = ConfiguracionService.obtener_configuracion(db)
        return config.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/", response_model=ConfiguracionResponse)
def actualizar_configuracion(datos: ConfiguracionUpdate, db: Session = Depends(get_db)):
    """Actualizar la configuración de precios (Solo administrador)"""
    try:
        # Convertir el modelo Pydantic a dict excluyendo valores None
        datos_dict = datos.dict(exclude_none=True)
        config = ConfiguracionService.actualizar_configuracion(db, datos_dict)
        return config.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))