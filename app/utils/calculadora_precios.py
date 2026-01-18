from datetime import datetime, timedelta
import math

class CalculadoraPrecios:
    """Utilidad para calcular precios del parqueadero"""
    
    @staticmethod
    def calcular_costo(fecha_entrada, fecha_salida, config, es_nocturno=False):
        """
        Calcular el costo total del estacionamiento
        
        NUEVA LÓGICA:
        1. Si es_nocturno=True: aplicar precio_nocturno (tarifa fija) - SIN IMPORTAR TIEMPO
        2. Si no: tarifa normal progresiva
        """
        # ==============================================
        # 🔍 DEBUG: Ver qué datos llegan
        # ==============================================
        print("\n" + "="*60)
        print("🔍 DEBUG CalculadoraPrecios.calcular_costo")
        print(f"es_nocturno: {es_nocturno} (tipo: {type(es_nocturno)})")
        print(f"config.precio_nocturno: {config.precio_nocturno}")
        
        # TARIFA NOCTURNA (si fue marcado como nocturno en la entrada)
        # ¡SIEMPRE aplicar tarifa nocturna si es_nocturno=True!
        if es_nocturno:
            print(f"🌙 APLICANDO TARIFA NOCTURNA - SIN IMPORTAR TIEMPO")
            
            # Calcular minutos para mostrar en detalles
            try:
                # Asegurar que las fechas sean datetime
                entrada = fecha_entrada
                salida = fecha_salida
                
                if isinstance(entrada, str):
                    entrada = datetime.fromisoformat(entrada.replace('Z', '+00:00'))
                if isinstance(salida, str):
                    salida = datetime.fromisoformat(salida.replace('Z', '+00:00'))
                
                delta = salida - entrada
                segundos_totales = delta.total_seconds()
                minutos_totales = int(segundos_totales / 60)
                
                # Si es menos de 1 minuto, mostrar 1 minuto (para visualización)
                if segundos_totales > 0 and minutos_totales == 0:
                    minutos_totales = 1
                    print(f"⏱️  Tiempo estacionado: {segundos_totales:.1f} segundos → mostrar como 1 minuto")
                else:
                    print(f"⏱️  Tiempo estacionado: {minutos_totales} minutos")
                    
            except Exception as e:
                print(f"⏱️  Error calculando tiempo: {e}, usando 1 minuto")
                minutos_totales = 1
            
            costo = round(float(config.precio_nocturno), 2)
            print(f"💰 Costo nocturno fijo: ${costo}")
            
            return {
                'costo': costo,
                'minutos': max(minutos_totales, 1),  # Al menos 1 minuto para mostrar
                'detalles': f'TARIFA NOCTURNA FIJA: ${config.precio_nocturno}'
            }
        
        # Si NO es nocturno, usar lógica normal
        print(f"☀️  APLICANDO TARIFA NORMAL")
        
        # Asegurar que las fechas sean datetime
        entrada_original = fecha_entrada
        salida_original = fecha_salida
        
        # Si las fechas son strings, convertirlas
        if isinstance(fecha_entrada, str):
            try:
                fecha_entrada = datetime.fromisoformat(fecha_entrada.replace('Z', '+00:00'))
                print(f"✅ fecha_entrada convertida de string: {entrada_original} -> {fecha_entrada}")
            except Exception as e:
                print(f"❌ Error convirtiendo fecha_entrada: {e}")
                return {'costo': 0, 'minutos': 0, 'detalles': 'Error: fecha_entrada inválida'}
        
        if isinstance(fecha_salida, str):
            try:
                fecha_salida = datetime.fromisoformat(fecha_salida.replace('Z', '+00:00'))
                print(f"✅ fecha_salida convertida de string: {salida_original} -> {fecha_salida}")
            except Exception as e:
                print(f"❌ Error convirtiendo fecha_salida: {e}")
                return {'costo': 0, 'minutos': 0, 'detalles': 'Error: fecha_salida inválida'}
        
        # Calcular diferencia
        try:
            delta = fecha_salida - fecha_entrada
            segundos_totales = delta.total_seconds()
            minutos_totales = int(segundos_totales / 60)
            print(f"⏱️  Diferencia: {delta}")
            print(f"⏱️  Minutos totales: {minutos_totales}")
        except Exception as e:
            print(f"❌ Error calculando diferencia: {e}")
            return {'costo': 0, 'minutos': 0, 'detalles': f'Error en cálculo: {e}'}
        
        # Para tarifa normal, manejar el caso de menos de 1 minuto
        if minutos_totales <= 0:
            print(f"⚠️  minutos_totales <= 0: {minutos_totales}")
            print(f"   Aplicando primera media hora: ${config.precio_media_hora}")
            return {
                'costo': round(float(config.precio_media_hora), 2),
                'minutos': 1,  # Mostrar al menos 1 minuto
                'detalles': f'Primera media hora: ${config.precio_media_hora}'
            }
        
        # TARIFA NORMAL PROGRESIVA (mantener tu lógica original)
        costo_total = 0
        detalles = []
        
        # Cobrar primera media hora (solo una vez al inicio)
        if minutos_totales >= 30:
            costo_total += float(config.precio_media_hora)
            detalles.append(f'Primera media hora: ${config.precio_media_hora}')
            print(f"   Primera media hora: ${config.precio_media_hora}")
        else:
            # Menos de 30 minutos, solo cobrar la primera media hora
            costo_total = float(config.precio_media_hora)
            detalles.append(f'Primera media hora: ${config.precio_media_hora}')
            print(f"   Menos de 30 min: ${costo_total}")
            
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
        
        print(f"   Horas adicionales: {horas_adicionales} x ${config.precio_hora_adicional} = ${costo_horas:.2f}")
        print(f"   💰 Costo total: ${costo_total:.2f}")
        
        print("="*60 + "\n")
        
        return {
            'costo': round(costo_total, 2),
            'minutos': minutos_totales,
            'detalles': ' | '.join(detalles)
        }
    
    @staticmethod
    def formatear_tiempo(minutos):
        """Formatear tiempo en formato legible"""
        print(f"🔍 formatear_tiempo: {minutos} minutos")
        
        # Si es 0 o negativo, mostrar 0m pero no "Error"
        if minutos <= 0:
            print(f"⚠️  minutos <= 0: {minutos}, mostrando 0m")
            return "0m"
        
        horas = minutos // 60
        mins = minutos % 60
        
        resultado = ""
        if horas > 0 and mins > 0:
            resultado = f'{horas}h {mins}m'
        elif horas > 0:
            resultado = f'{horas}h'
        else:
            resultado = f'{mins}m'
        
        print(f"   Resultado formateado: {resultado}")
        return resultado
    
    @staticmethod
    def validar_formato_placa(placa: str) -> bool:
        """
        Validar formato de placa ecuatoriana
        """
        placa_limpia = placa.upper().strip().replace('-', '').replace(' ', '')
        
        print(f"🔍 validar_formato_placa: '{placa}' -> '{placa_limpia}'")
        
        if len(placa_limpia) < 6 or len(placa_limpia) > 7:
            print(f"❌ Longitud inválida: {len(placa_limpia)}")
            return False
        
        if not placa_limpia[:3].isalpha():
            print(f"❌ Primeros 3 caracteres no son letras: {placa_limpia[:3]}")
            return False
        
        if not placa_limpia[3:].isdigit():
            print(f"❌ Los últimos caracteres no son números: {placa_limpia[3:]}")
            return False
        
        if len(placa_limpia[3:]) not in [3, 4]:
            print(f"❌ Número de dígitos inválido: {len(placa_limpia[3:])}")
            return False
        
        print(f"✅ Placa válida: {placa_limpia}")
        return True