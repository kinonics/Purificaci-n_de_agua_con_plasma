// ============================================================================
// PROYECTO: Purificación de Agua Mediante Contacto Directo con Plasma (TEI201)
// ARCHIVO: firmware/main.ino
// PLACA: Arduino Leonardo | SENSOR: DS18B20 (Protocolo 1-Wire)
// ============================================================================

#include <OneWire.h>            // Importa la librería para el protocolo de comunicación 1-Wire (1 solo cable de datos)
#include <DallasTemperature.h>  // Importa la librería específica para convertir los datos del sensor DS18B20 a grados Celsius

#define SENSOR_PIN 2            // Define el pin digital 2 del Arduino Leonardo como línea de datos del sensor DS18B20
#define BAUD_RATE 115200        // Define la velocidad del puerto serial en 115200 baudios para transmisión rápida hacia Python
#define SENSOR_RESOLUTION 10    // Define resolución de 10 bits (incrementos de 0.25 °C y tiempo máximo de conversión de 187.5 ms)
#define SAMPLE_DELAY_MS 10      // Define una pausa mínima de 10 ms entre ciclos (frecuencia determinada por la conversión de 187.5 ms)

OneWire oneWire(SENSOR_PIN);             // Crea el objeto oneWire asignado al pin digital 2 para gestionar el bus de datos
DallasTemperature sensors(&oneWire);     // Crea el objeto sensors pasándole la referencia del bus oneWire para controlar el DS18B20

// Función de configuración inicial: se ejecuta una sola vez al encender o reiniciar el Arduino Leonardo
void setup() {
  Serial.begin(BAUD_RATE);               // Inicializa la comunicación serial por USB a 115200 baudios
  sensors.begin();                       // Inicializa el bus 1-Wire y detecta el sensor DS18B20 conectado
  
  // Justificación técnica de muestreo: 10 bits equilibra precisión y velocidad (~5 muestras por segundo),
  // ideal para detectar rápido el contacto térmico del arco de plasma sin bloquear el microcontrolador.
  sensors.setResolution(SENSOR_RESOLUTION); // Configura la resolución interna del conversor ADC del sensor en 10 bits
}

// Función principal: se ejecuta en bucle continuo mientras el dispositivo esté energizado
void loop() {
  sensors.requestTemperatures();         // Envía el comando por el bus 1-Wire para que el sensor realice una medición térmica
  
  float temperatura = sensors.getTempCByIndex(0); // Obtiene la temperatura en °C del primer sensor (índice 0) conectado al bus

  // Validación de integridad: descarta lecturas corruptas (-127.0 °C = DEVICE_DISCONNECTED_C)
  // que pueden ocurrir por ruido electromagnético (EMI) durante el disparo de alto voltaje del plasma.
  if (temperatura != DEVICE_DISCONNECTED_C && temperatura > -55.0 && temperatura < 125.0) {
    unsigned long tiempo = millis();     // Captura el tiempo transcurrido en milisegundos desde que se encendió el Arduino
    
    // Envío de trama estructurada CSV por puerto serial: "tiempo_ms,temperatura_C"
    Serial.print(tiempo);                // Imprime el tiempo en milisegundos sin salto de línea
    Serial.print(",");                   // Imprime la coma separadora para que Python divida ambos valores fácilmente
    Serial.println(temperatura, 2);      // Imprime la temperatura con 2 decimales y agrega salto de línea (\n) al final
  }

  delay(SAMPLE_DELAY_MS);                // Espera 10 ms antes de iniciar la siguiente lectura para estabilizar el bus serial
}
