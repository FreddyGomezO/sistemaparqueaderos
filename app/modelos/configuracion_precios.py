from sqlalchemy import Column, Integer, Numeric, Time, DateTime
from datetime import datetime, time as dt_time
from app.config import Base

class ConfiguracionPrecios(Base):
    """Modelo para la configuración de precios del parqueadero"""
    __tablename__ = 'configuracion_precios'
    
    id = Column(Integer, primary_key=True, index=True)
    precio_media_hora = Column(Numeric(10, 2), nullable=False, default=0.50)
    precio_hora_adicional = Column(Numeric(10, 2), nullable=False, default=1.00)
    precio_nocturno = Column(Numeric(10, 2), nullable=False, default=10.00)
    hora_inicio_nocturno = Column(Time, nullable=False, default=dt_time(19, 0))
    hora_fin_nocturno = Column(Time, nullable=False, default=dt_time(7, 0))
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convertir el modelo a diccionario"""
        return {
            'id': self.id,
            'precio_media_hora': float(self.precio_media_hora),
            'precio_hora_adicional': float(self.precio_hora_adicional),
            'precio_nocturno': float(self.precio_nocturno),
            'hora_inicio_nocturno': str(self.hora_inicio_nocturno),
            'hora_fin_nocturno': str(self.hora_fin_nocturno),
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None
        }