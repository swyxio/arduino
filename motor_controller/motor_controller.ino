#include <ArduinoJson.h>

// Stepper motor pins
const int stepPin = 3;
const int dirPin = 4;

void setup() {
  Serial.begin(9600);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    // Create a JSON document
    StaticJsonDocument<200> doc;

    // Read the JSON string from Serial
    String jsonString = Serial.readStringUntil('\n');
    
    // Parse JSON
    DeserializationError error = deserializeJson(doc, jsonString);

    if (error) {
      Serial.println("Error parsing JSON");
      return;
    }

    // Get values from JSON
    const char* direction = doc["direction"];
    int steps = doc["steps"];

    // Set direction
    if (strcmp(direction, "clockwise") == 0) {
      digitalWrite(dirPin, HIGH);
    } else {
      digitalWrite(dirPin, LOW);
    }

    // Move motor
    for(int i = 0; i < steps; i++) {
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(500);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(500);
    }

    Serial.println("Movement complete");
  }
}