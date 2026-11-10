# Pip browser UI

`ui/` is a zero-build, dependency-free prototype of the alternate pocket
assistant interface. It works at phone size, streams replies from the local
server, and has a built-in demo brain for reviewing the interaction without a
model or network connection.

The layout uses the selected M5Stack CoreS3-SE's real **320×240 landscape,
4:3** display geometry. A larger desktop browser scales the same two-column
layout up for comfortable review. Resize a browser viewport to exactly 320×240
to inspect the physical-device view.

## Fastest preview (demo mode)

From the repository root:

```bash
python3 -m http.server 5173 --directory alternative_hardware_stack/ui
```

Open <http://127.0.0.1:5173>. The UI begins in **Built-in demo** mode, so it is
ready immediately. Use `Ctrl+C` in the terminal to stop the preview server.

Using a local HTTP server is preferable to double-clicking `index.html`:
browser microphone features generally require a secure context, and browsers
treat `localhost` as secure for development.

## Use the included local-model server

When the alternate stack's server is running, open its address (by default
<http://127.0.0.1:8787>). It serves this folder itself, so there is no second UI
command to run.

In Pip:

1. Select the **Demo** connection chip in the top-right.
2. Change **Connection mode** to **Local model server**.
3. Keep the endpoint as `/api/chat`.
4. Select **Check gateway**, then **Save settings**.

The gateway check calls only `GET /api/health`. A success means the gateway
process is reachable; it does **not** verify the model connection or the access
token. Sending a chat message exercises those separately.

If the server was started with `POCKET_AI_TOKEN`, enter that value in **Access
token**. Pip sends it as `Authorization: Bearer <token>`, keeps it in memory
only, and never writes it to browser storage. Re-enter it after every reload.

If the UI is served separately on port 5173, enter the absolute endpoint
`http://127.0.0.1:8787/api/chat`. The model server must allow the UI origin with
CORS in that arrangement.

## Server contract

The default request is:

```http
POST /api/chat
Content-Type: application/json
Accept: text/event-stream, application/x-ndjson, application/json

{
  "message": "Hello Pip",
  "history": [
    {"role": "user", "content": "Earlier question"},
    {"role": "assistant", "content": "Earlier answer"}
  ]
}
```

Streaming responses use OpenAI-style server-sent events:

```text
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: {"choices":[{"delta":{"content":" there!"}}]}

data: [DONE]
```

Before every request, Pip keeps only the newest complete user/assistant turns:
at most **38 messages** and at most **56 KiB of UTF-8 message content**. Older
turns are dropped. Pip never splits a turn, includes an unanswered user message,
or truncates an individual message; if the newest complete turn alone exceeds
the byte budget, no history is sent with the new message.

The parser also accepts NDJSON with `token`, `content`, `response`, or
`message.content`, and a non-streaming JSON response. Connection testing calls
`GET /api/health`.

## Browser features and privacy

- Typed chat works in all current browsers.
- Speech output uses the browser's `speechSynthesis` API and can be disabled in
  Brain settings.
- Voice input uses `SpeechRecognition` when the browser provides it. Support is
  browser-dependent and some implementations may use a browser-vendor speech
  service; it is not guaranteed to stay local. The mic button disables itself
  when the API is unavailable.
- Demo-mode messages never leave the tab. Server-mode messages are sent only to
  the configured chat endpoint. Conversations are held in memory and disappear
  on refresh; only connection preferences are saved in local storage.

## Files

- `index.html` — semantic UI, settings dialog, and message template
- `styles.css` — responsive device shell and idle/listening/thinking/speaking/error animations
- `app.js` — state machine, chat streaming, demo replies, speech, and settings
- `history-policy.js` — pure complete-turn history bounding used by the gateway request
- `favicon.svg` — local Pip face icon (no external asset requests)
