#pragma once
#include "common.h"
#include <Arduino.h>

struct Config {
    uint8_t  welcome_lights;    /* LIGHT_* bitmask */
    uint16_t welcome_duration;  /* seconds, 0 = disabled */
    uint8_t  goodbye_lights;    /* LIGHT_* bitmask */
    uint16_t goodbye_duration;  /* seconds, 0 = disabled */
    uint8_t  acc_lights;        /* LIGHT_* bitmask */
    bool     acc_enabled;
};

extern Config cfg;

void    config_load();
void    config_save();
void    config_reset_defaults();
bool    config_set(const String& key, const String& value);
String  config_to_string();
String  lights_to_str(uint8_t mask);
