from pydantic import BaseModel
from typing import Optional

class FacturaResponse(BaseModel):
    """Schema para respuesta de factura"""
    id: int
    vehiculo_id: int
    placa: str
    espacio_numero: int
    fecha_hora_entrada: str
    fecha_hora_salida: str
    tiempo_total_minutos: int
    costo_total: float
    detalles_cobro: Optional[str]
    fecha_generacion: str

    class Config:
        from_attributes = True

class FacturaDetallada(BaseModel):
    """Schema para factura detallada (para imprimir)"""
    placa: str
    espacio: int
    entrada: str
    salida: str
    tiempo_total: str
    costo_total: float
    detalles: str

class ReporteDiario(BaseModel):
    """Schema para reporte diario"""
    fecha: str
    total_vehiculos: int
    ingresos_total: float