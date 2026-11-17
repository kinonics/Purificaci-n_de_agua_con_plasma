# Purificación de Agua Mediante Contacto Directo con Plasma

Sistema de generación de plasma frío en aire a presión atmosférica para el tratamiento de agua en un vaso Petri, integrado con un sistema IoT de captura continua, almacenamiento local estructurado y monitoreo térmico en tiempo real para validar la transferencia de energía plasma-agua.

## 👥 Integrantes del Equipo
* Angelo Fisicaro
* Franco Fisicaro
* Francisco Osorio
* Joaquín Vásquez
* **Asignatura:** TEI201 — Taller de Diseño en Ingeniería (Sección 1, UAI)
* **Profesor:** Camilo Vásquez Wilson | **Ayudante:** Martín Raguileo

## 📌 Problema que Resuelve (Referencia al Avance 1)
Los métodos convencionales de tratamiento hídrico presentan limitaciones críticas frente a microcontaminantes emergentes (fármacos, pesticidas y disruptores endocrinos): la ultrafiltración no retiene compuestos traza, la ósmosis inversa sufre ensuciamiento de membranas con alto consumo energético y los tratamientos biológicos generan lodos residuales. Este proyecto implementa un reactor de plasma no sellado en contacto directo con el agua que degrada contaminantes mediante oxidación avanzada, utilizando un sistema de monitoreo térmico continuo para comprobar empíricamente la interacción entre la descarga de plasma y el agua.

## 🛠️ Componentes Necesarios para Replicar el Hardware
* 1x Microcontrolador Arduino Leonardo.
* 1x Sensor de temperatura digital impermeable DS18B20 (rango -55 °C a 125 °C, precisión ±0,5 °C, protocolo 1-Wire).
* 1x Protoboard, cables jumper y resistencia pull-up / variable.
* 2x Agujas metálicas (electrodos de descarga separados a 4 mm).
* 1x Vaso Petri de vidrio (encaje de 92 mm de diámetro).
* Estructura modular **Modelo Plasma V2** en madera MDF de 5 mm (Base de Torre de 80x80x25 mm, Base de Petri de 110x110x20 mm, Puente de Electrodo de 125x30x5 mm y eje vertical de 130 mm con fijaciones desmontables).

## ⚙️ Instrucciones para Cargar el Firmware y Conectar el Dashboard
1. **Conexión de Hardware:** Conectar el pin de datos del sensor DS18B20 al pin digital 2 del Arduino Leonardo (`SENSOR_PIN 2`), junto con alimentación (VCC), tierra (GND) y su resistencia en la protoboard según el plano en `hardware/esquematico.pdf`.
2. **Carga del Firmware:**
   * Abrir el archivo `firmware/main.ino` en **Arduino IDE**.
   * Instalar las librerías `OneWire` y `DallasTemperature` desde el Gestor de Librerías.
   * Seleccionar la placa **Arduino Leonardo**, elegir el puerto COM correspondiente y subir el código.
3. **Conexión del Dashboard y Repositorio de Datos:**
   * Instalar las dependencias en Python ejecutando en la terminal:
```bash
pip install pyserial matplotlib
