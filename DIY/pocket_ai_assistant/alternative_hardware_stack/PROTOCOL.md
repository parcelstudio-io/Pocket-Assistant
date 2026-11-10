# Pocket local protocol

This protocol keeps the model provider on the host. Neither the browser UI nor
the eventual CoreS3-SE firmware chooses an arbitrary upstream URL or receives
backend credentials.

## Text MVP

```text
browser or CoreS3-SE        Pocket gateway                 local model
        | POST /api/chat          |                            |
        |------------------------>| POST /v1/chat/completions  |
        |                         |--------------------------->|
        |     SSE text deltas     |       SSE text deltas      |
        |<------------------------|<---------------------------|
```

The default gateway is `http://127.0.0.1:8787`. It binds only to loopback until
the operator explicitly selects a LAN address.

### Discover configuration

`GET /api/health` returns operational status:

```json
{
  "status": "ok",
  "assistant": "Pocket",
  "backend": "demo",
  "model": "llama3.2:3b",
  "streaming": true,
  "auth_required": false
}
```

`GET /api/config` returns the public UI configuration. It never includes the
backend API key or access token.

### Send a turn

`POST /api/chat` is the small client-facing API:

```json
{
  "message": "Explain voltage in one sentence.",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"}
  ]
}
```

History may contain only `user` and `assistant` messages. The gateway supplies
the system prompt and configured model. This prevents a client from changing
the host's backend address.

The response is an OpenAI-compatible server-sent event stream:

```text
data: {"choices":[{"delta":{"content":"Voltage "},"finish_reason":null}]}

data: {"choices":[{"delta":{"content":"is..."},"finish_reason":null}]}

data: {"choices":[{"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

The gateway also exposes `POST /v1/chat/completions` for test tools and clients
that already speak the OpenAI chat-completions format. The pocket device should
prefer `/api/chat`, because it has a smaller request surface.

## Authentication

The token may be omitted for the default loopback-only preview. A non-loopback
listen address requires `POCKET_AI_TOKEN`; when set, both chat POST routes
require:

```text
Authorization: Bearer <token>
```

Health, public configuration, and static UI assets remain readable. The token
is a basic trusted-LAN boundary, not encryption. Never port-forward this server
or expose it to an untrusted network. The gateway refuses to bind to a
non-loopback address unless this token is configured.

## UI state machine

The client owns the visible state and uses these transitions:

```text
                         +---------+
                 +------>|  error  |------+
                 |       +---------+      |
                 |                        v
+------+     +-----------+     +----------+     +----------+
| idle |---->| listening |---->| thinking |---->| speaking |
+------+     +-----------+     +----------+     +----------+
   ^                                                |
   +------------------------------------------------+
```

- `idle`: ready for touch, typed input, or push-to-talk.
- `listening`: microphone owns the audio peripheral.
- `thinking`: microphone is stopped; request/stream is in progress.
- `speaking`: speaker owns the audio peripheral.
- `error`: show a short recoverable message, then return to idle.

For the CoreS3-SE MVP, `listening` and `speaking` must never overlap.

## Limits implemented by the gateway

- request body: 256 KiB maximum
- conversation: 40 messages maximum
- combined message text: 64 KiB maximum
- generated token request: 1–4096
- temperature: 0–2
- upstream timeout: 120 seconds by default

These are resource and misuse bounds, not a claim that every local model has a
4096-token context window.

## Future local voice extension

The current runnable prototype proves the UI and local **text-model** boundary.
Browser speech synthesis and recognition are optional conveniences and may use
operating-system or browser services.

A fully controlled local voice revision should add a separate WebSocket or
streaming HTTP contract:

1. device uploads framed 16 kHz mono PCM while in `listening`;
2. host-side local STT produces the user text;
3. the existing chat endpoint talks to Ollama/llama.cpp;
4. host-side local TTS returns framed PCM;
5. only after microphone shutdown does the device enter `speaking` and play it.

STT/TTS engine selection and audio framing are deliberately left out of the
text MVP so the first prototype is runnable, observable, and testable without
pretending that browser voice APIs are offline.
