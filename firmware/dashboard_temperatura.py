# ============================================================================
# PROYECTO: Purificación de Agua Mediante Contacto Directo con Plasma (TEI201)
# ARCHIVO: firmware/dashboard_temperatura.py
# DESCRIPCIÓN: Captura serial, almacenamiento CSV persistente, cálculo de
#              indicadores (Delta T, promedio, máx) y alerta visual en vivo.
# ============================================================================

import serial                   # Librería (pyserial) para leer los datos enviados por el Arduino Leonardo vía USB
import csv                      # Librería estándar para guardar el historial estructurado en formato CSV
import time                     # Librería para manejar pausas de inicialización del puerto serial
import matplotlib.pyplot as plt # Librería para generar el dashboard interactivo con gráficas en tiempo real

# --- 1. CONFIGURACIÓN DE PARÁMETROS DEL SISTEMA ---
PUERTO = "COM3"                 # Puerto serial donde se conecta el Arduino Leonardo (ajustar según el PC)
VELOCIDAD = 115200              # Velocidad en baudios idéntica a la configurada en Serial.begin(115200) del Arduino
ARCHIVO_CSV = "temperaturas.csv"# Nombre del archivo de repositorio persistente donde se guardan las mediciones

# Umbrales técnicos basados en la precisión del sensor DS18B20 (±0.5 °C) y seguridad operativa:
UMBRAL_CONTACTO_DELTA = 0.5     # Aumento >= 0.5 °C confirma contacto plasma-agua por sobre la incertidumbre del sensor
UMBRAL_ALERTA_ALTA_DELTA = 3.0  # Aumento >= 3.0 °C alerta calentamiento elevado (apagar/modular descarga de plasma)

# --- 2. INICIALIZACIÓN DE LISTAS DE DATOS ---
tiempos = []                    # Lista para almacenar el eje X (tiempo en segundos)
temperaturas = []               # Lista para almacenar el eje Y (temperatura del agua en °C)
temp_inicial = None             # Variable para guardar la primera lectura (línea base antes del disparo de plasma)

# --- 3. CONEXIÓN CON EL MICROCONTROLADOR ARDUINO ---
arduino = serial.Serial(        # Abre la conexión serial con los parámetros definidos
    PUERTO,                     # Asigna el puerto COM correspondiente
    VELOCIDAD,                  # Asigna la velocidad de 115200 baudios
    timeout=0.05                # Define un tiempo máximo de espera de 50 ms para no congelar la interfaz gráfica
)
time.sleep(2)                   # Espera 2 segundos para que el Arduino Leonardo se estabilice tras abrir el puerto
arduino.reset_input_buffer()    # Limpia cualquier byte incompleto acumulado previamente en el buffer de entrada

# --- 4. CONFIGURACIÓN DEL DASHBOARD EN TIEMPO REAL ---
plt.ion()                       # Activa el modo interactivo de Matplotlib para actualizar la gráfica sin bloquear el código
fig, ax = plt.subplots(figsize=(10, 6)) # Crea la ventana principal (fig) y los ejes del gráfico (ax) con tamaño 10x6 pulgadas
fig.canvas.manager.set_window_title("Dashboard IoT - Monitoreo Térmico de Plasma en Agua (TEI201)") # Título de la ventana

# Crea la curva principal de temperatura del agua
linea_temp, = ax.plot([], [], color="#0072B2", linewidth=2, label="Temperatura del Agua (°C)")

# Crea dos líneas horizontales punteadas para mostrar los umbrales de decisión en el gráfico
linea_umbral_contacto = ax.axhline(y=0, color="#2ECC71", linestyle="--", linewidth=1.5, label="Umbral Contacto (+0.5 °C)")
linea_umbral_alerta = ax.axhline(y=0, color="#E74C3C", linestyle=":", linewidth=1.5, label="Alerta Térmica (+3.0 °C)")

ax.set_xlabel("Tiempo (segundos)", fontsize=11)        # Etiqueta del eje X con unidad de medida explícita
ax.set_ylabel("Temperatura (°C)", fontsize=11)         # Etiqueta del eje Y con unidad de medida explícita
ax.set_title("Monitoreo en Tiempo Real: Transferencia Térmica Plasma-Agua", fontsize=13, fontweight="bold") # Título del gráfico
ax.grid(True, linestyle="--", alpha=0.6)               # Activa la cuadrícula de fondo para facilitar la lectura de valores
ax.legend(loc="upper left")                            # Muestra la leyenda en la esquina superior izquierda

# Crea un cuadro de texto dinámico en la esquina superior derecha para mostrar estadísticas y alertas visuales
cuadro_estado = ax.text(
    0.98, 0.05,                                        # Posición relativa (abajo a la derecha dentro del gráfico)
    "Esperando datos del sensor DS18B20...",           # Texto inicial antes de recibir la primera muestra
    transform=ax.transAxes,                            # Usa coordenadas relativas al gráfico (0 a 1)
    fontsize=10,                                       # Tamaño de fuente legible durante la presentación
    verticalalignment="bottom",                        # Alineación vertical inferior
    horizontalalignment="right",                       # Alineación horizontal derecha
    bbox=dict(boxstyle="round,pad=0.6", facecolor="#F0F0F0", edgecolor="#CCCCCC", alpha=0.9) # Diseño del recuadro
)

