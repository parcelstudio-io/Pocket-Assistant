# Pip: alternative local-first Pocket AI stack

This folder is an isolated, review-only alternative to the current Pocket AI
hardware and firmware. Nothing here replaces or modifies the existing stack.

The proposal uses an **M5Stack CoreS3-SE** as a small touch, microphone, and
speaker client. A Python gateway on your computer streams answers from a model
you host with Ollama, llama.cpp, or another OpenAI-compatible local server.

```text
┌─────────────────────────────┐       private LAN       ┌─────────────────────┐
│ Pip client                  │  POST /api/chat + SSE  │ Your computer       │
│                             │ ──────────────────────> │                     │
│ • browser prototype        │ <────────────────────── │ Pocket gateway      │
│ • later: CoreS3-SE device  │    streamed text       │        ↓            │
└─────────────────────────────┘                         │ local model runtime │
                                                       └─────────────────────┘
```

## What works now

| Piece | Current status |
| --- | --- |
| Cute Pip browser UI | Runnable; responsive desktop and true 320 × 240 layouts |
| Built-in demo | Runnable without a model or network |
| Local-model gateway | Runnable; Ollama/llama.cpp streaming, loopback default, token-required LAN mode |
| CoreS3-SE firmware | Review scaffold: face UI, touch, half-duplex audio ownership, and streamed text request |
| End-to-end physical voice | Not implemented yet; local STT, PCM transport, and local TTS are the next milestone |
| Physical hardware | Not purchased, flashed, or electrically tested |

The browser microphone is an optional convenience. Browser speech recognition
is not guaranteed to be local, so typed chat is the honest offline-model test.
The demo and a mocked compatible upstream have been tested in this workspace;
Ollama is not installed here, so no claim is made that a real model run was
validated on this computer.

## Run the prototype now (no model required)

From the repository root:

```bash
./alternative_hardware_stack/run_demo.sh
```

Open <http://127.0.0.1:8787>. The UI starts with its built-in demo brain, so
you can type immediately and inspect all of Pip's interaction states.

To exercise the Python gateway and SSE stream as well:

1. Select the **Demo** chip at the top-right.
2. Choose **Local model server**.
3. Leave the endpoint as `/api/chat`.
4. Select **Check gateway**, then **Save settings**.

The gateway is also in deterministic demo mode, so this path still needs no
download. Stop it with `Ctrl+C`.

## Run it with your own local model

Install [Ollama](https://docs.ollama.com/quickstart), then in one terminal:

```bash
ollama pull llama3.2:3b
ollama serve
```

If the Ollama desktop application is already serving on port `11434`, do not
start a second copy. In another terminal, from the repository root:

```bash
python3 alternative_hardware_stack/server/server.py
```

Open <http://127.0.0.1:8787> and select **Local model server** in Pip's Brain
settings as described above. The default model is `llama3.2:3b`. To select a
different model already installed in Ollama:

```bash
POCKET_AI_MODEL=qwen2.5:3b \
  python3 alternative_hardware_stack/server/server.py
```

See [server/README.md](server/README.md) for llama.cpp, compatible servers,
configuration, and tests.

## Review the hardware alternative

Start with [HARDWARE.md](HARDWARE.md). The proposed CoreS3-SE integrates the
320 × 240 touch display, dual microphones, codec, amplifier, 1 W speaker,
ESP32-S3, and Wi-Fi in one USB-C unit. The language model still runs on your
computer; it does not fit on the ESP32-S3.

The review firmware lives only in [device/](device/). With PlatformIO available
through `uv`, compile it without credentials or hardware:

```bash
cd alternative_hardware_stack/device
uvx --from platformio==6.2.0 pio run
```

Do not order hardware from this prototype alone. The staged acceptance gates
in `HARDWARE.md` deliberately put browser and local-model checks before a
purchase decision.

## When a physical device needs the server

Loopback (`127.0.0.1`) is safest for browser-only review. A CoreS3-SE needs the
computer's private-LAN IP, an explicit LAN bind, and a matching long random
token. For example:

```bash
POCKET_AI_HOST=0.0.0.0 \
POCKET_AI_TOKEN='replace-with-a-long-random-value' \
  python3 alternative_hardware_stack/server/server.py
```

Copy `device/include/device_config.example.h` to the ignored
`device/include/device_config.h`, then enter the computer's private-LAN URL and
the same token. Use a trusted network only. This HTTP prototype is not
encrypted; never port-forward port `8787` or expose it to the Internet.

## Folder map

- `HARDWARE.md` — board choice, internal buses, BOM boundary, and review gates
- `PROTOCOL.md` — text API, state machine, limits, and future local voice seam
- `ui/` — dependency-free Pip browser UI
- `server/` — standard-library Python gateway and tests
- `device/` — isolated PlatformIO CoreS3-SE firmware scaffold
- `run_demo.sh` — one-command model-free preview
