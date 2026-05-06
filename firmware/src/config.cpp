#include "config.h"
#include <Preferences.h>

Config cfg;
static Preferences prefs;

void config_load() {
    prefs.begin("autolights", true);
    cfg.welcome_lights   = prefs.getUChar("wl_lights",  LIGHT_GABARI);
    cfg.welcome_duration = prefs.getUShort("wl_time",   30);
    cfg.goodbye_lights   = prefs.getUChar("gb_lights",  LIGHT_GABARI);
    cfg.goodbye_duration = prefs.getUShort("gb_time",   30);
    cfg.acc_lights       = prefs.getUChar("acc_lights", LIGHT_GABARI);
    cfg.acc_enabled      = prefs.getBool("acc_en",      true);
    prefs.end();
}

void config_save() {
    prefs.begin("autolights", false);
    prefs.putUChar("wl_lights",  cfg.welcome_lights);
    prefs.putUShort("wl_time",   cfg.welcome_duration);
    prefs.putUChar("gb_lights",  cfg.goodbye_lights);
    prefs.putUShort("gb_time",   cfg.goodbye_duration);
    prefs.putUChar("acc_lights", cfg.acc_lights);
    prefs.putBool("acc_en",      cfg.acc_enabled);
    prefs.end();
}

void config_reset_defaults() {
    cfg = { LIGHT_GABARI, 30, LIGHT_GABARI, 30, LIGHT_GABARI, true };
    config_save();
}

static uint8_t parse_lights(const String& s) {
    uint8_t mask = LIGHT_NONE;
    if (s.indexOf("GABARI") >= 0) mask |= LIGHT_GABARI;
    if (s.indexOf("FOG")    >= 0) mask |= LIGHT_FOG;
    if (s.indexOf("XENON")  >= 0) mask |= LIGHT_XENON;
    return mask;
}

bool config_set(const String& key, const String& value) {
    if      (key == "welcome.lights")   cfg.welcome_lights   = parse_lights(value);
    else if (key == "welcome.time")     cfg.welcome_duration = (uint16_t)value.toInt();
    else if (key == "goodbye.lights")   cfg.goodbye_lights   = parse_lights(value);
    else if (key == "goodbye.time")     cfg.goodbye_duration = (uint16_t)value.toInt();
    else if (key == "acc.lights")       cfg.acc_lights       = parse_lights(value);
    else if (key == "acc.enabled")      cfg.acc_enabled      = (value.toInt() != 0);
    else return false;
    config_save();
    return true;
}

String lights_to_str(uint8_t mask) {
    if (mask == LIGHT_NONE) return "NONE";
    String s;
    if (mask & LIGHT_GABARI) s += "GABARI+";
    if (mask & LIGHT_FOG)    s += "FOG+";
    if (mask & LIGHT_XENON)  s += "XENON+";
    s.remove(s.length() - 1);
    return s;
}

String config_to_string() {
    String s;
    s += "welcome.lights  = " + lights_to_str(cfg.welcome_lights)  + "\n";
    s += "welcome.time    = " + String(cfg.welcome_duration)        + "s\n";
    s += "goodbye.lights  = " + lights_to_str(cfg.goodbye_lights)  + "\n";
    s += "goodbye.time    = " + String(cfg.goodbye_duration)        + "s\n";
    s += "acc.lights      = " + lights_to_str(cfg.acc_lights)       + "\n";
    s += "acc.enabled     = " + String(cfg.acc_enabled ? "yes" : "no") + "\n";
    return s;
}
