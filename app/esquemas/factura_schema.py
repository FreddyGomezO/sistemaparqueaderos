from pydantic import BaseModel
from typing import Optional

# ========== SCHEMAS DE ENTRADA/SALIDA ==========

class EntradaSchema(BaseModel):
    """Schema para registrar entrada de vehículo"""
    placa: str
    espacio_numero: int
    es_nocturno: bool = False
    
    class Config:
        from_attributes = True

class SalidaSchema(BaseModel):
    """Schema para registrar salida de vehículo"""
    placa: str
    
    class Config:
        from_attributes = True

# ========== SCHEMAS DE FACTURA ==========

class FacturaResponse(BaseModel):
    """Schema para respuesta de factura básica"""
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
    es_nocturno: bool

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
    es_nocturno: bool

    class Config:
        from_attributes = True

# ========== SCHEMAS DE REPORTES ==========

class ReporteDiario(BaseModel):
    """Schema para reporte diario básico"""
    fecha: str
    total_vehiculos: int
    ingresos_total: float

    class Config:
        from_attributes = True

class HoraPicoSchema(BaseModel):
    """Schema para horas pico"""
    hora: str
    cantidad: int

class EspacioUtilizadoSchema(BaseModel):
    """Schema para espacios utilizados"""
    espacio: int
    usos: int

class DistribucionTiempoSchema(BaseModel):
    """Schema para distribución de tiempo de estacionamiento"""
    menos_1h: int
    entre_1h_3h: int
    entre_3h_6h: int
    mas_6h: int
    nocturnos: int

class ReporteDetalladoSchema(BaseModel):
    """Schema para reporte detallado con gráficos"""
    fecha: str
    vehiculos_nocturnos: int
    vehiculos_diurnos: int
    ingresos_nocturnos: float
    ingresos_diurnos: float
    horas_pico: list[HoraPicoSchema]
    espacios_mas_utilizados: list[EspacioUtilizadoSchema]
    distribucion_tiempo: DistribucionTiempoSchema

    class Config:
        from_attributes = True