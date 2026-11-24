# Declaración de Fuentes e Inteligencia Artificial — TEI201

**Proyecto:** Purificación de Agua Mediante Contacto Indirecto con Plasma  
**Equipo:** Grupo 2 — Angelo Fisicaro, Franco Fisicaro, Francisco Osorio y Joaquín Vásquez  
**Asignatura:** TEI201 — Taller de Diseño en Ingeniería (Sección 1, UAI)  

---

## 1. Librerías utilizadas

| Librería | Versión | Uso en el proyecto | Fuente |
| :--- | :--- | :--- | :--- |
| OneWire | 2.3.8 | Comunicación digital 1-Wire en el pin 2 con el sensor DS18B20 | https://github.com/PaulStoffregen/OneWire |
| DallasTemperature | 3.9.0 | Configuración de resolución (10 bits) y lectura térmica del DS18B20 | https://github.com/milesburton/Arduino-Temperature-Control-Library |
| pyserial | 3.5 | Comunicación USB Serial bidireccional a 115200 baudios y detección dinámica de puertos COM (`list_ports`) | https://github.com/pyserial/pyserial |
| matplotlib | 3.9.2 | Gráfico térmico en tiempo real incrustado en Tkinter (`FigureCanvasTkAgg`) y exportación a PNG | https://matplotlib.org/ |

*(Los módulos `tkinter`, `csv`, `json`, `math`, `time`, `datetime` y `pathlib` forman parte de la biblioteca estándar incluida en Python).*

---

## 2. Código externo adaptado

