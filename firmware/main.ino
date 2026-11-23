

  Protocolo 115200 baudios, comandos terminados por salto de linea:
    PC -> Arduino: T:30.0 (objetivo), I (iniciar), P (detener), H (latido)
    Arduino -> PC: DATA,milisegundos,temperatura,rele(0/1)
                   # OBJETIVO,30.000
                   # INICIADO,CALENTAMIENTO  o  # INICIADO,ENFRIAMIENTO
                   # FINALIZADO,MOTIVO


#include <OneWire.h>
#include <DallasTemperature.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

const byte PIN_DS18B20 = 2;
const byte PIN_RELE = 7;
// Conservamos el estado activo LOW de la prueba que funciono en este montaje.
const byte RELE_ACTIVO = LOW;
const byte RELE_INACTIVO = HIGH;

const unsigned long INTERVALO_MS = 250;           // 4 muestras/segundo nominales.
const unsigned long MAX_SIN_LATIDO_MS = 1500;      // Deteccion de PC desconectado.

OneWire oneWire(PIN_DS18B20);
DallasTemperature sensor(&oneWire);

char entrada[40] = {0};
byte pos = 0;

enum Modo { NINGUNO, CALENTAMIENTO, ENFRIAMIENTO };
Modo modo = NINGUNO;

bool sesionActiva = false;
bool releEncendido = false;
bool lecturaValida = false;
bool objetivoConfigurado = false;
float temperatura = NAN;
float objetivo = NAN;
unsigned long conversionEn = 0;
unsigned long lecturaEn = 0;
unsigned long latidoEn = 0;

// Unica funcion que cambia el estado fisico del rele.
void escribirRele(bool activar) {
  releEncendido = activar;
  digitalWrite(PIN_RELE, activar ? RELE_ACTIVO : RELE_INACTIVO);
}

void finalizar(const char* motivo) {
  escribirRele(false);
  bool estabaActiva = sesionActiva;
  sesionActiva = false;
  modo = NINGUNO;
  if (estabaActiva) {
    Serial.print(F("# FINALIZADO,"));
    Serial.println(motivo);
  }
}

void procesar(const char* cmd) {
  unsigned long ahora = millis();

  if (strcmp(cmd, "P") == 0 || strcmp(cmd, "p") == 0) {
    finalizar("ORDEN_MANUAL");
    Serial.println(F("# DETENIDO"));

  } else if (strcmp(cmd, "H") == 0) {
    latidoEn = ahora;

  } else if (strncmp(cmd, "T:", 2) == 0) {
    if (sesionActiva) {
      Serial.println(F("# ERROR,NO_CAMBIAR_OBJETIVO_DURANTE_PRUEBA"));
      return;
    }
    char* fin = nullptr;
    double valor = strtod(cmd + 2, &fin);
    if (fin == cmd + 2 || *fin != '\0' || !isfinite(valor)
        || valor < 0 || valor > 100) {
      Serial.println(F("# ERROR,OBJETIVO_INVALIDO"));
      return;
    }
    objetivo = (float)valor;
    objetivoConfigurado = true;
    Serial.print(F("# OBJETIVO,"));
    Serial.println(objetivo, 3);

  } else if (strcmp(cmd, "I") == 0 || strcmp(cmd, "i") == 0) {
    // No comenzar sin una lectura reciente y objetivo diferente de la actual.
    if (sesionActiva || !objetivoConfigurado || !lecturaValida ||
        ahora - lecturaEn > 1000 || temperatura == objetivo) {
      finalizar("INICIO_NO_PERMITIDO");
      Serial.println(F("# INICIO_DENEGADO"));
      return;
    }

    modo = temperatura < objetivo ? CALENTAMIENTO : ENFRIAMIENTO;
    latidoEn = ahora;
    sesionActiva = true;

    if (modo == CALENTAMIENTO) {
      // Solo para la simulacion de banco, sin generador conectado.
      escribirRele(true);
      Serial.println(F("# INICIADO,CALENTAMIENTO"));
    } else {
      // Enfriamiento pasivo: NO se energiza la salida del rele.
      escribirRele(false);
      Serial.println(F("# INICIADO,ENFRIAMIENTO"));
    }
  }
}

void setup() {
  // Estado apagado antes de establecer el pin como salida.
  digitalWrite(PIN_RELE, RELE_INACTIVO);
  pinMode(PIN_RELE, OUTPUT);
  escribirRele(false);

  Serial.begin(115200);
  sensor.begin();
  sensor.setResolution(10);          // Conversion ~187,5 ms; periodo ~250 ms.
  sensor.setWaitForConversion(false);
  sensor.requestTemperatures();
  conversionEn = millis();
  Serial.println(F("# LISTO,PRUEBA_SIN_GENERADOR"));
}

void loop() {
  unsigned long ahora = millis();

  // Comandos no bloqueantes desde la aplicacion Python.
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      entrada[pos] = '\0';
      if (pos > 0) procesar(entrada);
      pos = 0;
    } else if (pos < sizeof(entrada) - 1) {
      entrada[pos++] = c;
    } else {
      pos = 0;
      finalizar("COMANDO_DEMASIADO_LARGO");
      Serial.println(F("# ERROR,COMANDO_LARGO"));
    }
  }

  ahora = millis();
  if (ahora - conversionEn >= INTERVALO_MS) {
    float t = sensor.getTempCByIndex(0);
    sensor.requestTemperatures();
    conversionEn = ahora;

    // Error tipico -127 °C, 85 °C de arranque u otras lecturas invalidas.
    if (t == DEVICE_DISCONNECTED_C || !isfinite(t) || t == 85.0 ||
        t < -20 || t > 100) {
      lecturaValida = false;
      finalizar("ERROR_SENSOR");
      Serial.println(F("# ERROR_SENSOR"));
    } else {
      temperatura = t;
      lecturaValida = true;
      lecturaEn = ahora;

      // Ambas direcciones se detienen al CRUZAR el objetivo.
      if (sesionActiva) {
        if (modo == CALENTAMIENTO && temperatura >= objetivo)
          finalizar("OBJETIVO_ALCANZADO");
        else if (modo == ENFRIAMIENTO && temperatura <= objetivo)
          finalizar("OBJETIVO_ALCANZADO");
      }

      Serial.print(F("DATA,"));
      Serial.print(ahora);
      Serial.print(',');
      Serial.print(temperatura, 3);
      Serial.print(',');
      Serial.println(releEncendido ? 1 : 0);
    }
  }

  // Esto NO es un limite de duracion de la prueba: solo corta al perder PC.
  ahora = millis();
  if (sesionActiva && ahora - latidoEn >= MAX_SIN_LATIDO_MS)
    finalizar("SIN_COMUNICACION");
}
