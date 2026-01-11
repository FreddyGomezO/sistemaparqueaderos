from app.utils.calculadora_precios import CalculadoraPrecios

class CalculoService:
    """Servicio que utiliza la calculadora de precios"""
    
    @staticmethod
    def calcular_costo(fecha_entrada, fecha_salida, config):
        """Calcular el costo del estacionamiento"""
        return CalculadoraPrecios.calcular_costo(fecha_entrada, fecha_salida, config)
    
    @staticmethod
    def formatear_tiempo(minutos):
        """Formatear tiempo en formato legible"""
        return CalculadoraPrecios.formatear_tiempo(minutos)