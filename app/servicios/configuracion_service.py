from sqlalchemy.orm import Session
from app.modelos.configuracion_precios import ConfiguracionPrecios
from datetime import datetime

class ConfiguracionService:
    """Servicio para manejar la configuración de precios"""
    
    @staticmethod
    def obtener_configuracion(db: Session):
        """Obtener la configuración actual de precios"""
        config = db.query(ConfiguracionPrecios).order_by(ConfiguracionPrecios.id.desc()).first()
        
        if not config:
            # Crear configuración por defecto si no existe
            config = ConfiguracionPrecios(
                precio_media_hora=0.50,
                precio_hora_adicional=1.00,
                precio_nocturno=10.00
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        
        return config
    
    @staticmethod
    def actualizar_configuracion(db: Session, datos: dict):
        """Actualizar la configuración de precios"""
        config = ConfiguracionService.obtener_configuracion(db)
        
        if 'precio_media_hora' in datos and datos['precio_media_hora'] is not None:
            config.precio_media_hora = datos['precio_media_hora']
        
        if 'precio_hora_adicional' in datos and datos['precio_hora_adicional'] is not None:
            config.precio_hora_adicional = datos['precio_hora_adicional']
        
        if 'precio_nocturno' in datos and datos['precio_nocturno'] is not None:
            config.precio_nocturno = datos['precio_nocturno']
        
        if 'hora_inicio_nocturno' in datos and datos['hora_inicio_nocturno'] is not None:
            config.hora_inicio_nocturno = datetime.strptime(datos['hora_inicio_nocturno'], '%H:%M').time()
        
        if 'hora_fin_nocturno' in datos and datos['hora_fin_nocturno'] is not None:
            config.hora_fin_nocturno = datetime.strptime(datos['hora_fin_nocturno'], '%H:%M').time()
        
        db.commit()
        db.refresh(config)
        return config