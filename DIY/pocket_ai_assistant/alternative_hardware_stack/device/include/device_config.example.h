#pragma once

// Copy this file to device_config.h. The real file is ignored by Git.
// Keep the local server on a private, trusted LAN; do not port-forward it.
#define POCKET_WIFI_SSID "your-2.4-ghz-wifi-name"
#define POCKET_WIFI_PASSWORD "your-wifi-password"

// Use the host computer's private-LAN IP address, not localhost and not the
// server's loopback review URL. CoreS3-SE interprets localhost as itself.
#define POCKET_SERVER_URL "http://192.168.1.10:8787"

// LAN mode requires POCKET_AI_TOKEN. Copy that same value here.
#define POCKET_DEVICE_TOKEN ""

// The review scaffold sends this text after a press-and-release gesture.
// Replacing it with captured audio + local STT is a later, explicit milestone.
#define POCKET_DEMO_PROMPT \
    "Introduce yourself as a cheerful pocket assistant in one short sentence."
