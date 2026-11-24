# Documentación y Justificación Técnica del Sistema IoT (TEI201)

**Proyecto:** Purificación de Agua Mediante Contacto Indirecto con Plasma  
**Equipo:** Grupo 2 — Angelo Fisicaro, Franco Fisicaro, Francisco Osorio y Joaquín Vásquez  
**Asignatura:** TEI201 — Taller de Diseño en Ingeniería (Sección 1, UAI)  
**Profesor:** Camilo Vásquez Wilson | **Ayudante:** Martín Raguileo  

## 1. Conexión con la Problemática Original (Avance 1)

Las tecnologías convencionales de tratamiento hídrico presentan limitaciones operativas críticas frente a microcontaminantes emergentes como fármacos, pesticidas y disruptores endocrinos:
* **Ultrafiltración:** Opera entre 1 y 10 bar, pero el tamaño de poro de sus membranas no logra retener sales ni compuestos traza.
* **Ósmosis Inversa:** Requiere altas presiones (10 a 80 bar), sufre ensuciamiento severo por materia orgánica y coloidal, eleva la demanda energética y genera salmuera residual.
* **Tratamientos Biológicos:** Presentan alta sensibilidad a variaciones térmicas o hidráulicas y requieren una compleja gestión de lodos residuales.

Para superar la baja escalabilidad de los reactores de plasma tradicionales que exigen cámaras de vacío selladas, este prototipo implementa un **reactor de plasma frío no sellado** que opera con aire a presión atmosférica en contacto indirecto con el agua contenida en un vaso Petri. El sistema IoT integrado captura, almacena, visualiza y utiliza la curva térmica del agua en tiempo real para validar empíricamente la transferencia de energía plasma-agua y ejecutar un control automático en prueba de banco al alcanzar la temperatura objetivo definida por el operador.

## 2. Arquitectura de Software y Ciclo de Datos IoT (Versión 2)

El software (`firmware/main.ino` y `registro_temperatura_v2.py`) implementa el ciclo completo de datos del prototipo IoT: captura continua, validación, almacenamiento persistente, visualización en tiempo real y actuación automática en lazo cerrado:

* **Captura, Resolución y Protocolo Serial:** El firmware en el **Arduino Leonardo** (librerías `OneWire` y `DallasTemperature`) lee el sensor DS18B20 en el pin digital 2 (`SENSOR_PIN 2`) con resolución de **10 bits** (incrementos de 0,25 °C y tiempo máximo de conversión de 187,5 ms). Esta resolución ofrece mayor velocidad de respuesta que los 12 bits (750 ms) sin sacrificar exactitud práctica frente a la precisión física del sensor (±0,5 °C). El microcontrolador transmite por USB Serial a **115200 baudios** (`VELOCIDAD = 115200`) la trama estructurada `DATA,milisegundos,temperatura,rele` a una frecuencia nominal de **4 Hz** (~250 ms entre muestras).
* **Ingesta No Bloqueante y Protección ante Interferencia (EMI):** Debido a que las descargas de alto voltaje en aire pueden inducir ruido electromagnético en la línea de datos, la aplicación `registro_temperatura_v2.py` consulta el puerto serial de forma no bloqueante cada **100 ms** (`INTERVALO_GUI_MS = 100`) mediante el bucle de eventos de Tkinter (`root.after`), validando cada lectura antes de graficar o guardar:
  * Descarta encabezados, tramas corruptas o incompletas, mensajes de error y lecturas no finitas o fuera del rango físico del DS18B20 (-55 °C a 125 °C).
  * Utiliza la marca temporal del Arduino para asegurar intervalos reales precisos desde la primera lectura válida ($t = 0$) y detecta reinicios del microcontrolador.
  * Supervisa la continuidad del flujo de datos e interrumpe automáticamente la sesión con alerta visible si transcurren **5 segundos sin lecturas válidas** (`TIEMPO_SIN_DATOS_S = 5`).
