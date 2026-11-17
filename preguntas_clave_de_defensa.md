# Guía de Preparación: Defensa Avance #3 (TEI201)

**Proyecto:** Purificación de Agua Mediante Contacto Directo con Plasma  
**Integrantes:** Angelo Fisicaro, Franco Fisicaro, Francisco Osorio y Joaquín Vásquez  
**Profesor:** Camilo Vásquez Wilson | **Ayudante:** Martín Raguileo  

---

## 3. Preguntas Clave que el Profesor Puede Hacerles en la Defensa

De acuerdo con la pauta del **Avance #3 (Sección 3.6 y 6.3)**, el evaluador puede realizar preguntas a cualquier integrante del grupo sobre el funcionamiento del código (incluyendo las partes asistidas por IA), las decisiones de hardware, el modelo 3D y el protocolo de validación.

---

### A. Preguntas sobre Software, Código y Declaración de IA (30 %)

#### 1. ¿Por qué eligieron una resolución de 10 bits en el sensor DS18B20 dentro del código de Arduino?
* **Respuesta técnica:** En el sensor DS18B20 la resolución es configurable entre $9$ y $12\text{ bits}$. Elegimos **$10\text{ bits}$** (`sensors.setResolution(10)`) porque entrega incrementos de lectura de **$0,25\text{ }^\circ\text{C}$** con un tiempo máximo de conversión de **$187,5\text{ ms}$** (lo que permite capturar alrededor de $5\text{ muestras por segundo}$). Si hubiéramos usado $12\text{ bits}$, el sensor tardaría hasta $750\text{ ms}$ por cada lectura, haciendo mucho más lenta la detección en tiempo real del disparo de plasma, sin ganar exactitud real porque la **precisión física especificada** del sensor es de **$\pm 0,5\text{ }^\circ\text{C}$** (recordando que *resolución no es lo mismo que precisión*).

#### 2. ¿Por qué incluyeron la condición `if (temperatura != DEVICE_DISCONNECTED_C)` en Arduino y el bloque `try-except ValueError` en Python?
* **Respuesta técnica:** Porque nuestro reactor genera un arco de plasma en aire a alto voltaje, lo que produce **interferencia electromagnética (EMI)**. Si un pulso de ruido corrompe momentáneamente un paquete en el bus *1-Wire* (devolviendo $-127\text{ }^\circ\text{C}$, que equivale a `DEVICE_DISCONNECTED_C`) o envía una trama serial incompleta al computador, estas dos validaciones filtran y descartan la lectura corrupta sin que el dashboard en vivo se congele ni se detenga durante la demostración.

#### 3. ¿Cómo transforma su software los datos crudos en información útil para tomar decisiones?
* **Respuesta técnica:** El script en Python registra automáticamente la temperatura basal inicial ($T_0$) del agua antes de encender la descarga y calcula en cada instante la variación térmica ($\Delta T = T_{\text{actual}} - T_0$), el promedio y el valor máximo:
  * **Umbral de validación ($\Delta T \ge +0,5\text{ }^\circ\text{C}$):** Cuando el incremento supera la incertidumbre instrumental del sensor ($\pm 0,5\text{ }^\circ\text{C}$), el panel de estado cambia a **color verde**, confirmando estadísticamente que existe contacto y transferencia energética efectiva entre el plasma y el agua.
  * **Alerta de seguridad ($\Delta T \ge +3,0\text{ }^\circ\text{C}$):** Si el aumento térmico alcanza o supera $+3,0\text{ }^\circ\text{C}$, se activa una **alerta visual roja** indicando que se debe apagar o modular la fuente para evitar calentamiento excesivo, evaporación o deterioro de los electrodos, manteniendo el proceso dentro del régimen de plasma frío (no térmico).

#### 4. ¿Para qué sirven las funciones `while arduino.in_waiting:` y `archivo.flush()` en el código de Python?
* **Respuesta técnica:**
  * `while arduino.in_waiting:` revisa cuántos bytes hay esperando en el buffer serial y los lee todos antes de redibujar el gráfico. Esto evita que se acumule retraso (*lag*) entre lo que mide el Arduino Leonardo y lo que muestra la gráfica de `matplotlib`.
  * `archivo.flush()` fuerza al sistema operativo a guardar cada fila inmediatamente en el disco duro dentro de `temperaturas.csv`. Así garantizamos la **persistencia de los datos** incluso si el programa se interrumpe abruptamente.

