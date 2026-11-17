# Protocolo Experimental y de Validación (Testing)

**Proyecto:** Purificación de Agua Mediante Contacto Directo con Plasma. \\
**Modelo Evaluado:** Modelo Plasma V2 (Estructura MDF 5mm + Vaso Petri) y Sistema de Adquisición DS18B20

## 1. ¿Qué se evaluará? (Objetivos de la Prueba)
1. **Contacto efectivo y transferencia térmica plasma-agua:** Comprobar empíricamente que el arco de plasma generado en aire impacta y transfiere energía térmica al volumen de agua contenido en el vaso Petri.
2. **Integración y estabilidad electrónica frente a interferencias:** Verificar que el sensor DS18B20 sumergido en el vaso Petri registre lecturas continuas válidas sin sufrir desconexiones ni bloqueos por interferencia electromagnética (EMI) derivada de la descarga de alto voltaje.

## 2. ¿Cómo se medirá? (Metodología e Instrumentación)
* **Montaje Físico Integrado:** Se dispone el vaso Petri (diámetro de encaje de 92 mm) sobre la Base de Petri de madera MDF de 5 mm, ubicando el Puente de Electrodo con las 2 agujas separadas a 4 mm entre sí directamente sobre la superficie del agua.
* **Instrumentación:** Sensor digital de temperatura DS18B20 (rango de -55 °C a 125 °C, precisión de ±0,5 °C) conectado mediante protocolo 1-Wire al pin digital 2 de un microcontrolador Arduino Leonardo (configurado a una resolución de 10 bits, tiempo de conversión de hasta 187,5 ms y velocidad serial de 115200 baudios).
* **Procedimiento Paso a Paso:**
  1. **Fase Basal (Control Ambiental):** Con la sonda DS18B20 inmersa en el vaso Petri y aislada de las agujas, se inicia el script en Python (`pyserial` y `matplotlib`) para registrar la temperatura inicial del agua sin descarga de plasma durante 60 segundos, estableciendo la línea base frente a la temperatura ambiente.
  2. **Fase de Activación (Disparo de Plasma):** Se acciona la descarga entre los electrodos sobre la superficie del agua manteniendo el monitoreo continuo en tiempo real en el dashboard local.
  3. **Fase Post-Descarga y Registro:** Se detiene la descarga y se continúa registrando la curva térmica hasta su estabilización, exportando automáticamente la serie temporal (`Tiempo_s`, `Temperatura_C`) al archivo `temperaturas.csv`.

## 3. ¿Qué criterios determinarán si cumple los objetivos? (Criterios de Aceptación)
* **Criterio de Éxito Térmico ($\Delta T$):** El contacto plasma-agua se considerará validado si el incremento de temperatura registrado ($\Delta T = T_{\text{final}} - T_{\text{inicial}}$) es estrictamente superior a la incertidumbre del sensor (**$\Delta T > 0,5\text{ }^\circ\text{C}$**) respecto a la variación de la línea base ambiental.
* **Criterio de Integridad de Datos:** El aislamiento e integración electrónica se considerará exitoso si el archivo `temperaturas.csv` registra una tasa de pérdida de paquetes inferior al 5% y el código no arroja lecturas de desconexión (`DEVICE_DISCONNECTED_C`) durante el encendido del arco eléctrico.
* **Criterio de Seguridad Operativa:** El arco de plasma debe mantenerse confinado entre los electrodos y la superficie del vaso Petri sin desviarse hacia la estructura de soporte de MDF ni hacia el cableado del sensor.
