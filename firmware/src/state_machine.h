#pragma once
#include <Arduino.h>

typedef enum {
    STATE_OFF,      /* без ключ, без скорошна активност */
    STATE_WELCOME,  /* отключено — welcome lights активни */
    STATE_ACC,      /* контакт без двигател, AUTO режим */
    STATE_DRL,      /* двигател работи, AUTO режим */
    STATE_GOODBYE,  /* двигател спря — goodbye lights активни */
    STATE_MANUAL,   /* копчето НЕ е на AUTO — не правим нищо */
} sm_state_t;

void        sm_init();
void        sm_tick();
sm_state_t  sm_state();
const char* sm_state_name();
