from datetime import datetime, timedelta
import math

class CalculadoraPrecios:
    """Utilidad para calcular precios del parqueadero"""
    
    @staticmethod
    def calcular_costo(fecha_entrada, fecha_salida, config):
        """
        Calcular el costo total del estacionamiento
        
        Regla de cobro:
        - Primera media hora: precio_media_hora (solo UNA VEZ al inicio)
        - Cada hora adicional (o fracción): precio_hora_adicional
        - Si pasa 12h completas en horario nocturno: precio_nocturno
        
        Args:
            fecha_entrada: datetime de entrada
            fecha_salida: datetime de salida
            config: objeto ConfiguracionPrecios
        
        Returns:
            dict con costo, minutos y detalles
        """
        delta = fecha_salida - fecha_entrada
        minutos_totales = int(delta.total_seconds() / 60)
        
        if minutos_totales <= 0:
            return {'costo': 0, 'minutos': 0, 'detalles': 'Error en el cálculo de tiempo'}
        
        costo_total = 0
        detalles = []
        minutos_procesados = 0
        
        # Cobrar primera media hora (solo una vez al inicio)
        if minutos_totales >= 30:
            costo_total += float(config.precio_media_hora)
            detalles.append(f'Primera media hora: ${config.precio_media_hora}')
            minutos_procesados = 30
        else:
            # Menos de 30 minutos, solo cobrar la primera media hora
            costo_total = float(config.precio_media_hora)
            detalles.append(f'Primera media hora: ${config.precio_media_hora}')
            return {
                'costo': round(costo_total, 2),
                'minutos': minutos_totales,
                'detalles': ' | '.join(detalles)
            }
        
        # Calcular horas adicionales después de la primera media hora
        minutos_restantes = minutos_totales - 30
        horas_adicionales = math.ceil(minutos_restantes / 60.0)
        costo_horas = horas_adicionales * float(config.precio_hora_adicional)
        
        costo_total += costo_horas
        detalles.append(f'{horas_adicionales} hora(s) adicional(es): ${costo_horas:.2f}')
        
        return {
            'costo': round(costo_total, 2),
            'minutos': minutos_totales,
            'detalles': ' | '.join(detalles)
        }
    
    @staticmethod
    def _es_periodo_nocturno(momento, config):
        """Verificar si está en período nocturno"""
        hora_actual = momento.time()
        inicio = config.hora_inicio_nocturno
        fin = config.hora_fin_nocturno
        
        # El período nocturno cruza medianoche (ej: 19:00 a 07:00)
        if inicio > fin:
            es_nocturno = hora_actual >= inicio or hora_actual < fin
            
            if hora_actual >= inicio:
                fin_periodo = datetime.combine(momento.date() + timedelta(days=1), fin)
            else:
                fin_periodo = datetime.combine(momento.date(), fin)
            
            if hora_actual < fin:
                inicio_periodo = datetime.combine(momento.date() - timedelta(days=1), inicio)
            else:
                inicio_periodo = datetime.combine(momento.date(), inicio)
        else:
            # Período normal dentro del mismo día
            es_nocturno = inicio <= hora_actual < fin
            fin_periodo = datetime.combine(momento.date(), fin)
            inicio_periodo = datetime.combine(momento.date(), inicio)
        
        return {
            'es_nocturno': es_nocturno,
            'fin_periodo': fin_periodo,
            'inicio_periodo': inicio_periodo if inicio_periodo > momento else None
        }
    
    @staticmethod
    def _calcular_tarifa_diurna(minutos, config):
        """
        Calcular tarifa diurna progresiva
        
        Regla: 
        - Primera media hora: precio_media_hora
        - Cada hora adicional (o fracción): precio_hora_adicional
        """
        costo = 0
        detalles = []
        
        if minutos <= 30:
            # Solo primera media hora
            costo = float(config.precio_media_hora)
            detalles.append(f'Primera media hora: ${config.precio_media_hora}')
        else:
            # Primera media hora
            costo += float(config.precio_media_hora)
            detalles.append(f'Primera media hora: ${config.precio_media_hora}')
            
            # Calcular horas adicionales (redondeo hacia arriba)
            minutos_restantes = minutos - 30
            horas_adicionales = math.ceil(minutos_restantes / 60.0)
            costo_horas = horas_adicionales * float(config.precio_hora_adicional)
            
            costo += costo_horas
            detalles.append(f'{horas_adicionales} hora(s) adicional(es): ${costo_horas:.2f}')
        
        return {
            'total': costo,
            'detalles': detalles
        }
    
    @staticmethod
    def formatear_tiempo(minutos):
        """Formatear tiempo en formato legible"""
        horas = minutos // 60
        mins = minutos % 60
        return f'{horas}h {mins}m'