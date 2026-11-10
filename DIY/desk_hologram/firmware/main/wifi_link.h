// Wi-Fi station with the Pocket AI's transmit-power cap applied after every radio start. Copied from the first Pocket AI unchanged.
#pragma once
#include <stdbool.h>

typedef void (*wifi_link_cb_t)(bool connected);

void wifi_link_start(wifi_link_cb_t cb);
bool wifi_link_connected(void);
