#pragma once
#include <stdbool.h>

void inputs_init();
void inputs_update();       /* извиква се всеки цикъл на loop() */

bool inputs_acc();          /* KL18 активен */
bool inputs_auto_mode();    /* копчето е на AUTO */
bool inputs_engine();       /* двигателят работи (алтернатор > 13.2V) */
bool inputs_unlock_take();  /* true еднократно при получен unlock pulse */

/* За debug/BLE статус */
uint32_t inputs_vbat_mv();  /* напрежение акумулатор в mV */
