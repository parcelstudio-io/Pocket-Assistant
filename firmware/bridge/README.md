# A1 LAN voice bridge

This host program lets the A1's existing Xiaozhi WebSocket firmware exchange
live voice with the OpenAI Realtime API. The A1 sends 16 kHz Opus audio to this
computer. The bridge decodes and upsamples it to 24 kHz PCM for Realtime, then
encodes the reply as 24 kHz Opus for A1. The OpenAI API key stays on the host.

The current A1 build holds its amplifier in mute. The bridge can exercise the
microphone and network path, but **you will not hear a reply from A1 until the
speaker and amplifier have been connected and qualified and a separate firmware
build enables the amplifier**. Do not enable that output just to test this
bridge.

## Host setup

The computer and A1 must be on the same trusted Wi-Fi network. The computer
must remain on while using A1 voice. Python 3.11+ and the system `libopus`
library are required. From the repository root:

```sh
uv venv firmware/.work/bridge-venv
uv pip install --python firmware/.work/bridge-venv/bin/python -r firmware/bridge/requirements.txt
```

The repository's A1 setup creates an ignored `firmware/.work/bridge.env` file
with two different random LAN secrets. If that file is absent, create it with
two independent random tokens and limit it to your user account:

```sh
umask 077
printf 'A1_OTA_TOKEN=%s\nA1_BRIDGE_TOKEN=%s\n' \
  "$(openssl rand -hex 24)" "$(openssl rand -hex 24)" \
  > firmware/.work/bridge.env
```

Load it in the terminal that will run the bridge, then provide an OpenAI API
key with Realtime API access:

```sh
set -a
source firmware/.work/bridge.env
set +a
read -rsp 'OpenAI API key: ' OPENAI_API_KEY; echo
export OPENAI_API_KEY
```

Find the computer's Wi-Fi IP and start the server, replacing `192.168.1.10`
with that address:

```sh
PYTHONPATH=firmware firmware/.work/bridge-venv/bin/python -m bridge.server \
  --host 192.168.1.10 --advertise-host 192.168.1.10
```

The bridge listens on port 8765. Its HTTP health endpoint is
`http://192.168.1.10:8765/health`.

## A1 provisioning

Build the local assistant variant with the computer's Wi-Fi IP and the OTA
secret. For the current host address, run from the repository root:

```sh
source firmware/.work/bridge.env
source firmware/.work/esp-idf/export.sh
firmware/scripts/build.sh --assistant-local \
  --bridge-url="http://192.168.1.171:8765/ota/${A1_OTA_TOKEN}"
```

Flash the resulting merged image at address `0x0` using the firmware project's
flash instructions. This full-image flash clears saved Wi-Fi settings, so
provision A1 onto the Wi-Fi network again. The firmware posts its
system info to the local OTA URL at startup. The bridge returns a Xiaozhi
WebSocket URL, a separate WebSocket bearer token, and protocol version 1. No
Xiaozhi account activation is involved.

The OTA URL secret is stored on A1 and travels over HTTP on your Wi-Fi LAN.
Use only a private, trusted network; do not forward port 8765 to the Internet.
The OTA endpoint will not return the WebSocket token without the secret URL.
The API key is never sent to A1. Restart the bridge with the same secrets if
A1 retains its provisioned URL and WebSocket settings.

## Checks

```sh
PYTHONPATH=firmware firmware/.work/bridge-venv/bin/python -m unittest discover \
  -s firmware/bridge/tests -v
```

Tests cover Opus conversion, the Xiaozhi hello and OTA bootstrap, WebSocket
authorization, audio transfer and TTS state ordering against a mocked Realtime
connection. This workspace has no `OPENAI_API_KEY`, so no live API call was
made. The tests do not validate the A1 speaker circuit.

The bridge uses the [Realtime WebSocket API](https://developers.openai.com/api/docs/guides/voice-websockets),
[conversation audio events](https://developers.openai.com/api/docs/guides/realtime-conversations),
and [server VAD](https://developers.openai.com/api/docs/guides/realtime-vad).
