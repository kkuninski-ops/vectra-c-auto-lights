/*
 * Vectra C Auto Lights Controller
 * Target : ESP32 DevKit v1
 * Framework: Arduino (PlatformIO)
 *
 * Функции:
 *   DRL       — ксенон + габарити при работещ двигател (AUTO режим)
 *   Welcome   — конфигурируеми светлини при отключване
 *   Goodbye   — конфигурируеми светлини при изгасване
 *   ACC       — конфигурируеми светлини при контакт без двигател
 *   BLE       — конфигурация от телефон (Nordic UART Service)
 *
 * Всичко важи САМО при AUTO позиция на копчето за светлини.
 * При ръчни позиции (0 / габарити / ниски) — factory поведение.
 */

#include <Arduino.h>
#include "config.h"
#include "outputs.h"
#include "inputs.h"
#include "ble_config.h"
#include "state_machine.h"
#include "common.h"

void setup() {
    Serial.begin(115200);
    outputs_init();
    inputs_init();
    config_load();
    ble_init();
    sm_init();
    Serial.println("[boot] Vectra Auto Lights ready");
}

void loop() {
    inputs_update();
    sm_tick();
    ble_tick();
    delay(LOOP_MS);
}
