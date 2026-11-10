# Pocket character protocol, version 1

One WebSocket between the device and the server. JSON text frames carry
control; binary frames carry audio. The device never sees an API key: the
server owns every upstream credential.

```text
A1 (ESP32-C3)                              Pocket server (your computer)
  │  ── ws://host:8790/ws ──────────────────►  │
  │  {"type":"hello", ...}                     │
  │  ◄──────────── {"type":"hello","ok":true}  │
  │                                            │
  │  button down: {"type":"listen","action":"start"}
  │  ── binary PCM frames (16 kHz, 16-bit, mono, 40 ms = 1280 bytes) ──►
  │  button up:   {"type":"listen","action":"stop"}
  │                                            │  STT → brain → TTS
  │  ◄── {"type":"state","state":"thinking"}   │
  │  ◄── {"type":"transcript","role":"user","text":"..."}
  │  ◄── {"type":"emotion","emotion":"happy"}  │
  │  ◄── {"type":"state","state":"speaking"}   │
  │  ◄── {"type":"audio","action":"start","rate":16000}
  │  ◄── binary PCM frames, paced at real time │
  │  ◄── {"type":"transcript","role":"assistant","text":"..."}
  │      (as soon as the brain finishes, usually mid-speech)
  │  ◄── {"type":"audio","action":"end"}       │
  │  ◄── {"type":"state","state":"idle"}       │
```

## Audio

Both directions: 16 000 Hz, signed 16-bit little-endian, mono, raw PCM.
One binary frame is 40 ms, 640 samples, 1280 bytes. The server paces its
frames at real time with a lead of at most 8 frames (320 ms), so the device
needs about half a second of buffer and no more.

The `hello` carries `"audio": {"rate": 16000, "bits": 16, "channels": 1,
"frame_ms": 40, "codec": "pcm"}`. `codec` is the seam for Opus later; a
server that cannot honour the request answers `hello` with `"ok": false`.

## Device → server

| Message | Meaning |
| --- | --- |
| `{"type":"hello","device":"<id>","version":1,"token":"<optional>","audio":{…}}` | first frame on every connection |
| `{"type":"listen","action":"start"}` | the button went down; PCM frames follow |
| `{"type":"listen","action":"stop"}` | the button came up; take a turn |
| `{"type":"text","text":"…"}` | a typed turn (test tools, no audio) |
| `{"type":"abort"}` | stop speaking now |
| `{"type":"ping"}` | keep-alive; the server answers `pong` |

## Server → device

| Message | Meaning |
| --- | --- |
| `{"type":"hello","ok":true,"server":"pocket-character","name":"<character>","session":"<id>"}` | accepted |
| `{"type":"hello","ok":false,"error":"…"}` | refused (bad token, bad audio format); the server then closes |
| `{"type":"state","state":"idle"\|"listening"\|"thinking"\|"speaking"\|"error","message":"…"}` | drives the face |
| `{"type":"emotion","emotion":"…"}` | one of the fixed set below |
| `{"type":"gesture","gesture":"roll"\|"blink","amount":0–1}` | a one-off movement on top of the emotion |
| `{"type":"transcript","role":"user"\|"assistant","text":"…"}` | for the log and any text display; the assistant's is sent as soon as the reply is complete, not after it has been spoken |
| `{"type":"audio","action":"start","rate":16000}` | PCM frames follow |
| `{"type":"audio","action":"end"}` | last frame sent |
| `{"type":"error","message":"…"}` | recoverable; the device shows it briefly and returns to idle |
| `{"type":"pong"}` | |

## Emotions

`neutral`, `happy`, `excited`, `sad`, `surprised`, `confused`, `thinking`,
`sleepy`, `angry`, `love`, `sarcastic`. Entering `sarcastic` rolls the eyes on
the device by itself; entering `confused` does a smaller roll. A `gesture`
message triggers one explicitly (a device that sends `{"type":"gesture",…}`
gets it echoed back, which is how test tools drive it). The brain is asked to begin every reply with one tag
such as `[happy]`; the server strips it, sends it as an `emotion` message, and
falls back to `neutral` when a reply has no tag. The device keeps the last
emotion through `speaking` and relaxes to `neutral` a few seconds into `idle`.

## States and the face

```text
idle ──button down──► listening ──button up──► thinking ──first audio──► speaking ──audio end──► idle
  ▲                                                                                   │
  └──────────────────────────── abort, error, or connection loss ─────────────────────┘
```

`listening` and `speaking` never overlap: the microphone is read only while
listening and the amplifier is enabled only while speaking.

## Limits

- recording: 20 seconds maximum per turn (the server stops listening and takes the turn)
- text turn: 2 000 characters
- history kept per session: 20 turns
- a `hello` must arrive within 5 seconds of connecting
