# Purificación de Agua Mediante Contacto Indirecto con Plasma

Sistema de generación de plasma frío en aire a presión atmosférica para el tratamiento de agua en un vaso Petri, integrado con un sistema IoT en lazo cerrado (`v2`) de captura continua, almacenamiento local estructurado, monitoreo térmico en tiempo real y control automático de un módulo relé de prueba de banco para validar la transferencia de energía plasma-agua.

## Integrantes del Equipo
* **Grupo 2**
* Angelo Fisicaro
* Franco Fisicaro
* Francisco Osorio
* Joaquín Vásquez
* **Asignatura:** TEI201 — Taller de Diseño en Ingeniería (Sección 1, UAI)
* **Profesor:** Camilo Vásquez Wilson | **Ayudante:** Martín Raguileo

## Problema que Resuelve (Referencia al Avance 1)
Los métodos convencionales de tratamiento hídrico presentan limitaciones críticas frente a microcontaminantes emergentes (fármacos, pesticidas y disruptores endocrinos): la ultrafiltración no retiene compuestos traza, la ósmosis inversa sufre ensuciamiento de membranas con alto consumo energético y los tratamientos biológicos generan lodos residuales. Este proyecto implementa un reactor de plasma frío no sellado en aire a presión atmosférica en contacto indirecto con el agua para degradar contaminantes mediante oxidación avanzada, utilizando un sistema IoT de monitoreo térmico continuo para comprobar empíricamente la interacción energética entre la descarga de plasma y el agua.

## Componentes Necesarios para Replicar el Hardware
* 1x Microcontrolador **Arduino Leonardo**.
* 1x Sensor de temperatura digital impermeable **DS18B20** (rango -55 °C a 125 °C, precisión ±0,5 °C, protocolo 1-Wire).
* 1x **Módulo relé** (actuador de prueba de banco para validar el corte automático por temperatura).
* 1x Protoboard, cables jumper y resistencia pull-up / variable.
* 1x Fuente de alto voltaje para generación de plasma frío en aire *(mantener físicamente desconectada durante pruebas de conmutación del relé y demostraciones de banco)*.
* 2x Agujas metálicas (electrodos de descarga separados a 4 mm).
* 1x Vaso Petri de vidrio (encaje de 60 mm de diámetro).
* 1x Lámina de cobre (40 × 40 mm con lengüeta lateral) como electrodo pasivo de referencia a tierra (0 V).
* Estructura modular desmontable **Modelo Plasma V2** en madera MDF de 5,5 mm (Base de Torre de 80 × 80 × 25 mm, Base de Petri de 110 × 110 × 20 mm, Puente de Electrodo de 125 × 30 × 5 mm y eje vertical de 130 mm con fijaciones desmontables).

## Estructura del Repositorio
* [firmware/](firmware/) — Código fuente en Arduino C++ (`main.ino`) y dashboard de monitoreo y control en Python (`registro_temperatura_v2.py`).
* [hardware/](hardware/) — Esquemático eléctrico (`esquematico.pdf`), lista de materiales con costos (`BOM.xlsx`) y fotografías del prototipo desde múltiples ángulos.
* [diseno-3D/](diseno-3D/) — Modelo paramétrico y gemelo 3D en Fusion 360 (`.f3d`), planos técnicos en PDF, corte láser (`.dxf`) y renders.
* [testing/](testing/) — Protocolo experimental, subcarpeta `mediciones/` con logs cuantitativos por sesión (`temperaturas.csv` y `metadatos.json`) y análisis de fallas.
* [docs/](docs/) — Justificación técnica del sistema IoT (`justificacion_tecnica.md`), informe técnico y documentación complementaria.
* [FUENTES.md](FUENTES.md) — Declaración obligatoria de librerías, código externo adaptado, bibliografía científica y uso de herramientas de IA.

## Instrucciones para Cargar el Firmware y Conectar el Dashboard

### 1. Conexión de Hardware
Conectar el pin de datos del sensor **DS18B20** al pin digital 2 del Arduino Leonardo (`SENSOR_PIN 2`), junto con alimentación (`VCC`), tierra (`GND`), la resistencia del bus 1-Wire en la protoboard y el **módulo relé de prueba** según el diagrama en `hardware/esquematico.pdf`. Separar físicamente el cableado de la sonda respecto a los conductores de alta tensión para mitigar interferencias electromagnéticas (EMI).

### 2. Carga del Firmware (`Arduino Leonardo`)
1. Abrir `firmware/main.ino` en **Arduino IDE**.
2. Instalar las librerías `OneWire` y `DallasTemperature` desde el Gestor de Librerías.
3. Seleccionar la placa **Arduino Leonardo** y su puerto COM correspondiente.
4. Subir el código (configurado con resolución de **10 bits**, muestreo nominal a **4 Hz**, comunicación serial a **115200 baudios**, trama `DATA,milisegundos,temperatura,rele`, comandos seriales `I/P/H/T` y límite de parada de 30 s en el microcontrolador).
5. **Cerrar el Monitor Serial y el Plotter Serial** de Arduino IDE antes de abrir el dashboard para liberar el puerto USB.

### 3. Instalación de Dependencias del Dashboard (`Python`)
Instalar las librerías externas requeridas ejecutando en la terminal:

```bash
python -m pip install pyserial matplotlib
