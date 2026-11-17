# Declaración de Fuentes e Inteligencia Artificial — TEI201

## 1. Librerías utilizadas

| Librería | Versión | Uso en el proyecto | Fuente |
| :--- | :--- | :--- | :--- |
| OneWire | 2.3.8 | Comunicación 1-Wire pin 2 | https://github.com/PaulStoffregen/OneWire |
| DallasTemperature | 3.9.0 | Lectura térmica DS18B20 | https://github.com/milesburton/Arduino-Temperature-Control-Library |
| pyserial | 3.5 | Lectura serial a 115200 bd | https://github.com/pyserial/pyserial |
| matplotlib | 3.9.2 | Dashboard en tiempo real | https://matplotlib.org/ |

## 2. Código externo adaptado

### Inicialización y resolución del sensor DS18B20 (main.ino, líneas 1-31)
* Fuente: Ejemplo Simple.ino de la librería DallasTemperature (https://github.com/milesburton/Arduino-Temperature-Control-Library)
* Adaptación: Se definió el pin digital 2 (`#define SENSOR_PIN 2`), se aumentó la velocidad serial a 115200 baudios, se fijó la resolución en 10 bits (`sensors.setResolution(10)`, tiempo de conversión hasta 187,5 ms) y se agregó una validación `if (temperatura != DEVICE_DISCONNECTED_C)` para enviar por puerto serial el tiempo (`millis()`) y la temperatura separados por coma con `delay(10)`.

### Lectura serial, graficación interactiva y guardado CSV (dashboard_temperatura.py, líneas 1-58)
* Fuente: Documentación oficial de PySerial (https://pyserial.readthedocs.io/) y modo interactivo de Matplotlib (`plt.ion()`).
* Adaptación: Se configuró la lectura no bloqueante con `timeout=0.05` y limpieza de buffer (`reset_input_buffer()`), decodificando la trama `tiempo_ms, temp` para convertir milisegundos a segundos (`float(tiempo_ms) / 1000`), actualizar la curva en vivo y guardar cada fila en `temperaturas.csv` usando `archivo.flush()`.

## 3. Uso de Inteligencia Artificial

### Script de visualización en tiempo real y manejo de excepciones (dashboard_temperatura.py, líneas 18-58)
* Herramienta: Asistente de IA (noviembre 2026)
* Prompt utilizado: "Escribe un script en Python con pyserial y matplotlib que lea tiempo en ms y temperatura desde Arduino a 115200 baudios, grafique en tiempo real y guarde los datos en temperaturas.csv sin perder muestras"
* Adaptación: Se ajustó el puerto serial (`COM3`), se incorporó un bloque `try-except ValueError` para descartar tramas incompletas por ruido electromagnético del arco de plasma y un bloque `except KeyboardInterrupt` con `finally` para cerrar de forma segura el puerto serial y el archivo CSV.
* Comprensión: El equipo comprende que el bucle `while arduino.in_waiting:` vacía el buffer serial en cada iteración, grafica los arreglos `tiempos` y `temperaturas` mediante `linea.set_data()` y asegura la persistencia de datos en disco con `archivo.flush()`.

### Estructura de documentación del repositorio (README.md y protocolo de pruebas)
* Herramienta: Gemini (noviembre 2026)
* Uso: Generación de la plantilla base en Markdown para `README.md`, `FUENTES.md` y estructuración del protocolo experimental a partir de los informes y códigos elaborados por el equipo.
