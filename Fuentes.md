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



## 4. Bibliografía Científica y Herramientas de Diseño CAD

### Fundamentos físicos y estado del arte
- Conrads, H., y Schmidt, M. (2000). Plasma generation and plasma sources. Plasma Sources Science and Technology, 9(4), 441-454.
  - Aplicación en el proyecto: Clasificación fundamental de fuentes de plasma atmosférico y criterios de selección de régimen entre no térmico (plasma frío) frente a descargas de arco térmico.

- Foster, J. E. (2017). Plasma-based water purification: Challenges and prospects for the future. Physics of Plasmas, 24(5), 055501.
  - Aplicación en el proyecto: Respaldo teórico para la ruptura dieléctrica del aire a presión atmosférica (aproximadamente 30 kV/cm), la prevención de inestabilidad térmica mediante geometría de punta fina y la generación de especies reactivas de oxígeno y nitrógeno (RONS).

- Svarnas, P., Poupouzas, M., Papalexopoulou, K., Kalaitzopoulou, E., Skipitari, M., Papadea, P., y Krontiras, C. (2022). Water modification by cold plasma jet with respect to physical and chemical properties. Applied Sciences, 12(23), 11950.
  - Aplicación en el proyecto: Referencia experimental para la arquitectura indirecta pin-to-water, el cierre de circuito mediante acoplamiento capacitivo a tierra (0 V) bajo el recipiente dieléctrico y el análisis del comportamiento térmico y evaporativo del agua tratada.

- Alvarado Avilés, A. B., Montesel Pastuzo, C. G., y Yépez, P. (2021). Efecto del agua activada por plasma frío en la descontaminación de material de empaque en el llenado aséptico (Tesis doctoral, ESPOL - FIMCP).
  - Aplicación en el proyecto: Análisis del agua activada por plasma en procesos de desinfección y degradación oxidativa.

- Celestino Vázquez, J. (2023). Análisis de propiedades fisicoquímicas del agua activada por plasma y su aplicación en la agricultura.
  - Aplicación en el proyecto: Análisis de la evolución de los parametros fisicoquímicos del agua tras la interacción plasma-líquido y su escalabilidad en aplicaciones reales (ODS 6).

### Software de modelado 3D y manufactura digital
- Autodesk Fusion 360 (Licencia Educacional UAI)
  - Uso en el proyecto: Modelado paramétrico tridimensional del reactor (torre de soporte, puente voladizo y peana), validación geométrica del gap aire-agua (7,8 mm en seco y 2,8 mm libres sobre 5 mm de agua), generación del juego de planos técnicos ortogonales en PDF (Planos_PlasmaV2.pdf) y exportación de vectores 2D (.dxf) para corte láser en MDF de 5,5 mm.

### Asistencia de Inteligencia Artificial en Diseño Mecánico
- Herramienta: Gemini (octubre - noviembre 2026)
  - Uso: Apoyo en el cálculo de tolerancias mecánicas para corte láser (diámetro 12,5 mm para perno roscado M12 y diámetro 62 mm para placa Petri comercial de 60 x 15 mm), optimización de anidado (nesting) en planchas de MDF de 300 x 300 mm y estructuración técnica de las especificaciones de manufactura en la memoria del proyecto.
