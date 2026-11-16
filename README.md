# Purificación de agua mediante contacto directo con plasma

Repositorio oficial del proyecto para la asignatura **Taller de Diseño, Sección 1** de la Universidad Adolfo Ibáñez.

## 👥 Integrantes
* Angelo Fisicaro
* Franco Fisicaro
* Francisco Osorio
* Joaquín Vásquez

* **Profesor:** Camilo Vásquez
* **Ayudante:** Martín Raguileo

## 📌 Problemática y Descripción
La creciente escasez y contaminación hídrica exigen alternativas eficaces frente a las limitaciones de las tecnologías tradicionales (como ósmosis inversa o tratamientos biológicos, que generan lodos o sufren saturación de membranas). Este proyecto propone el desarrollo de un **reactor de plasma no sellado** que opera en contacto directo con el ambiente, utilizando aire como gas ionizable para la degradación destructiva de microcontaminantes.

## 🛠️ Componentes Utilizados
* Microcontrolador Arduino Leonardo.
* Sensor de temperatura DS18B20 (comunicación 1-wire).
* Protoboard, cables de conexión y resistencia pull-up.
* Estructura modular de madera MDF de 5mm (Modelo Plasma V2) y vaso Petri.

## ⚙️ Instrucciones de Instalación y Uso
1. **Hardware:** Conectar el sensor DS18B20 al pin digital 2 de Arduino Leonardo según el esquemático en la carpeta `hardware/`.
2. **Firmware:** Cargar el código `adquisicion_temperatura.ino` (ubicado en la carpeta `firmware/`) usando Arduino IDE[cite: 1].
3. **Dashboard / Monitoreo:** Instalar las librerías de Python necesarias ejecutando en consola:
   ```bash
   pip install pyserial matplotlib
