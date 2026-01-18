
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class VehiculoBase(BaseModel):
    """Schema base para vehículos"""
    placa: str = Field(..., min_length=1, max_length=20, description="Placa del vehículo")

    @validator('placa')
    def validar_placa(cls, v):
        """Convertir placa a mayúsculas y eliminar espacios"""
        return v.upper().strip()


class VehiculoEntrada(VehiculoBase):
    """Schema para registrar entrada de un vehículo"""
    espacio_numero: int = Field(..., ge=1, le=15, description="Número de espacio (1-15)")
    # NUEVO CAMPO: indica si es entrada nocturna
    es_nocturno: bool = Field(False, description="Indica si el vehículo pagará tarifa nocturna")

class VehiculoSalida(BaseModel):
    """Schema para registrar salida de un vehículo"""
    placa: str = Field(..., min_length=1, max_length=20, description="Placa del vehículo")

    @validator('placa')
    def validar_placa(cls, v):
        """Convertir placa a mayúsculas y eliminar espacios"""
        return v.upper().strip()

class VehiculoResponse(BaseModel):
    """Schema para respuesta de vehículo"""
    id: int
    placa: str
    espacio_numero: int
    fecha_hora_entrada: str
    fecha_hora_salida: Optional[str]
    costo_total: Optional[float]
    estado: str
    creado_en: str

    class Config:
        from_attributes = True

class VehiculoConEstimacion(VehiculoResponse):
    """Schema para vehículo con costo estimado"""
    costo_estimado: float
    tiempo_estimado: str
    detalles: str

class EspacioResponse(BaseModel):
    """Schema para respuesta de espacios"""
    numero: int
    ocupado: bool
    placa: Optional[str] = None
    entrada: Optional[str] = None