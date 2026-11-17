# Documentación y Justificación Técnica del Sistema IoT (TEI201)

**Proyecto:** Purificación de Agua Mediante Contacto Directo con Plasma[cite: 2]  
**Equipo:** Angelo Fisicaro, Franco Fisicaro, Francisco Osorio y Joaquín Vásquez[cite: 2, 3]  
**Asignatura:** TEI201 — Taller de Diseño en Ingeniería (Sección 1, UAI)[cite: 1, 2, 3]  
**Profesor:** Camilo Vásquez | **Ayudante:** Martín Raguileo[cite: 2, 3]  

## 1. Conexión con la Problemática Original (Avance 1)

Las tecnologías convencionales de tratamiento de agua presentan limitaciones operativas frente a microcontaminantes emergentes como fármacos, pesticidas y disruptores endocrinos[cite: 2]:
* **Ultrafiltración:** Opera entre 1 y 10 bar, pero el tamaño de poro de sus membranas no logra retener sales ni compuestos traza[cite: 2].
* **Ósmosis Inversa:** Requiere altas presiones (10 a 80 bar), sufre ensuciamiento severo por materia orgánica y coloidal, eleva la demanda energética y genera salmuera residual[cite: 2].
* **Tratamientos Biológicos:** Presentan alta sensibilidad a variaciones térmicas o hidráulicas y requieren una compleja gestión de lodos secundarios[cite: 2].

Para superar la baja escalabilidad de los reactores de plasma tradicionales que exigen cámaras de vacío selladas, este prototipo implementa un **reactor de plasma frío no sellado** que utiliza aire a presión atmosférica como gas ionizable en contacto directo con el agua[cite: 2]. El sistema IoT integrado monitorea continuamente la curva térmica del agua para comprobar empíricamente la transferencia de energía plasma-agua y asegurar que el reactor opere sin evaporación violenta ni degradación de los electrodos[cite: 1, 2].

## 2. Arquitectura de Software y Ciclo de Datos IoT

El software implementa el ciclo completo exigido para el prototipo IoT (captura continua, almacenamiento persistente, visualización en tiempo real y generación de información para la toma de decisiones)[cite: 1]:

* **Justificación de Resolución y Frecuencia de Muestreo:** El firmware en el Arduino Leonardo configura el sensor DS18B20 con una resolución de 10 bits (`sensors.setResolution(10)`), lo que establece un tiempo máximo de conversión de 187,5 ms y una pausa de bucle de 10 ms (`delay(10)`)[cite: 1, 3]. Esta decisión técnica permite capturar aproximadamente 5 muestras por segundo a 115200 baudios, detectando de forma inmediata el incremento térmico al encender el arco de plasma sin la latencia de 750 ms que impondría una resolución de 12 bits, dado que la precisión física del sensor es de ±0,5 °C[cite: 1, 3].
* **Filtrado de Interferencia Electromagnética (EMI):** Debido a que la descarga de alto voltaje en aire genera ruido electromagnético capaz de afectar la línea de datos, el código en C++ valida cada lectura mediante la condición `if (temperatura != DEVICE_DISCONNECTED_C)` antes de transmitir por el puerto serial[cite: 3]. En paralelo, el receptor en Python incorpora un bloque `try-except ValueError` y lectura con `timeout=0.05` para descartar tramas corruptas o incompletas sin interrumpir la ejecución del dashboard en vivo[cite: 1, 3].
* **Repositorio Persistente de Datos:** El script en Python registra cada medición válida con su respectiva marca temporal en segundos (`Tiempo_s`, `Temperatura_C`) dentro del archivo estructurado `temperaturas.csv`, ejecutando `archivo.flush()` en cada ciclo para garantizar la persistencia histórica de los datos incluso ante desconexiones abruptas[cite: 1, 3].
* **Generación de Información y Toma de Decisiones:** El dashboard en tiempo real (`matplotlib.pyplot` en modo interactivo `plt.ion()`) procesa las lecturas crudas para calcular la variación térmica acumulada ($\Delta T = T_{\text{actual}} - T_{\text{inicial}}$), el promedio y el valor máximo de la sesión[cite: 1, 3]. Superar el umbral de $\Delta T > +0,5\text{ }^\circ\text{C}$ (superior a la incertidumbre de ±0,5 °C del sensor) confirma transferencia térmica efectiva entre el plasma y el agua, mientras que un incremento excesivo alerta al operador para modular o detener la descarga y conservar el régimen no térmico[cite: 1, 2, 3].

