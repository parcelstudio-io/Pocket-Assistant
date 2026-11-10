// Wi-Fi station with the project's transmit-power cap applied after every radio start.
#pragma once
#include <stdbool.h>

typedef void (*wifi_link_cb_t)(bool connected);

void wifi_link_start(wifi_link_cb_t cb);
bool wifi_link_connected(void);
