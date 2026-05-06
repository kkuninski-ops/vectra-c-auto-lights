#include "state_machine.h"
#include "common.h"
#include "config.h"
#include "inputs.h"
#include "outputs.h"

static sm_state_t _state       = STATE_OFF;
static uint32_t   _timer_ticks = 0;

static uint32_t secs_to_ticks(uint16_t s) {
    return (uint32_t)s * 1000u / LOOP_MS;
}

/* ── Влизане в всяко състояние ──────────────────────────────────────── */

static void enter_off() {
    _state = STATE_OFF;
    _timer_ticks = 0;
    outputs_all_off();
}

static void enter_welcome() {
    _state = STATE_WELCOME;
    _timer_ticks = secs_to_ticks(cfg.welcome_duration);
    outputs_set(cfg.welcome_lights);
}

static void enter_acc() {
    _state = STATE_ACC;
    _timer_ticks = 0;
    if (cfg.acc_enabled)
        outputs_set(cfg.acc_lights);
    else
        outputs_all_off();
}

static void enter_drl() {
    _state = STATE_DRL;
    _timer_ticks = 0;
    /* DRL = винаги ксенон + габарити */
    outputs_gabari(true);
    outputs_xenon(true);
    outputs_fog(false);
}

static void enter_goodbye() {
    _state = STATE_GOODBYE;
    _timer_ticks = secs_to_ticks(cfg.goodbye_duration);
    outputs_set(cfg.goodbye_lights);
}

static void enter_manual() {
    _state = STATE_MANUAL;
    _timer_ticks = 0;
    outputs_all_off();  /* factory BCM управлява всичко */
}

/* ── Tick ────────────────────────────────────────────────────────────── */

void sm_init() {
    enter_off();
}

void sm_tick() {
    bool acc    = inputs_acc();
    bool isauto = inputs_auto_mode();
    bool engine = inputs_engine();
    bool unlock = inputs_unlock_take();

    if (_timer_ticks > 0) _timer_ticks--;

    switch (_state) {

    case STATE_OFF:
        if (acc && !isauto) {
            enter_manual();
        } else if (acc && isauto && engine) {
            enter_drl();
        } else if (acc && isauto && !engine) {
            enter_acc();
        } else if (unlock && !acc) {
            /* отключване без ключ → welcome */
            if (cfg.welcome_duration > 0)
                enter_welcome();
        }
        break;

    case STATE_WELCOME:
        if (acc && !isauto) {
            enter_manual();
        } else if (acc && engine) {
            /* ключ + двигател по време на welcome → директно DRL,
             * без втори студен старт на ксенона */
            enter_drl();
        } else if (acc && !engine) {
            enter_acc();
        } else if (_timer_ticks == 0) {
            enter_off();
        }
        break;

    case STATE_ACC:
        if (!acc) {
            enter_off();
        } else if (!isauto) {
            enter_manual();
        } else if (engine) {
            enter_drl();
        }
        break;

    case STATE_DRL:
        if (!acc && !engine) {
            enter_off();
        } else if (!isauto) {
            enter_manual();
        } else if (!engine) {
            /* двигателят спря, ключът е още вътре */
            if (cfg.goodbye_duration > 0)
                enter_goodbye();
            else
                enter_acc();
        }
        break;

    case STATE_GOODBYE:
        if (engine) {
            /* двигателят запали отново в goodbye → DRL */
            enter_drl();
        } else if (!acc) {
            /* ключът се вади → гасим веднага */
            enter_off();
        } else if (_timer_ticks == 0) {
            /* таймерът изтече, ключът е още вътре */
            enter_acc();
        }
        break;

    case STATE_MANUAL:
        if (!acc) {
            enter_off();
        } else if (isauto) {
            /* шофьорът върна на AUTO */
            if (engine) enter_drl();
            else        enter_acc();
        }
        break;
    }
}

sm_state_t  sm_state()      { return _state; }

const char* sm_state_name() {
    switch (_state) {
    case STATE_OFF:     return "OFF";
    case STATE_WELCOME: return "WELCOME";
    case STATE_ACC:     return "ACC";
    case STATE_DRL:     return "DRL";
    case STATE_GOODBYE: return "GOODBYE";
    case STATE_MANUAL:  return "MANUAL";
    default:            return "UNKNOWN";
    }
}
