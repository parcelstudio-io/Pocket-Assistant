// The LED filament on GPIO0: LEDC PWM at 5 kHz, the only status light.
//   rest       a dim pool on the desk (HOLO_LAMP_REST_PCT)
//   listening  brighter while the button is held (HOLO_LAMP_LISTEN_PCT)
//   thinking   a slow breath between rest and HOLO_LAMP_THINK_PCT while the desktop works
#pragma once

typedef enum { LAMP_REST, LAMP_LISTENING, LAMP_THINKING } lamp_mode_t;

void lamp_boot_low(void);   // first thing in app_main: the pin is driven low before anything else runs
void lamp_start(void);      // PWM on at the rest level, plus the task that slews and breathes
void lamp_set(lamp_mode_t mode);