---

### B. Preguntas sobre Hardware y Diseño para la Reparación (30 %)

#### 5. ¿Por qué seleccionaron el sensor DS18B20 en cápsula impermeable y el Arduino Leonardo?
* **Respuesta técnica:** El sensor **DS18B20** posee un encapsulado metálico sumergible que permite medir directamente el volumen de agua en el vaso Petri con un rango de **$-55\text{ }^\circ\text{C}$ a $125\text{ }^\circ\text{C}$** y una precisión de **$\pm 0,5\text{ }^\circ\text{C}$** (entre $-10\text{ }^\circ\text{C}$ y $85\text{ }^\circ\text{C}$). Además, utiliza el protocolo digital **1-Wire**, que requiere un único pin de datos (pin digital $2$) acompañado de una resistencia *pull-up*, reduciendo el cableado expuesto a interferencias frente al microcontrolador **Arduino Leonardo**.

#### 6. ¿Cómo cumple su prototipo con el criterio de "Diseño para la Reparación"?
* **Respuesta técnica:** A diferencia de un sistema sellado con adhesivos permanentes, el **Modelo Plasma V2** es una estructura modular de madera MDF de $5\text{ mm}$ con uniones mecánicas desmontables (tuercas y eje vertical roscado de $130\text{ mm}$ de altura). Esto permite retirar el vaso Petri (encaje de $\varnothing\text{ }92\text{ mm}$), reemplazar las $2$ agujas del puente de electrodos o cambiar el sensor DS18B20 y las conexiones en la protoboard en segundos sin dañar ni destruir ninguna pieza del ensamble.

---

### C. Preguntas sobre Diseño 3D y Tolerancias (20 %)

#### 7. ¿Cómo se integra el diseño 3D con la electrónica y qué dimensiones críticas consideraron?
* **Respuesta técnica:** El **Modelo Plasma V2** consta de tres piezas principales en MDF de $5\text{ mm}$:
  1. **Base de Petri ($110 \times 110 \times 20\text{ mm}$):** Incluye una cavidad circular de **$\varnothing\text{ }92\text{ mm}$** y $5\text{ mm}$ de profundidad para inmovilizar el vaso Petri justo debajo de la descarga.
  2. **Base de Torre ($80 \times 80 \times 25\text{ mm}$):** Posee una perforación central de **$\varnothing\text{ }12,5\text{ mm}$** que sostiene el eje vertical de $130\text{ mm}$.
  3. **Puente de Electrodo ($125 \times 30 \times 5\text{ mm}$):** Tiene un agujero de $\varnothing\text{ }12,5\text{ mm}$ para regular la altura sobre el agua mediante tuercas y dos perforaciones separadas exactamente a **$4\text{ mm}$** para fijar las $2$ agujas como electrodos de descarga, manteniendo alejado el cableado del sensor DS18B20 para evitar arcos parásitos.

---

### D. Preguntas sobre Testing, Validación y Problema Original (10 %)

#### 8. ¿El aumento de temperatura demuestra por sí solo que el agua quedó purificada de microcontaminantes?
* **Respuesta técnica:** No directamente, y lo declaramos de forma transparente en nuestro análisis. En esta etapa del prototipo, la medición de temperatura cumple el objetivo de **validar empíricamente el contacto físico y la transferencia de energía entre el plasma y el agua** (evidenciado en nuestras pruebas con un incremento sostenido desde $\sim 22,5\text{ }^\circ\text{C}$ hasta $\sim 25,0\text{ }^\circ\text{C}$ en $90\text{ segundos}$, superando ampliamente el margen de error de $\pm 0,5\text{ }^\circ\text{C}$ del sensor). La literatura científica (Foster, 2017; Malik, 2010) demuestra que cuando el plasma no térmico en aire entra en contacto con el agua, genera especies reactivas de oxígeno y nitrógeno (radicales hidroxilo, ozono) capaces de degradar microcontaminantes sin producir lodos ni saturar membranas como ocurre en la ósmosis inversa o tratamientos biológicos.