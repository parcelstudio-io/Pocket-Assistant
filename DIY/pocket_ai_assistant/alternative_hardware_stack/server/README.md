# Local AI server

This zero-dependency Python server does two jobs:

1. serves the prototype UI from `../ui`; and
2. streams chat from an OpenAI-compatible local endpoint such as Ollama or
   llama.cpp without exposing backend credentials to the browser.

Python 3.11 or newer is recommended. It binds to loopback by default, so it is
not exposed to other computers.

## Fastest prototype (no model installed)

From the repository root:

```sh
python3 alternative_hardware_stack/server/server.py --demo
```

Open <http://127.0.0.1:8787>. Demo mode sends deterministic pretend replies so
the UI, streaming path, and conversation state can be reviewed first.

## Use Ollama

Start Ollama and install a model in another terminal. The default server model
name is `llama3.2:3b`:

```sh
ollama pull llama3.2:3b
ollama serve
```

Then start Pocket:

```sh
python3 alternative_hardware_stack/server/server.py
```

To use a different installed model:

```sh
POCKET_AI_MODEL=qwen2.5:3b \
  python3 alternative_hardware_stack/server/server.py
```

The default backend root is `http://127.0.0.1:11434`; the server automatically
uses its OpenAI-compatible `/v1/chat/completions` endpoint.

## Use llama.cpp or another compatible server

Start `llama-server` on a port other than Pocket's `8787`, then point Pocket at
its `/v1` base. The model value must match what that server expects.

```sh
POCKET_AI_BACKEND=llamacpp \
POCKET_AI_BASE_URL=http://127.0.0.1:8080/v1 \
POCKET_AI_MODEL=local-model \
  python3 alternative_hardware_stack/server/server.py
```

For a backend that requires a bearer token, set `POCKET_AI_API_KEY`. It remains
server-side and is intentionally omitted from `/api/config`.

## Browser API

- `GET /api/health` — server/backend selection and model name
- `GET /api/config` — non-secret UI configuration
- `POST /api/chat` — `{ "message": "Hi", "history": [...] }`
- `POST /v1/chat/completions` — OpenAI-compatible chat request

Both POST endpoints default to an OpenAI-style SSE stream. Each content chunk
is under `choices[0].delta.content`; the stream ends with `data: [DONE]`.
The `/v1` endpoint also supports `"stream": false`.

Useful environment variables:

| Variable | Default |
| --- | --- |
| `POCKET_AI_BACKEND` | `ollama` (`demo`, `llamacpp`, and `openai` also work) |
| `POCKET_AI_BASE_URL` | `http://127.0.0.1:11434` |
| `POCKET_AI_MODEL` | `llama3.2:3b` |
| `POCKET_AI_HOST` / `POCKET_AI_PORT` | `127.0.0.1` / `8787` |
| `POCKET_AI_SYSTEM_PROMPT` | short built-in Pocket persona |
| `POCKET_AI_TOKEN` | empty; optional Bearer token for both chat POST routes |
| `POCKET_AI_CORS_ORIGIN` | empty (same-origin UI needs no CORS permission) |
| `POCKET_AI_TIMEOUT` | `120` seconds |

Only bind to `0.0.0.0` on a trusted LAN. A long token is required whenever the
listen address is not loopback; startup fails closed without one. The client
sends it as `Authorization: Bearer <token>`:

```sh
POCKET_AI_HOST=0.0.0.0 \
POCKET_AI_TOKEN='replace-with-a-long-random-value' \
  python3 alternative_hardware_stack/server/server.py
```

The token adds a basic access boundary but not TLS. Do not port-forward this
review prototype or run it on an untrusted network.

## Tests

The tests use an injected fake backend and a mocked OpenAI-compatible stream;
they never download or contact a model:

```sh
python3 -m unittest discover \
  -s alternative_hardware_stack/server/tests -v
```