### Inicialización del sensor DS18B20, trama estructurada y control de relé (`firmware/main.ino`, líneas `[X–Y]`)
* **Fuente:** Ejemplo `Simple.ino` de la librería `DallasTemperature` (https://github.com/milesburton/Arduino-Temperature-Control-Library).
* **Adaptación:** Se definió el pin digital 2 (`#define SENSOR_PIN 2`), se fijó la velocidad serial en **115200 baudios** y la resolución en **10 bits** (`sensors.setResolution(10)`, pasos de 0,25 °C y conversión máxima de 187,5 ms) para operar a **4 Hz nominales**. Sobre la base de lectura se implementó el filtrado de desconexiones/errores frente a interferencia electromagnética (EMI), la transmisión de la trama estructurada `DATA,milisegundos,temperatura,rele`, la recepción de comandos seriales (`I/P/H/T`) para controlar el módulo relé de prueba de banco y un límite automático de parada a los 30 s en Arduino.

### Adquisición serial no bloqueante, interfaz Tkinter y persistencia (`firmware/registro_temperatura_v2.py`, líneas `[X–Y]`)
* **Fuente:** Documentación oficial de PySerial (https://pyserial.readthedocs.io/) y ejemplos oficiales de integración de Matplotlib en Tkinter (*Embedding in Tk*: https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html).
* **Adaptación:** Se implementó una aplicación de escritorio en Tkinter que consulta el puerto serial de forma no bloqueante cada `100 ms` mediante `root.after()`, incorpora selector dinámico de puerto COM (`list_ports`), descarta tramas corruptas o fuera de rango (-55 °C a 125 °C), corta la sesión tras 5 s sin lecturas válidas, guarda cada ensayo en una carpeta única con fecha y hora dentro de `testing/mediciones/` (`temperaturas.csv` con `flush()` inmediato y `metadatos.json`), permite reabrir registros históricos (`Abrir CSV`) sin Arduino, exportar gráficos en PNG y enviar la orden automática de apagado al relé al cruzar la temperatura objetivo.

---

## 3. Uso de Inteligencia Artificial

### Desarrollo y depuración del dashboard y protocolo serial v2 (`firmware/registro_temperatura_v2.py` y `firmware/main.ino`, líneas `[X–Y]`)
* **Herramienta:** `[Indicar herramienta exacta, ej. ChatGPT / Claude / Copilot / Gemini]` (noviembre 2026).
* **Prompt / Uso utilizado:** Apoyo para estructurar la aplicación de escritorio en Python (`tkinter`, `pyserial` y `matplotlib`) y su protocolo serial bidireccional con Arduino a 115200 baudios para capturar lecturas del DS18B20, calcular indicadores en vivo, persistir los datos en CSV/JSON y accionar un relé de prueba al alcanzar una temperatura objetivo.
* **Adaptación:** Se integró la detección dinámica de puertos COM, el parseo de la trama `DATA,milisegundos,temperatura,rele`, el manejo de errores por ruido EMI, la lógica de medición según dirección (calentamiento con relé encendido / enfriamiento con relé apagado) mediante comandos `I/P/H/T` y el protocolo de seguridad que mantiene desconectada la fuente de alto voltaje durante las pruebas del relé.
* **Comprensión:** El equipo comprende el ciclo completo de datos del sistema —desde la conversión de 10 bits en Arduino y la lectura no bloqueante cada 100 ms en Tkinter hasta el cálculo de $\Delta T$, promedio y frecuencia real, el vaciado a disco con `flush()` y el cierre automático por objetivo alcanzado (`OBJETIVO_ALCANZADO`)— y validó su operación en banco registrando 303 mediciones continuas a 4,00 Hz reales exactos.

### Estructura de documentación del repositorio (`README.md`, `FUENTES.md`, `docs/justificacion_tecnica.md` y protocolo de pruebas)
* **Herramienta:** Gemini (noviembre 2026).
* **Uso:** Generación y actualización de las plantillas en Markdown para `README.md`, `FUENTES.md`, `docs/justificacion_tecnica.md` y estructuración del protocolo experimental a partir de los informes, planos, videos de validación y códigos elaborados por el equipo.

---

## 4. Bibliografía Científica y Herramientas de Diseño CAD

### Fundamentos físicos y estado del arte
* Conrads, H., y Schmidt, M. (2000). Plasma generation and plasma sources. *Plasma Sources Science and Technology*, 9(4), 441-454.
  * Aplicación en el proyecto: Clasificación fundamental de fuentes de plasma atmosférico y criterios de selección de régimen entre no térmico (plasma frío) frente a descargas de arco térmico.
* Foster, J. E. (2017). Plasma-based water purification: Challenges and prospects for the future. *Physics of Plasmas*, 24(5), 055501.
  * Aplicación en el proyecto: Respaldo teórico para la ruptura dieléctrica del aire a presión atmosférica (aproximadamente 30 kV/cm), la prevención de inestabilidad térmica mediante geometría de punta fina y la generación de especies reactivas de oxígeno y nitrógeno (RONS).
* Svarnas, P., Poupouzas, M., Papalexopoulou, K., Kalaitzopoulou, E., Skipitari, M., Papadea, P., y Krontiras, C. (2022). Water modification by cold plasma jet with respect to physical and chemical properties. *Applied Sciences*, 12(23), 11950.
  * Aplicación en el proyecto: Referencia experimental para la arquitectura indirecta pin-to-water, el cierre de circuito mediante acoplamiento capacitivo a tierra (0 V) bajo el recipiente dieléctrico y el análisis del comportamiento térmico y evaporativo del agua tratada.
* Alvarado Avilés, A. B., Montesel Pastuzo, C. G., y Yépez, P. (2021). *Efecto del agua activada por plasma frío en la descontaminación de material de empaque en el llenado aséptico* (Tesis doctoral, ESPOL - FIMCP).
  * Aplicación en el proyecto: Análisis del agua activada por plasma en procesos de desinfección y degradación oxidativa.
* Celestino Vázquez, J. (2023). *Análisis de propiedades fisicoquímicas del agua activada por plasma y su aplicación en la agricultura*.
  * Aplicación en el proyecto: Análisis de la evolución de los parámetros fisicoquímicos del agua tras la interacción plasma-líquido y su escalabilidad en aplicaciones reales (ODS 6).

### Software de modelado 3D y manufactura digital
* **Autodesk Fusion 360** (Licencia Educacional UAI)
  * Uso en el proyecto: Modelado paramétrico tridimensional del reactor (torre de soporte, puente voladizo y peana), validación geométrica del gap aire-agua (7,8 mm en seco y 2,8 mm libres sobre 5 mm de agua), generación del juego de planos técnicos ortogonales en PDF (`Planos_PlasmaV2.pdf`) y exportación de vectores 2D (`.dxf`) para corte láser en MDF de 5,5 mm.

### Asistencia de Inteligencia Artificial en Diseño Mecánico
* **Herramienta:** Gemini (octubre - noviembre 2026)
  * Uso: Apoyo en el cálculo de tolerancias mecánicas para corte láser (diámetro 12,5 mm para perno roscado M12 y diámetro 62 mm para placa Petri comercial de 60 × 15 mm), optimización de anidado (nesting) en planchas de MDF de 300 × 300 mm y estructuración técnica de las especificaciones de manufactura en la memoria del proyecto.
