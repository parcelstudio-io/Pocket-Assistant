# Pip: the Pocket AI character

Our own firmware and server for board A1. No Xiaozhi, no third-party backend
account. The device shows a pair of animated eyes, you hold the button and
talk, your computer turns that into text, asks a language model, speaks the
answer back, and tells the eyes how to feel about it.

```text
┌──────────────────────────┐   one WebSocket, trusted Wi-Fi   ┌──────────────────────────────┐
│ A1 (ESP32-C3 SuperMini)  │ ───────────────────────────────► │ pocket-server (your computer) │
│  eyes on the OLED, 30 fps│   16 kHz PCM up while listening  │  STT  → brain → TTS           │
│  push-to-talk button     │ ◄─────────────────────────────── │  OpenAI by default            │
│  mic in, amp out         │   state · emotion · PCM down     │  Ollama / llama.cpp optional  │
└──────────────────────────┘                                   └──────────────────────────────┘
```

Status on 8 October 2026: the server passes 24 tests and talks to a fake
device end to end in demo mode and on the local gpt-oss:20b model; the firmware compiles for the ESP32-C3 and
renders every expression on the host. **Nothing has run on the real board
yet**: A1 is off the breadboard until the brass harness exists.

## The character

Eleven emotions, six states, one gesture, eyes only. Open the live preview
(`eyes/preview.html`, also published as the "Pip Eyes" artifact) to click
through them. The device runs the same model, `firmware/main/eyes.c`.

| Emotions | neutral · happy · excited · sad · surprised · confused · thinking · sleepy · angry · love · sarcastic |
| **Gesture** | the eye roll: a sweep up and over with half-closed lids, then a blink. Automatic on `sarcastic` (full) and `confused` (half); the server can also send `{"type":"gesture","gesture":"roll"}` |
| --- | --- |
| **States** | boot (eyes open slowly) · idle (blinks, glances, sleepy after 90 s) · listening (bigger, bobs with your voice) · thinking (looks up and away) · speaking (bounces with its voice) · error (confused, shakes) |

The brain starts every reply with a tag such as `[happy]`; the server strips
it and sends it to the device before the first audio frame, so the face
changes as Pip starts to speak.

## Run the server

```bash
cd pocket_ai_assistant/character/server
# the full local stack lives in .venv-speech (Python 3.12: Whisper and Kokoro wheels need it)
uv venv .venv-speech --python 3.12
uv pip install --python .venv-speech/bin/python torch --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv-speech/bin/python -e . faster-whisper kokoro soundfile \
  "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"

# 0. everything local: Whisper ears, gpt-oss brain, Kokoro voice (no key, no cloud)
POCKET_BRAIN=ollama .venv-speech/bin/python -m pocket_server

# 1. no key, no models: demo brain, robot-beep voice
.venv-speech/bin/python -m pocket_server --demo

# 2. OpenAI for brain, ears and voice (key stays on this computer)
export OPENAI_API_KEY=sk-...
POCKET_BRAIN=openai .venv-speech/bin/python -m pocket_server

# 3. local brain, OpenAI ears and voice
POCKET_BRAIN=ollama POCKET_STT=openai POCKET_TTS=openai .venv-speech/bin/python -m pocket_server
```

### The local model

Installed on 8 October 2026 (no root needed): Ollama 0.40.1 in `~/.local/ollama`,
running as a user service (`systemctl --user status ollama`), serving
**gpt-oss:20b**, OpenAI's open-weight model under the Apache 2.0 licence
(21 B parameters, 3.6 B active, 13 GB on disk). On this computer's RTX 5000
Ada it loads fully on the GPU and answers a one-sentence turn in about 0.5 s
once warm. It is a reasoning model, so the server sends
`reasoning_effort=low` (`POCKET_REASONING_EFFORT`); without it the model
spends its whole token budget thinking and says nothing.

```bash
~/.local/ollama/bin/ollama list                 # what is installed
~/.local/ollama/bin/ollama pull qwen3:8b        # an alternative, Apache 2.0, 5 GB
POCKET_BRAIN=ollama POCKET_OLLAMA_MODEL=qwen3:8b .venv/bin/python -m pocket_server
```

