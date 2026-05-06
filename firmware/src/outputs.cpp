#include "outputs.h"
#include <Arduino.h>

/* HIGH = активен (реле затворено / MOSFET включен) */
#define PIN_XENON_OUT  26
#define PIN_GABARI_OUT 27
#define PIN_FOG_OUT    14
#define PIN_ILLUM_OUT  13   /* radio/cluster illumination — BC547 + 1N4007 */

void outputs_init() {
    pinMode(PIN_XENON_OUT,  OUTPUT);
    pinMode(PIN_GABARI_OUT, OUTPUT);
    pinMode(PIN_FOG_OUT,    OUTPUT);
    pinMode(PIN_ILLUM_OUT,  OUTPUT);
    outputs_all_off();
}

void outputs_xenon(bool on)        { digitalWrite(PIN_XENON_OUT,  on ? HIGH : LOW); }
void outputs_gabari(bool on)       { digitalWrite(PIN_GABARI_OUT, on ? HIGH : LOW); }
void outputs_fog(bool on)          { digitalWrite(PIN_FOG_OUT,    on ? HIGH : LOW); }
void outputs_illumination(bool on) { digitalWrite(PIN_ILLUM_OUT,  on ? HIGH : LOW); }

void outputs_set(uint8_t mask) {
    outputs_gabari(mask & LIGHT_GABARI);
    outputs_fog   (mask & LIGHT_FOG);
    outputs_xenon (mask & LIGHT_XENON);
}

void outputs_all_off() {
    outputs_xenon(false);
    outputs_gabari(false);
    outputs_fog(false);
    outputs_illumination(false);
}
