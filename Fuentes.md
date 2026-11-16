---

### 2. `FUENTES.md` (**¡Obligatorio para evitar el nota 1,0!**)
Este documento declara todas las librerías, códigos externos y el uso de inteligencia artificial durante el desarrollo del software.

```markdown
# Declaración de Fuentes y Uso de Inteligencia Artificial

Este documento da cumplimiento a los requisitos obligatorios de la evaluación de Software de la asignatura Taller de Diseño (UAI)[cite: 2].

## 1. Librerías y Dependencias Externas
* **OneWire.h (Arduino IDE):** Utilizada para gestionar la comunicación 1-wire con el sensor DS18B20[cite: 1]. (Fuente: Repositorio oficial de librerías de Arduino).
* **DallasTemperature.h (Arduino IDE):** Librería complementaria para simplificar la lectura de temperatura del sensor DS18B20[cite: 1].
* **pyserial (Python):** Utilizada para la lectura en tiempo real del puerto serial proveniente del microcontrolador Arduino Leonardo[cite: 1].
* **matplotlib.pyplot (Python):** Utilizada para el despliegue dinámico de la gráfica de temperatura frente al tiempo[cite: 1].

## 2. Código Externo Adaptado
* Estructuras de lectura serial y almacenamiento en archivos `.csv` basadas en ejemplos estándar de comunicación serial en Python y la documentación oficial de `pyserial`.

## 3. Uso de Herramientas de Inteligencia Artificial
* **Herramientas utilizadas:** Asistentes de inteligencia artificial basados en modelos de lenguaje grandes (LLMs).
* **Aplicaciones y adaptaciones:** Apoyo en la depuración de la sintaxis del script en Python para la visualización en tiempo real con `matplotlib`, y en la redacción y estructuración de la documentación técnica del repositorio. 
* **Declaración de comprensión:** Los integrantes del grupo comprenden a cabalidad el funcionamiento del código implementado y son capaces de explicar las decisiones técnicas adoptadas en el sistema de adquisición de temperatura.

