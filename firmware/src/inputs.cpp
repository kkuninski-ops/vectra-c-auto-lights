#include "inputs.h"
#include <Arduino.h>

/* ── Пинове ─────────────────────────────────────────────────────────── */

#define PIN_VBAT_ADC   34   /* АDC1_CH6 — работи с BLE */
#define PIN_ACC_IN     35   /* Оптрон KL18/ACC  — active LOW */
#define PIN_AUTO_IN    32   /* Оптрон AUTO сигнал — active LOW */
#define PIN_UNLOCK_IN  33   /* Оптрон unlock pulse — active LOW */

/* ── Прагове за напрежение ──────────────────────────────────────────── */
/* Делител 47kΩ / 10kΩ → Vadc = Vbat × 10/57
 * analogReadMilliVolts() връща mV на ADC входа
 * Vbat_mV = Vadc_mV × 57 / 10
 *
 * При 13.2V → Vadc = 2316 mV (двигател пали)
 * При 12.8V → Vadc = 2246 mV (двигател спира)
 */
#define ENGINE_ON_MV   13200u
#define ENGINE_OFF_MV  12800u

/* ── Дебаунс ────────────────────────────────────────────────────────── */
#define DEBOUNCE_TICKS 3u   /* × 50ms = 150ms */

/* ── Вътрешно състояние ─────────────────────────────────────────────── */

static bool _acc     = false;
static bool _auto    = false;
static bool _engine  = false;
static uint32_t _vbat_mv = 0;

static uint8_t _acc_cnt  = 0;
static uint8_t _auto_cnt = 0;

static volatile bool _unlock_flag = false;

void IRAM_ATTR _unlockISR() {
    _unlock_flag = true;
}

/* ── Init ────────────────────────────────────────────────────────────── */

void inputs_init() {
    pinMode(PIN_ACC_IN,    INPUT_PULLUP);
    pinMode(PIN_AUTO_IN,   INPUT_PULLUP);
    pinMode(PIN_UNLOCK_IN, INPUT_PULLUP);
    pinMode(PIN_VBAT_ADC,  INPUT);
    analogSetAttenuation(ADC_11db);

    attachInterrupt(digitalPinToInterrupt(PIN_UNLOCK_IN), _unlockISR, FALLING);
}

/* ── Четене на ADC с осредняване ────────────────────────────────────── */

static uint32_t read_vbat_mv() {
    uint32_t sum = 0;
    for (uint8_t i = 0; i < 8; i++) {
        sum += analogReadMilliVolts(PIN_VBAT_ADC);
        delay(1);
    }
    uint32_t vadc_mv = sum >> 3;
    return vadc_mv * 57u / 10u;    /* обратен делител */
}

/* ── Update — извиква се всеки цикъл ───────────────────────────────── */

static void debounce(bool raw, bool& state, uint8_t& cnt) {
    if (raw) {
        if (cnt < DEBOUNCE_TICKS) cnt++;
        if (cnt >= DEBOUNCE_TICKS) state = true;
    } else {
        if (cnt > 0) cnt--;
        if (cnt == 0) state = false;
    }
}

void inputs_update() {
    debounce(digitalRead(PIN_ACC_IN)  == LOW, _acc,  _acc_cnt);
    debounce(digitalRead(PIN_AUTO_IN) == LOW, _auto, _auto_cnt);

    _vbat_mv = read_vbat_mv();

    if (!_engine && _vbat_mv >= ENGINE_ON_MV)  _engine = true;
    if (_engine  && _vbat_mv <= ENGINE_OFF_MV) _engine = false;
}

/* ── Публични getter-и ──────────────────────────────────────────────── */

bool     inputs_acc()          { return _acc; }
bool     inputs_auto_mode()    { return _auto; }
bool     inputs_engine()       { return _engine; }
uint32_t inputs_vbat_mv()      { return _vbat_mv; }

bool inputs_unlock_take() {
    if (_unlock_flag) { _unlock_flag = false; return true; }
    return false;
}