Other models worth trying, all run by the same command with a different
`POCKET_OLLAMA_MODEL`: `qwen3:30b-a3b` (Apache 2.0, mixture of experts, fast
even on the CPU), `gemma3:12b` and `llama3.3` (open weights under Google's and
Meta's own licences, not Apache). 

### Local ears and voice

With `.venv-speech`, speech never leaves the computer either:

| Job | Model | Licence | Size | Speed here (CPU) |
| --- | --- | --- | --- | --- |
| ears (STT) | Whisper `small.en` via faster-whisper | MIT | 460 MB | a 4 s question in 1.1 s |
| voice (TTS) | Kokoro-82M, voice `af_heart` | Apache 2.0 | 330 MB | a sentence in well under a second |

`POCKET_STT=auto` and `POCKET_TTS=auto` pick them whenever the packages are
importable, so `POCKET_BRAIN=ollama` alone gives the all-local loop. Options:
`POCKET_STT_LOCAL_MODEL` (`base.en` is faster, `large-v3-turbo` more accurate),
`POCKET_TTS_LOCAL_VOICE` (`af_heart`, `af_bella`, `am_michael`, …),
`POCKET_LOCAL_DEVICE=cuda` to put Whisper on the GPU (needs the cuDNN and
cuBLAS pip packages). Verified 8 October 2026: a Kokoro-spoken question went
through Whisper, gpt-oss and Kokoro and came back as an 11.5 s reply that
Whisper transcribed word for word.

Defaults: `127.0.0.1:8790`, character name `Pip`, chat model
`gpt-4.1-mini`, transcription `gpt-4o-mini-transcribe`, voice
`gpt-4o-mini-tts` / `coral`. Every one is an environment variable; see
`server/pocket_server/config.py`. `POCKET_PERSONA` replaces the first
paragraph of the system prompt.

For the device, bind the LAN and set a token; the firmware sends it in `hello`:

```bash
POCKET_HOST=0.0.0.0 POCKET_TOKEN="$(openssl rand -hex 24)" POCKET_BRAIN=openai \
  .venv/bin/python -m pocket_server
```

`ws://` is unencrypted. Trusted home Wi-Fi only; never port-forward 8790.
Hosting it elsewhere later means `wss://` and a real certificate; the device
code only needs the URL changed.

### Test without the device

```bash
.venv-speech/bin/python ../tools/fake_device.py --text "Hi! What is your name?" --play
.venv-speech/bin/python ../tools/fake_device.py --record 4 --play     # speak into the computer's mic
.venv-speech/bin/python -m unittest discover -s tests -v
```

## Build and flash the firmware

```bash
cd pocket_ai_assistant/character/firmware
source ../../firmware/.work/esp-idf/export.sh          # ESP-IDF 6.0.2, already installed
printf 'CONFIG_POCKET_WIFI_SSID="Jw-wifi"\nCONFIG_POCKET_WIFI_PASSWORD="..."\nCONFIG_POCKET_SERVER_URL="ws://192.168.1.171:8790/ws"\nCONFIG_POCKET_TOKEN="..."\n' > sdkconfig.secrets
SDKCONFIG_DEFAULTS="sdkconfig.defaults;sdkconfig.secrets" idf.py set-target esp32c3
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

`sdkconfig.secrets` is ignored by git. `idf.py menuconfig` → "Pocket
character" holds every option: Wi-Fi, server URL and token, the amplifier
switch, the volume cap, the transmit-power cap, the microphone gain.

What the firmware does, in order: NVS, OLED probe at 0x3C then 0x3D
(headless if absent), I²S duplex at 16 kHz with the amplifier held in shutdown,
button, Wi-Fi with the 8.5 dBm cap applied after every radio start, then the
WebSocket. Hold the button to talk; release to send. Press during a reply to
interrupt it.

### Safety carried over from the Step 11 build

- **The amplifier is off by default.** `CONFIG_POCKET_ENABLE_AMPLIFIER=y` is
  needed to drive GPIO5, and then only while speaking, after the clocks have
  run with zeros for `POCKET_AMP_STARTUP_DELAY_MS` (100 ms). Everything else
  works with it off: eyes, listening, the whole conversation, just no sound.
- **Volume cap 65, squared** (42 % of full scale). Builder decision 2026-10-26,
  on the basis that the amplifier's GAIN pin is left open (9 dB): full scale is
  then 5.43 V peak and cap 65 gives 2.29 V peak against the speaker's 2.53 V,
  2.06 V measured on normalised speech. The Kconfig range and the runtime hook
  both stop at 65. The cap can be changed at runtime by the server's volume hook.
- The firmware logs the worst-case speaker peak every two seconds while
  playing, like the Step 11 build.
- USB is the only power source; both USB ports are never connected together;
  GPIO9 stays the ROM button. Same hardware contract as `CLAUDE.md`.

### Wokwi

`firmware/wokwi/` holds a diagram (ESP32-C3 DevKitM stand-in, SSD1306 at
0x3D, button) and a `wokwi.toml` pointing at the merged image. Start it from
VS Code's Wokwi extension to see the eyes without hardware. Build with
`CONFIG_POCKET_WIFI_SSID="Wokwi-GUEST"` and an empty password for simulated
Wi-Fi. The Wokwi MCP bridge could not start a simulation from this session.

## Protocol

`PROTOCOL.md`. Version 1, JSON control plus raw PCM, 40 ms frames, server
paced at most 320 ms ahead of real time so the device's 0.8 s buffer is plenty.
`codec` in `hello` is the seam for Opus if the server ever leaves the LAN.

## Layout

```text
character/
├── PROTOCOL.md
├── README.md
├── eyes/preview.html          the character, live, in a browser
├── server/                    pocket_server package, tests, pyproject
├── tools/fake_device.py       the device, pretended by your computer
└── firmware/                  ESP-IDF project: main/, host/ (render sheet), wokwi/
```

## Not done yet

- Hardware bring-up: flash A1 once the harness exists; measure the real
  microphone gain (`POCKET_MIC_SHIFT`); confirm the amplifier start sequence on
  the speaker; Wi-Fi inside the brass frame.
- Wi-Fi provisioning without a rebuild (a setup hotspot or BLE), so the
  credentials stop living in `sdkconfig.secrets`.
- Opus over the WebSocket and `wss://` for the cloud-hosted server.
- A wake word, if push-to-talk ever gets old.
