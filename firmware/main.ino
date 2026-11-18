// ============================================================================
// PROYECTO: Purificación de Agua Mediante Contacto Directo con Plasma (TEI201)
// ARCHIVO: firmware/main.ino
// PLACA: Arduino Leonardo | SENSOR: DS18B20 (Protocolo 1-Wire)
// ============================================================================

#include <OneWire.h>
#include <DallasTemperature.h>

const int pinDatos = 2;
const unsigned long intervalo = 250;

OneWire oneWire(pinDatos);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(9600);
  sensors.begin();
  sensors.setResolution(10);

  Serial.println("tiempo_s,temperatura_C");
}

void loop() {
  unsigned long inicio = millis();

  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);

  if (tempC != DEVICE_DISCONNECTED_C) {
    Serial.print(millis() / 1000.0, 3);
    Serial.print(",");
    Serial.println(tempC, 2);
  }

  unsigned long transcurrido = millis() - inicio;

  if (transcurrido < intervalo) {
    delay(intervalo - transcurrido);
  }
}

