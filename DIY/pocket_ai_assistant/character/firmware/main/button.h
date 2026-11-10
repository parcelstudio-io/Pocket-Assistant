// The one button: GPIO10 to ground, debounced in a small task.
#pragma once
#include <stdbool.h>

typedef enum { BUTTON_PRESSED, BUTTON_RELEASED, BUTTON_LONG_PRESS } button_event_t;
typedef void (*button_cb_t)(button_event_t ev);

void button_init(button_cb_t cb);
bool button_is_down(void);
