# Purificación de agua mediante contacto directo con plasma

Repositorio oficial del proyecto para la asignatura **Taller de Diseño, Sección 1** de la Universidad Adolfo Ibáñez.

## 👥 Integrantes
* Angelo Fisicaro
* Franco Fisicaro
* Francisco Osorio
* Joaquín Vásquez

* **Profesor:** Camilo Vásquez
* **Ayudante:** Martín Raguileo

---

## 📌 Resumen del Proyecto
La creciente escasez hídrica y contaminación exigen alternativas eficientes frente a las limitaciones de las tecnologías tradicionales (como ósmosis inversa o tratamientos biológicos). Este proyecto propone el desarrollo de un **reactor de plasma no sellado** que opera en contacto directo con el ambiente, utilizando aire como gas ionizable para la degradación destructiva de microcontaminantes.

## 📂 Estructura del Repositorio
- `codigo/`: Códigos fuente en Arduino IDE (`.ino`) y procesamiento de datos en Python (`.py`)[cite: 2].
- `planos/`: Planos técnicos del prototipo (Modelo V2: Base de torre, base de Petri y puente de electrodos)[cite: 2].
- `informes/`: Documentación y avances del proyecto.
- `imagenes/`: Fotografías de los prototipos experimentales y esquemas[cite: 1, 2].

## 📊 Sistema Electrónico y Validación
Se implementó un sistema de adquisición de temperatura utilizando:
* **Microcontrolador:** Arduino Leonardo[cite: 2].
* **Sensor:** DS18B20 (comunicación 1-wire)[cite: 2].
* **Monitoreo:** Script en Python con librerías `pyserial` y `matplotlib` para graficar el comportamiento térmico en tiempo real y exportar los datos a un archivo `.csv`[cite: 2].

