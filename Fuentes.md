# 📚 Declaración de Fuentes y Uso de Inteligencia Artificial
**Proyecto:** Purificación de Agua Mediante Contacto Directo con Plasma  
**Asignatura:** Taller de Diseño — Universidad Adolfo Ibáñez (UAI)  

---

> **Aviso Importante de Cumplimiento:**  
> Este documento da cumplimiento oficial a los requerimientos obligatorios de la dimensión de Software de la asignatura[cite: 2]. *(Nota: La ausencia o vacío de este archivo asigna automáticamente la calificación mínima de 1,0).*

---

## ⚙️ 1. Librerías y Dependencias Externas

Para el funcionamiento del sistema de adquisición y monitoreo de temperatura, se emplearon las siguientes librerías de código abierto:

*   **`OneWire.h` (Arduino IDE):**  
    *   *Fuente:* Repositorio oficial de librerías de Arduino / Dallas Semiconductor.  
    *   *Aplicación:* Gestión de la comunicación por protocolo *1-wire* con el sensor de temperatura DS18B20[cite: 1].
*   **`DallasTemperature.h` (Arduino IDE):**  
    *   *Fuente:* Comunidad de desarrolladores de Arduino.  
    *   *Aplicación:* Simplificación de la lectura de datos térmicos y gestión de resoluciones del sensor DS18B20[cite: 1].
*   **`pyserial` (Python):**  
    *   *Fuente:* Índice de paquetes de Python (PyPI) / Documentación oficial de Python.  
    *   *Aplicación:* Lectura en tiempo real del flujo de datos transmitidos por el puerto serial desde el microcontrolador Arduino Leonardo[cite: 1].
*   **`matplotlib.pyplot` (Python):**  
    *   *Fuente:* Librería estándar de visualización científica en Python.  
    *   *Aplicación:* Generación de la interfaz gráfica dinámica (dashboard local) para la representación de temperatura frente al tiempo[cite: 1].

---

## 🛠️ 2. Fragmentos de Código Externo y Adaptaciones

*   **Estructura de Comunicación Serial:**  
    *   *Origen:* Ejemplos estándar de la documentación de PySerial y foros de desarrollo de Arduino.  
    *   *Adaptación:* Modificación de los tiempos de muestreo, manejo de excepciones (`try-except` para evitar interrupciones por pérdida de paquetes) y automatización del guardado directo en formato `.csv` (`temperaturas.csv`)[cite: 1].

---

## 🤖 3. Declaración del Uso de Inteligencia Artificial

*   **Herramientas Empleadas:** Asistentes basados en modelos de lenguaje avanzados (LLMs).
*   **Ámbito de Aplicación:**  
    *   Apoyo en la optimización y sintaxis del script de adquisición en Python para el gráfico en tiempo real con `matplotlib`[cite: 1].
    *   Estructuración y redacción de la documentación técnica del repositorio[cite: 2].
*   **Declaración de Dominio Técnico:**  
    *   *Los integrantes del grupo declaran comprender a cabalidad el funcionamiento íntegro del código implementado, poseyendo la capacidad plena para explicar las decisiones técnicas, esquemáticos y la lógica detrás del sistema de medición.*