* **Repositorio Local Persistente y Trazabilidad:** Cada sesión crea una carpeta única con fecha, hora y microsegundos dentro de `testing/mediciones/` (`YYYY-MM-DD_HH-MM-SS_ffffff/`), evitando sobrescribir ensayos anteriores. En ella se almacenan:
  * `temperaturas.csv` (columnas `tiempo_s,temperatura_C`), escrito y vaciado a disco (`flush()`) inmediatamente con cada lectura válida para resguardar los datos incluso ante desconexiones abruptas.
  * `metadatos.json`, con los parámetros y resumen estadístico de la sesión.
  * La interfaz permite reabrir experimentos guardados (`Abrir CSV`) reconstruyendo la curva, la tabla y las métricas sin necesidad de conectar el Arduino, además de exportar el gráfico en formato **PNG** (`Exportar PNG`).
* **Visualización, Generación de Información y Control por Relé:** El dashboard local en **Tkinter** con gráfico incrustado de **Matplotlib** (`FigureCanvasTkAgg`) y tabla desplazable calcula en vivo la temperatura actual, el tiempo transcurrido, la cantidad de mediciones, la variación térmica acumulada ($\Delta T = T_{\text{actual}} - T_{\text{inicial}}$), el promedio aritmético, la frecuencia real observada (Hz) y el estado del **Relé de prueba**. Antes de iniciar, el operador ingresa una **temperatura objetivo** (entre 0 y 100 °C), que se dibuja como línea de referencia horizontal y activa el control serial hacia Arduino mediante los comandos **`I/P/H/T`**:
  * **Meta mayor (Calentamiento):** Si la temperatura inicial es menor que el objetivo, el sistema mide calentamiento con el **relé encendido**.
  * **Meta menor (Enfriamiento):** Si la temperatura inicial es mayor que el objetivo, el sistema mide enfriamiento con el **relé apagado**.
  * **Cierre automático y límite de seguridad:** Cuando la temperatura cruza el objetivo en la dirección de la medición, el sistema ordena el corte (`APAGADO (ORDEN ENVIADA)`) y cierra el registro (`Arduino cerró la prueba: OBJETIVO_ALCANZADO`). Además, el firmware de Arduino incorpora un límite de parada a los **30 segundos**.
* **Alcance y Protocolo de Seguridad Eléctrica:** El lazo de actuación controla exclusivamente el **relé de prueba de banco**; por seguridad eléctrica, **la fuente de alta tensión debe permanecer físicamente desconectada** durante las pruebas de conmutación y demostraciones en sala.

## 3. Selección de Hardware y Diseño para la Reparación

* **Microcontrolador Arduino Leonardo:** Gestiona el bus digital del sensor (pin digital 2), el accionamiento del módulo relé y la comunicación USB Serial bidireccional a 115200 baudios con el computador, con selección dinámica del puerto COM desde el dashboard.
* **Sensor Digital Impermeable DS18B20:** Seleccionado por su cápsula sumergible, rango operativo de -55 °C a 125 °C y precisión especificada de ±0,5 °C (entre -10 °C y 85 °C). Al transmitir datos digitales mediante protocolo 1-Wire (9,6 Kbd) por un solo pin con resistencia pull-up/variable en protoboard, reduce la caída de tensión y la susceptibilidad al ruido eléctrico frente a sensores analógicos convencionales cerca de la zona de descarga.
* **Módulo Relé de Prueba de Banco:** Actúa como interruptor electromecánico controlado digitalmente desde el Arduino Leonardo para validar el cierre automático del ciclo IoT (sensado → procesamiento → actuación) con retroalimentación visual y sonora (clic de conmutación y LED indicador) manteniendo aislada la etapa de alto voltaje.
* **Electrodos y Referencia a Tierra:** La descarga de plasma se produce entre 2 agujas metálicas separadas a **4 mm** sobre un vaso Petri de vidrio (encaje de 60 mm de diámetro), complementado con una **lámina de cobre de 40 × 40 mm con lengüeta lateral** como electrodo pasivo de referencia a tierra (0 V).
* **Diseño para la Reparación en Campo:** El prototipo prescinde de pegamentos estructurales o sellados destructivos. Su ensamblaje modular con fijaciones desmontables permite retirar el vaso Petri para limpieza, sustituir las agujas desgastadas por oxidación, ajustar la altura del puente sobre el eje vertical e intervenir la protoboard, el módulo relé, la lámina de cobre o la sonda DS18B20 sin dañar la estructura.