## 3. Selección de Hardware y Diseño para la Reparación

* **Microcontrolador Arduino Leonardo:** Gestiona el bus digital en el pin 2 (`#define SENSOR_PIN 2`) y mantiene comunicación serial estable por USB a 115200 baudios con el computador donde corre el dashboard[cite: 1, 3].
* **Sensor Digital DS18B20:** Se seleccionó por su encapsulado sumergible, su rango operativo de -55 °C a 125 °C y su precisión especificada de ±0,5 °C (entre -10 °C y 85 °C)[cite: 1, 3]. Al transmitir datos digitales mediante el protocolo 1-Wire (9,6 Kbd) a través de un único pin con resistencia pull-up, evita la caída de tensión y la susceptibilidad al ruido eléctrico que sufriría un sensor analógico convencional cerca de la descarga de plasma[cite: 1, 3].
* **Diseño para la Reparación en Campo:** El prototipo evita el uso de uniones permanentes o sellados destructivos[cite: 1, 2]. El montaje modular permite retirar libremente el vaso Petri para limpieza, sustituir las agujas utilizadas como electrodos en caso de desgaste por oxidación, ajustar la altura del puente mediante tuercas en el eje vertical e intervenir la protoboard o el sensor DS18B20 sin dañar la estructura[cite: 1, 3].

## 4. Integración Mecánica y Gemelo 3D (Modelo Plasma V2)

El diseño estructural **Modelo Plasma V2** fue modelado paramétricamente en madera MDF de 5 mm de espesor para aislar eléctricamente los soportes y garantizar la alineación entre los electrodos y el volumen de agua[cite: 1, 3]:
* **Base de Petri (Lámina 3/4):** Plataforma de 110 x 110 mm y 20 mm de alto con una cavidad circular superior de Ø92 mm (5 mm de profundidad) que inmoviliza el vaso Petri debajo de la zona de descarga[cite: 3].
* **Base de Torre (Lámina 2/4):** Bloque de soporte de 80 x 80 mm y 25 mm de alto con perforación central de Ø12,5 mm para anclar el eje vertical de 130 mm de altura[cite: 3].
* **Puente de Electrodo (Lámina 4/4):** Brazo horizontal de 125 x 30 mm en MDF de 5 mm con un orificio de Ø12,5 mm para el eje vertical y 2 perforaciones separadas exactamente a 4 mm entre sí para alojar las agujas metálicas que actúan como electrodos sobre el agua[cite: 3].

## 5. Validación Experimental y Análisis de Fallas

* **Validación Cuantitativa de Contacto Plasma-Agua:** Durante las pruebas de monitoreo de 90 segundos, el sistema registró una línea base inicial cercana a 22,5 °C (entre los 0 y 10 s) seguida de un ascenso continuo hasta alcanzar aproximadamente 25,0 °C a los 90 segundos de exposición[cite: 3]. El incremento neto ($\Delta T \approx +2,5\text{ }^\circ\text{C}$) quintuplica el margen de error del sensor (±0,5 °C), demostrando cuantitativamente el contacto y la transferencia energética del plasma hacia el agua[cite: 1, 2, 3].
* **Análisis y Solución de Falla Detectada:** En las pruebas iniciales del Avance 2 se detectó ausencia de lecturas válidas e interferencias en la conexión entre el sensor y el modelo físico durante las descargas[cite: 3]. Esta falla se resolvió asegurando la conexión en protoboard con su resistencia pull-up en el bus 1-Wire, separando físicamente el cableado de la sonda respecto a los cables de alta tensión de las agujas e implementando el filtrado de lecturas `DEVICE_DISCONNECTED_C` y `try-except` en el software[cite: 1, 3].
