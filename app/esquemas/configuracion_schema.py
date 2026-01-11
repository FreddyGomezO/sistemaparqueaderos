from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import time as dt_time
from decimal import Decimal

class ConfiguracionBase(BaseModel):
    """Schema base para configuración"""
    precio_media_hora: Optional[Decimal] = Field(None, ge=0, description="Precio por media hora")
    precio_hora_adicional: Optional[Decimal] = Field(None, ge=0, description="Precio por hora adicional")
    precio_nocturno: Optional[Decimal] = Field(None, ge=0, description="Precio nocturno (12 horas)")
    hora_inicio_nocturno: Optional[str] = Field(None, description="Hora inicio período nocturno (HH:MM)")
    hora_fin_nocturno: Optional[str] = Field(None, description="Hora fin período nocturno (HH:MM)")

    @validator('hora_inicio_nocturno', 'hora_fin_nocturno')
    def validar_formato_hora(cls, v):
        if v is not None:
            try:
                # Validar formato HH:MM
                parts = v.split(':')
                if len(parts) != 2:
                    raise ValueError('Formato debe ser HH:MM')
                hora, minuto = int(parts[0]), int(parts[1])
                if not (0 <= hora < 24 and 0 <= minuto < 60):
                    raise ValueError('Hora o minuto inválido')
            except:
                raise ValueError('Formato de hora inválido, use HH:MM')
        return v

class ConfiguracionCreate(ConfiguracionBase):
    """Schema para crear configuración"""
    pass

class ConfiguracionUpdate(ConfiguracionBase):
    """Schema para actualizar configuración"""
    pass

class ConfiguracionResponse(BaseModel):
    """Schema para respuesta de configuración"""
    id: int
    precio_media_hora: float
    precio_hora_adicional: float
    precio_nocturno: float
    hora_inicio_nocturno: str
    hora_fin_nocturno: str
    actualizado_en: Optional[str]

    class Config:
        from_attributes = True