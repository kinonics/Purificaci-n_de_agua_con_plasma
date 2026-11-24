# Documentación y Justificación Técnica del Sistema IoT (TEI201)

**Proyecto:** Purificación de Agua Mediante Contacto Indirecto con Plasma  
**Equipo:** Grupo 2 — Angelo Fisicaro, Franco Fisicaro, Francisco Osorio y Joaquín Vásquez  
**Asignatura:** TEI201 — Taller de Diseño en Ingeniería (Sección 1, UAI)  
**Profesor:** Camilo Vásquez Wilson | **Ayudante:** Martín Raguileo  

## 1. Conexión con la Problemática Original (Avance 1)

Las tecnologías convencionales de tratamiento hídrico presentan limitaciones operativas críticas frente a microcontaminantes emergentes como fármacos, pesticidas y disruptores endocrinos:
* **Ultrafiltración:** Opera entre 1 y 10 bar, pero el tamaño de poro de sus membranas no logra retener sales ni compuestos traza.
* **Ósmosis Inversa:** Requiere altas presiones (10 a 80 bar), sufre ensuciamiento severo por materia orgánica y coloidal, eleva el consumo energético y genera salmuera residual.
* **Tratamientos Biológicos:** Son sensibles a variaciones térmicas o hidráulicas y generan lodos residuales de gestión compleja.

Para superar la baja escalabilidad de los reactores de plasma tradicionales que exigen cámaras de vacío selladas, este prototipo implementa un **reactor de plasma frío no sellado** en aire a presión atmosférica y en contacto indirecto con el agua contenida en un vaso Petri. El sistema IoT integrado captura, almacena y monitorea continuamente la curva térmica del agua para comprobar empíricamente la transferencia de energía plasma-agua y observar el comportamiento térmico del experimento en tiempo real.

## 2. Arquitectura de Software y Ciclo de Datos IoT

El software implementa el ciclo completo de datos del prototipo IoT (captura continua, validación, almacenamiento local estructurado, visualización en vivo y apoyo a la toma de decisiones operativas):

* **Captura y Comunicación Serial:** El firmware en el **Arduino Leonardo** (`firmware/main.ino`, con librerías `OneWire` y `DallasTemperature`) lee el sensor DS18B20 desde el pin digital 2 (`SENSOR_PIN 2`) y transmite tiempo (en segundos) y temperatura (en °C) separados por coma por USB Serial a **9600 baudios** (`VELOCIDAD = 9600`) a una frecuencia nominal de **4 Hz**. En el computador, la aplicación `registro_temperatura.py` consulta el puerto serial de forma no bloqueante (`timeout=0`) cada **100 ms** (`INTERVALO_GUI_MS = 100`) mediante el bucle de eventos de Tkinter (`root.after`), utilizando el reloj del Arduino para fijar el tiempo transcurrido entre muestras a partir de la primera lectura válida ($t = 0$).
* **Validación y Manejo de Interferencia Electromagnética (EMI):** Dado que la descarga de alto voltaje en aire puede inducir ruido electromagnético en la línea de datos, el software filtra y protege la adquisición en tiempo real:
  * Descarta encabezados, tramas corruptas o incompletas (`parse_measurement`), mensajes con prefijo `# ERROR` y lecturas no finitas o fuera del rango operativo del sensor (-55 °C a 125 °C).
  * Detecta reinicios del microcontrolador o retrocesos en el reloj (`t <= last_raw`) para evitar series temporales inconsistentes.
  * Supervisa la continuidad de llegada de datos e interrumpe la sesión con alerta visible si transcurren **5 segundos sin lecturas válidas** (`TIEMPO_SIN_DATOS_S = 5`), evitando sesiones ciegas ante desconexiones.
* **Repositorio Local Persistente y Trazabilidad:** Cada ejecución crea una carpeta única identificada por fecha, hora y microsegundos dentro de `testing/mediciones/` (`YYYY-MM-DD_HH-MM-SS_ffffff`), impidiendo sobrescribir ensayos previos. En cada sesión se generan:
  * `temperaturas.csv` (columnas `tiempo_s,temperatura_C`), con vaciado inmediato a disco (`flush()`) tras cada medición válida para preservar los datos incluso ante cortes abruptos.
  * `metadatos.json`, que registra la temperatura objetivo configurada, el motivo de término, la cantidad de muestras, $\Delta T$, el promedio y la frecuencia real observada.
  * Además, la aplicación permite reabrir registros históricos (`.csv` y `.json`) sin conectar el Arduino y exportar los gráficos en formato **PNG** (200 dpi) para documentación técnica.