# --- 5. BUCLE PRINCIPAL DE CAPTURA, ALMACENAMIENTO Y GENERACIÓN DE INFORMACIÓN ---
try:
    with open(ARCHIVO_CSV, "w", newline="", encoding="utf-8") as archivo: # Abre/crea el archivo CSV en modo escritura
        escritor = csv.writer(archivo)                 # Crea el objeto escritor para insertar filas en el archivo CSV
        
        # Escribe la fila de encabezados estructurados en el repositorio CSV
        escritor.writerow(["Tiempo_s", "Temperatura_C", "Delta_T_C", "Temp_Promedio_C", "Estado_Alerta"])
        
        # Mantiene el sistema corriendo mientras la ventana del gráfico siga abierta
        while plt.fignum_exists(fig.number):
            
            # Lee todas las tramas disponibles en el buffer serial para evitar retrasos (lag)
            while arduino.in_waiting:
                dato = arduino.readline().decode(errors="ignore").strip() # Lee una línea, la convierte a texto y quita espacios
                
                try:
                    tiempo_ms, temp = dato.split(",")  # Separa el texto usando la coma en tiempo (ms) y temperatura (°C)
                    t = round(float(tiempo_ms) / 1000.0, 2) # Convierte el tiempo de milisegundos a segundos con 2 decimales
                    temperatura = float(temp)          # Convierte el texto de temperatura a número decimal (float)
                    
                    # Si es la primera medición válida, la fija como temperatura base inicial (T0)
                    if temp_inicial is None:
                        temp_inicial = temperatura     # Guarda la temperatura del agua antes de encender el plasma
                        # Ajusta la posición de las líneas horizontales de umbral según la temperatura inicial medida
                        linea_umbral_contacto.set_ydata([temp_inicial + UMBRAL_CONTACTO_DELTA, temp_inicial + UMBRAL_CONTACTO_DELTA])
                        linea_umbral_alerta.set_ydata([temp_inicial + UMBRAL_ALERTA_ALTA_DELTA, temp_inicial + UMBRAL_ALERTA_ALTA_DELTA])
                    
                    # Agrega los nuevos valores a las listas históricas de la sesión
                    tiempos.append(t)
                    temperaturas.append(temperatura)
                    
                    # --- CÁLCULO DE INDICADORES Y REGLAS DE DECISIÓN ---
                    delta_t = temperatura - temp_inicial                   # Calcula el incremento térmico acumulado (Delta T)
                    temp_promedio = sum(temperaturas) / len(temperaturas)  # Calcula la temperatura media de la prueba
                    temp_max = max(temperaturas)                           # Identifica la temperatura máxima registrada
                    
                    # Evalúa en qué estado operativo se encuentra el reactor de plasma según Delta T
                    if delta_t >= UMBRAL_ALERTA_ALTA_DELTA:
                        estado = "ALERTA: EXCESO TÉRMICO (Apagar/Modular Plasma)"
                        color_caja = "#FADBD8"         # Fondo rojo claro de alerta crítica
                        color_borde = "#E74C3C"        # Borde rojo intenso
                    elif delta_t >= UMBRAL_CONTACTO_DELTA:
                        estado = "VALIDADO: Contacto Plasma-Agua Activo (Delta T > 0.5 °C)"
                        color_caja = "#D4EFDF"         # Fondo verde claro de confirmación exitosa
                        color_borde = "#2ECC71"        # Borde verde
                    else:
                        estado = "LÍNEA BASE: Sin transferencia térmica significativa"
                        color_caja = "#EBF5FB"         # Fondo azul claro de monitoreo basal
                        color_borde = "#3498DB"        # Borde azul
                    
                    # Guarda la fila completa en el repositorio CSV y fuerza el volcado inmediato al disco duro
                    escritor.writerow([t, round(temperatura, 2), round(delta_t, 2), round(temp_promedio, 2), estado])
                    archivo.flush()                    # Garantiza que los datos persistan aunque se corte la energía
                    
                except ValueError:
                    # Si llega una línea incompleta por ruido al conectar o encender el arco, la ignora sin detener el programa
                    continue

            # Si ya existen datos capturados, actualiza el gráfico y el panel de indicadores en vivo
            if tiempos:
                linea_temp.set_data(tiempos, temperaturas) # Actualiza los puntos X e Y de la curva de temperatura
                ax.relim()                                 # Recalcula los límites de los ejes según los nuevos datos
                ax.autoscale_view()                        # Ajusta automáticamente la escala visual de la ventana
                
                # Actualiza el texto y color del cuadro de indicadores en tiempo real
                texto_info = (
                    f"ESTADO: {estado}\n"
                    f"Temp. Actual: {temperaturas[-1]:.2f} °C | Temp. Inicial (T0): {temp_inicial:.2f} °C\n"
                    f"Incremento (ΔT): {delta_t:+.2f} °C | Promedio: {temp_promedio:.2f} °C | Máx: {temp_max:.2f} °C"
                )
                cuadro_estado.set_text(texto_info)         # Reemplaza el texto del recuadro con las métricas actuales
                cuadro_estado.set_bbox(dict(boxstyle="round,pad=0.6", facecolor=color_caja, edgecolor=color_borde, alpha=0.95))
            
            plt.pause(0.1)                                 # Refresca la interfaz gráfica cada 0.1 segundos

except KeyboardInterrupt:
    # Captura la combinación de teclas Ctrl + C en la consola para detener la medición limpiamente
    print("Medición detenida manualmente por el usuario.")

finally:
    # Bloque de cierre seguro: se ejecuta siempre al terminar para liberar los recursos del computador
    arduino.close()                                        # Cierra el puerto serial para que Arduino IDE u otro programa pueda usarlo
    plt.close("all")                                       # Cierra todas las ventanas gráficas abiertas de Matplotlib
    print(f"Sesión finalizada. Datos históricos e indicadores guardados en '{ARCHIVO_CSV}'.")
