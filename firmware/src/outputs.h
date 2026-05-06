#pragma once
#include "common.h"
#include <stdint.h>

void outputs_init();
void outputs_set(uint8_t mask);
void outputs_xenon(bool on);
void outputs_gabari(bool on);
void outputs_fog(bool on);
void outputs_illumination(bool on);  /* radio/cluster illumination wire */
void outputs_all_off();