## 4. Integración Mecánica y Gemelo 3D (Modelo Plasma V2)

La estructura **Modelo Plasma V2** fue modelada paramétricamente en Fusion 360 (`.f3d`, planos técnicos en PDF y archivos de corte láser `.dxf`) en madera **MDF de 5,5 mm** para aislar eléctricamente los soportes y mantener una geometría repetible entre los electrodos y el agua:
* **Base de Petri:** Plataforma de 110 × 110 × 20 mm encargada de inmovilizar el vaso Petri de vidrio (encaje de 60 mm de diámetro) junto con la lámina de cobre de referencia a tierra (40 × 40 mm con lengüeta lateral) bajo los electrodos.
* **Base de Torre:** Bloque de soporte de 80 × 80 × 25 mm que ancla el eje vertical de 130 mm mediante fijaciones desmontables.
* **Puente de Electrodo:** Brazo horizontal de 125 × 30 × 5 mm regulable en altura sobre el eje vertical, con 2 perforaciones separadas exactamente a 4 mm entre sí para fijar las agujas metálicas sobre la superficie del agua.

## 5. Validación Experimental, Análisis de Fallas y Mejoras

* **Validación Cuantitativa de Transferencia Plasma-Agua:** En pruebas de exposición al plasma durante 90 segundos, el sistema registró una línea base inicial cercana a 22,5 °C (0 a 10 s) seguida de un ascenso continuo hasta aproximadamente 25,0 °C a los 90 s. El incremento neto ($\Delta T \approx +2,5\text{ }^\circ\text{C}$) quintuplica el margen de error del sensor DS18B20 (±0,5 °C), demostrando empíricamente la transferencia energética entre el plasma y el agua.
* **Validación de Banco del Sistema IoT v2 (Adquisición, Control y Persistencia):** En prueba funcional completa con `registro_temperatura_v2.py` (fuente de alto voltaje desconectada y objetivo configurado en 28,00 °C desde una temperatura inicial de 20,75 °C), el sistema capturó **303 mediciones** continuas durante **75,505 s** a una frecuencia real estable de **4,00 Hz** (pasos exactos de 0,25 °C cada ~250 ms), registrando un incremento de **$\Delta T = +7,25\text{ }^\circ\text{C}$** y un promedio de **25,11 °C**. Al alcanzar exactamente 28,0000 °C, el sistema ejecutó el corte automático del relé (`APAGADO (ORDEN ENVIADA)` / `OBJETIVO_ALCANZADO`) y permitió reabrir íntegramente el registro desde `temperaturas.csv` sin conexión al Arduino.
* **Análisis y Solución de Falla Detectada:** En las pruebas iniciales (Avance 2) se presentó ausencia de lecturas válidas e interferencias en la conexión entre el sensor y el montaje físico durante las descargas. Esta falla se resolvió asegurando la conexión y resistencia del bus 1-Wire en la protoboard, separando físicamente el cableado de la sonda respecto a los conductores de alta tensión e incorporando validación de tramas, detección de reinicios y corte automático tras 5 s sin datos válidos en el software.
* **Limitación Crítica y Propuesta de Mejora:** Si bien la variación térmica ($\Delta T$) valida cuantitativamente el contacto energético plasma-agua y permite automatizar el corte por temperatura, no mide de forma directa la degradación química de contaminantes y puede verse influida por variaciones de la temperatura ambiente. Como mejora futura se plantea incorporar un segundo sensor de temperatura ambiental de control y complementar el protocolo con ensayos fisicoquímicos directos sobre el agua tratada.
