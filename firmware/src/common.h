#pragma once

#define LOOP_MS     50u     /* ms per main loop tick */
#define LOOP_HZ     (1000u / LOOP_MS)

/* Light output bitmask — used across config, outputs, state machine */
#define LIGHT_NONE   0x00u
#define LIGHT_GABARI 0x01u
#define LIGHT_FOG    0x02u
#define LIGHT_XENON  0x04u
#define LIGHT_ALL    (LIGHT_GABARI | LIGHT_FOG | LIGHT_XENON)
