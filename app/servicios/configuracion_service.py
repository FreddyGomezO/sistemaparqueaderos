from sqlalchemy.orm import Session
from app.modelos.configuracion_precios import ConfiguracionPrecios
from datetime import datetime
import traceback  # <-- Añade esto

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
        # ==============================================
        # 🔍 DEBUG: Ver qué llega EXACTAMENTE
        # ==============================================
        print("\n" + "="*60)
        print("🔍 DEBUG BACKEND - ConfiguracionService.actualizar_configuracion")
        print("Datos recibidos:", datos)
        
        if 'hora_fin_nocturno' in datos:
            hora_fin = datos['hora_fin_nocturno']
            print(f"\n🔍 hora_fin_nocturno detallado:")
            print(f"  Valor: '{hora_fin}'")
            print(f"  Tipo: {type(hora_fin)}")
            print(f"  Longitud: {len(hora_fin) if hora_fin else 0}")
            if hora_fin:
                print(f"  Caracteres:", [f"{i}:'{c}'({ord(c)})" for i, c in enumerate(hora_fin)])
                print(f"  Partes al dividir ':': {hora_fin.split(':')}")
                
                # Intentar parsear para ver si hay error
                try:
                    hora_parsed = datetime.strptime(hora_fin, '%H:%M').time()
                    print(f"  ✅ Parseado correctamente: {hora_parsed}")
                except ValueError as e:
                    print(f"  ❌ Error al parsear: {e}")
                    print(f"  Traceback:", traceback.format_exc())
        
        print("="*60 + "\n")
        
        # Continuar con el código original
        config = ConfiguracionService.obtener_configuracion(db)
        
        if 'precio_media_hora' in datos and datos['precio_media_hora'] is not None:
            config.precio_media_hora = datos['precio_media_hora']
        
        if 'precio_hora_adicional' in datos and datos['precio_hora_adicional'] is not None:
            config.precio_hora_adicional = datos['precio_hora_adicional']
        
        if 'precio_nocturno' in datos and datos['precio_nocturno'] is not None:
            config.precio_nocturno = datos['precio_nocturno']
        
        if 'hora_inicio_nocturno' in datos and datos['hora_inicio_nocturno'] is not None:
            try:
                config.hora_inicio_nocturno = datetime.strptime(datos['hora_inicio_nocturno'], '%H:%M').time()
                print(f"✅ hora_inicio_nocturno parseado: {config.hora_inicio_nocturno}")
            except ValueError as e:
                print(f"❌ Error parseando hora_inicio_nocturno: {e}")
                raise
        
        if 'hora_fin_nocturno' in datos and datos['hora_fin_nocturno'] is not None:
            try:
                config.hora_fin_nocturno = datetime.strptime(datos['hora_fin_nocturno'], '%H:%M').time()
                print(f"✅ hora_fin_nocturno parseado: {config.hora_fin_nocturno}")
            except ValueError as e:
                print(f"❌ Error parseando hora_fin_nocturno: {e}")
                print(f"  Valor que causó error: '{datos['hora_fin_nocturno']}'")
                raise
        
        db.commit()
        db.refresh(config)
        return config