* **Visualización, Generación de Información y Decisión Operativa:** El dashboard local en **Tkinter** con gráfico incrustado de **Matplotlib** (`FigureCanvasTkAgg`) y tabla desplazable transforma las lecturas crudas en indicadores en vivo: temperatura actual, tiempo transcurrido, conteo de mediciones, variación térmica acumulada ($\Delta T = T_{\text{actual}} - T_{\text{inicial}}$), promedio aritmético y frecuencia real observada (Hz). Antes de iniciar, el operador fija una **temperatura objetivo** (entre 0 y 100 °C), representada como línea de referencia en el gráfico; al alcanzarla o superarla ($T \ge T_{\text{objetivo}}$), el sistema guarda esa medición y finaliza automáticamente el registro.
* **Alcance y Límite de Seguridad:** El sistema IoT cumple estrictamente funciones de instrumentación, registro y monitoreo térmico; **no controla la fuente de alto voltaje ni constituye un sistema de seguridad eléctrica**.

## 3. Selección de Hardware y Diseño para la Reparación

* **Microcontrolador Arduino Leonardo:** Gestiona el bus digital en el pin 2 (`SENSOR_PIN 2`) y mantiene la comunicación USB Serial a 9600 baudios con el dashboard local, permitiendo además detección dinámica del puerto COM desde la interfaz sin fijar un puerto estático por computador.
* **Sensor Digital Impermeable DS18B20:** Seleccionado por su encapsulado sumergible, su rango operativo de -55 °C a 125 °C y su precisión especificada de ±0,5 °C (entre -10 °C y 85 °C). Al transmitir datos digitales mediante el protocolo 1-Wire (9,6 Kbd) a través de un único cable con resistencia pull-up/variable en protoboard, reduce la caída de tensión y la susceptibilidad al ruido eléctrico respecto a sensores analógicos convencionales cerca de la descarga de plasma.
* **Electrodos y Referencia a Tierra:** La descarga se produce entre 2 agujas metálicas separadas a **4 mm** sobre un vaso Petri de vidrio (encaje de 60 mm de diámetro), acompañado de una **lámina de cobre de 40 × 40 mm con lengüeta lateral** que actúa como electrodo pasivo de referencia a tierra (0 V).
* **Diseño para la Reparación en Campo:** El montaje evita uniones permanentes o sellados destructivos. Su estructura modular con fijaciones desmontables permite retirar el vaso Petri para limpieza, sustituir las agujas en caso de desgaste por oxidación, regular la altura del puente sobre el eje vertical e intervenir la lámina de cobre, la protoboard o la sonda DS18B20 sin dañar el prototipo.

## 4. Integración Mecánica y Gemelo 3D (Modelo Plasma V2)

El diseño estructural **Modelo Plasma V2** fue modelado paramétricamente en Fusion 360 (`.f3d`, planos técnicos en PDF y corte láser `.dxf`) en madera **MDF de 5,5 mm** para aislar eléctricamente los soportes y mantener una alineación repetible entre los electrodos y el volumen de agua:
* **Base de Petri:** Plataforma de 110 × 110 × 20 mm diseñada para alojar y estabilizar el vaso Petri de vidrio (encaje de 60 mm de diámetro) junto con la lámina de cobre de referencia a tierra (40 × 40 mm con lengüeta lateral) bajo la zona de descarga.
* **Base de Torre:** Soporte de 80 × 80 × 25 mm encargado de anclar el eje vertical de 130 mm mediante fijaciones desmontables.
* **Puente de Electrodo:** Brazo horizontal de 125 × 30 × 5 mm montado sobre el eje vertical, con 2 perforaciones separadas exactamente a 4 mm entre sí para fijar las agujas metálicas sobre el agua.

## 5. Validación Experimental y Análisis de Fallas

* **Validación Cuantitativa de Transferencia Plasma-Agua:** En pruebas de monitoreo de 90 segundos, el sistema registró una línea base inicial cercana a 22,5 °C (entre los 0 y 10 s) seguida de un ascenso continuo hasta aproximadamente 25,0 °C al completar los 90 segundos. El incremento neto ($\Delta T \approx +2,5\text{ }^\circ\text{C}$) quintuplica la incertidumbre instrumental del sensor (±0,5 °C), comprobando cuantitativamente la transferencia térmica del plasma hacia el agua.
* **Análisis y Solución de Fallas Detectadas:** Durante las pruebas iniciales (Avance 2) se presentó ausencia de lecturas válidas e interferencias entre el sensor y el montaje físico al operar la descarga. Esta falla se mitigó asegurando la conexión en protoboard con la resistencia en el bus 1-Wire, separando físicamente el cableado de la sonda respecto a los conductores de alta tensión e incorporando en `registro_temperatura.py` el descarte de tramas `# ERROR` o fuera de rango, la detección de reinicios del Arduino y el corte automático con alerta tras 5 segundos sin lecturas válidas.
