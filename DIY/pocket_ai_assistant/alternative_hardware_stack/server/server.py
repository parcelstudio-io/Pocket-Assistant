#!/usr/bin/env python3
"""Small local-model gateway for the alternative Pocket AI prototype.

The browser talks to this process instead of talking directly to Ollama or
llama.cpp.  Keeping that boundary on the host means a backend token never has
to be stored in the browser or on the pocket device.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import hmac
from ipaddress import ip_address
import json
import os
from pathlib import Path
import re
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import time
from typing import Iterable, Iterator, Mapping, Protocol, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen
from uuid import uuid4


MAX_REQUEST_BYTES = 256 * 1024
MAX_MESSAGES = 40
MAX_CONTENT_CHARS = 64 * 1024
DEFAULT_SYSTEM_PROMPT = (
    "You are Pocket, a cheerful local pocket assistant. Be warm, practical, "
    "and concise. Use plain language unless the user asks for technical detail."
)


def _is_loopback_host(host: str) -> bool:
    """Return whether a listen address is restricted to this computer."""

    candidate = host.strip().strip("[]")
    if candidate.lower() == "localhost":
        return True
    try:
        return ip_address(candidate).is_loopback
    except ValueError:
        return False


class RequestError(ValueError):
    """The browser supplied an invalid request."""


class BackendError(RuntimeError):
    """The configured local model backend could not answer."""


def _env_int(env: Mapping[str, str], name: str, default: int) -> int:
    raw = env.get(name, str(default))
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _env_float(env: Mapping[str, str], name: str, default: float) -> float:
    raw = env.get(name, str(default))
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8787
    backend: str = "ollama"
    base_url: str = "http://127.0.0.1:11434"
    model: str = "llama3.2:3b"
    api_key: str = ""
    request_timeout: float = 120.0
    cors_origin: str = ""
    access_token: str = ""
    assistant_name: str = "Pocket"
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    ui_dir: Path = Path(__file__).resolve().parent.parent / "ui"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        values = os.environ if env is None else env
        default_ui = Path(__file__).resolve().parent.parent / "ui"
        settings = cls(
            host=values.get("POCKET_AI_HOST", "127.0.0.1"),
            port=_env_int(values, "POCKET_AI_PORT", 8787),
            backend=values.get("POCKET_AI_BACKEND", "ollama").strip().lower(),
            base_url=values.get(
                "POCKET_AI_BASE_URL", "http://127.0.0.1:11434"
            ).strip(),
            model=values.get("POCKET_AI_MODEL", "llama3.2:3b").strip(),
            api_key=values.get("POCKET_AI_API_KEY", "").strip(),
            request_timeout=_env_float(values, "POCKET_AI_TIMEOUT", 120.0),
            cors_origin=values.get("POCKET_AI_CORS_ORIGIN", "").strip(),
            access_token=values.get("POCKET_AI_TOKEN", "").strip(),
            assistant_name=values.get("POCKET_AI_NAME", "Pocket").strip(),
            system_prompt=values.get(
                "POCKET_AI_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT
            ).strip(),
            ui_dir=Path(values.get("POCKET_AI_UI_DIR", str(default_ui))).expanduser(),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if not self.host:
            raise ValueError("POCKET_AI_HOST cannot be empty")
        if not 0 <= self.port <= 65535:
            raise ValueError("POCKET_AI_PORT must be between 0 and 65535")
        if self.backend not in {"demo", "ollama", "llamacpp", "openai"}:
            raise ValueError(
                "POCKET_AI_BACKEND must be demo, ollama, llamacpp, or openai"
            )
        if self.backend != "demo" and not self.base_url:
            raise ValueError("POCKET_AI_BASE_URL cannot be empty")
        if not self.model:
            raise ValueError("POCKET_AI_MODEL cannot be empty")
        if self.request_timeout <= 0:
            raise ValueError("POCKET_AI_TIMEOUT must be greater than zero")
        if not self.assistant_name:
            raise ValueError("POCKET_AI_NAME cannot be empty")
        if not self.system_prompt:
            raise ValueError("POCKET_AI_SYSTEM_PROMPT cannot be empty")
        if not _is_loopback_host(self.host) and not self.access_token:
            raise ValueError(
                "POCKET_AI_TOKEN is required when POCKET_AI_HOST is not a "
                "loopback address"
            )


class ChatBackend(Protocol):
    def stream(
        self,
        messages: Sequence[dict[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Iterator[str]: ...


def chat_completions_url(base_url: str) -> str:
    """Turn a server root, a /v1 base, or a full endpoint into an endpoint."""

    parsed = urlsplit(base_url.rstrip("/"))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("POCKET_AI_BASE_URL must be an http(s) URL")
    path = parsed.path.rstrip("/")
    if path.endswith("/chat/completions"):
        endpoint_path = path
    elif path.endswith("/v1"):
        endpoint_path = f"{path}/chat/completions"
    else:
        endpoint_path = f"{path}/v1/chat/completions"
    return urlunsplit(
        (parsed.scheme, parsed.netloc, endpoint_path, parsed.query, "")
    )


def _text_from_chunk(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return ""
    choice = choices[0]
    delta = choice.get("delta")
    if isinstance(delta, dict) and isinstance(delta.get("content"), str):
        return delta["content"]
    message = choice.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), str):
        return message["content"]
    if isinstance(choice.get("text"), str):
        return choice["text"]
    return ""


class OpenAICompatibleBackend:
    """Adapter for the OpenAI-compatible APIs in Ollama and llama.cpp."""

    def __init__(self, base_url: str, api_key: str = "", timeout: float = 120.0):
        self.endpoint = chat_completions_url(base_url)
        self.api_key = api_key
        self.timeout = timeout

    def stream(
        self,
        messages: Sequence[dict[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Iterator[str]:
        body = json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(self.endpoint, data=body, headers=headers, method="POST")

        try:
            with urlopen(request, timeout=self.timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    payload = json.loads(response.read().decode("utf-8"))
                    text = _text_from_chunk(payload)
                    if text:
                        yield text
                    return

                for raw_line in response:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line or line.startswith(":") or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        return
                    try:
                        payload = json.loads(data)
                    except json.JSONDecodeError as exc:
                        raise BackendError("local backend returned invalid SSE JSON") from exc
                    text = _text_from_chunk(payload)
                    if text:
                        yield text
        except HTTPError as exc:
            detail = exc.read(1024).decode("utf-8", errors="replace").strip()
            suffix = f": {detail}" if detail else ""
            raise BackendError(f"local backend returned HTTP {exc.code}{suffix}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise BackendError(
                "cannot reach the local model backend; start Ollama/llama.cpp "
                "or run with POCKET_AI_BACKEND=demo"
            ) from exc
        except json.JSONDecodeError as exc:
            raise BackendError("local backend returned invalid JSON") from exc


class DemoBackend:
    """Deterministic, model-free backend for exercising the complete UI path."""

    def stream(
        self,
        messages: Sequence[dict[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Iterator[str]:
        del model, temperature, max_tokens
        user_text = next(
            (item["content"] for item in reversed(messages) if item["role"] == "user"),
            "hello",
        )
        clipped = user_text[:240]
        reply = (
            "Beep boop! Local demo mode is working. "
            f"You said: “{clipped}” Connect Ollama or llama.cpp when you want real answers."
        )
        yield from re.findall(r"\S+\s*", reply)


def _validate_messages(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise RequestError("messages must be a non-empty array")
    if len(value) > MAX_MESSAGES:
        raise RequestError(f"messages cannot contain more than {MAX_MESSAGES} items")
    result: list[dict[str, str]] = []
    total = 0
    for item in value:
        if not isinstance(item, dict):
            raise RequestError("each message must be an object")
        role = item.get("role")
        content = item.get("content")
        if role not in {"system", "user", "assistant"}:
            raise RequestError("message role must be system, user, or assistant")
        if not isinstance(content, str) or not content.strip():
            raise RequestError("message content must be a non-empty string")
        total += len(content)
        if total > MAX_CONTENT_CHARS:
            raise RequestError("message content is too large")
        result.append({"role": role, "content": content})
    return result


def _number(value: object, name: str, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RequestError(f"{name} must be a number")
    return float(value)


def _integer(value: object, name: str, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int):
        raise RequestError(f"{name} must be an integer")
    return value


def _openai_request(
    payload: object, settings: Settings
) -> tuple[list[dict[str, str]], str, float, int, bool]:
    if not isinstance(payload, dict):
        raise RequestError("JSON body must be an object")
    messages = _validate_messages(payload.get("messages"))
    model = payload.get("model", settings.model)
    if not isinstance(model, str) or not model.strip() or len(model) > 200:
        raise RequestError("model must be a short non-empty string")
    temperature = _number(payload.get("temperature"), "temperature", 0.7)
    if not 0 <= temperature <= 2:
        raise RequestError("temperature must be between 0 and 2")
    max_tokens = _integer(payload.get("max_tokens"), "max_tokens", 512)
    if not 1 <= max_tokens <= 4096:
        raise RequestError("max_tokens must be between 1 and 4096")
    stream = payload.get("stream", True)
    if not isinstance(stream, bool):
        raise RequestError("stream must be true or false")
    return messages, model.strip(), temperature, max_tokens, stream


def _friendly_request(
    payload: object, settings: Settings
) -> tuple[list[dict[str, str]], str, float, int, bool]:
    if not isinstance(payload, dict):
        raise RequestError("JSON body must be an object")
    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        raise RequestError("message must be a non-empty string")
    history_value = payload.get("history", [])
    if not isinstance(history_value, list):
        raise RequestError("history must be an array")
    history: list[dict[str, str]] = []
    for item in history_value:
        if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"}:
            raise RequestError("history roles must be user or assistant")
        history.append(item)
    messages = _validate_messages(
        [
            {"role": "system", "content": settings.system_prompt},
            *history,
            {"role": "user", "content": message},
        ]
    )
    temperature = _number(payload.get("temperature"), "temperature", 0.7)
    if not 0 <= temperature <= 2:
        raise RequestError("temperature must be between 0 and 2")
    max_tokens = _integer(payload.get("max_tokens"), "max_tokens", 512)
    if not 1 <= max_tokens <= 4096:
        raise RequestError("max_tokens must be between 1 and 4096")
    return messages, settings.model, temperature, max_tokens, True


class PocketRequestHandler(SimpleHTTPRequestHandler):
    settings: Settings
    backend_impl: ChatBackend
    ui_root: Path

    protocol_version = "HTTP/1.1"
    server_version = "PocketLocal/0.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(self.ui_root), **kwargs)

    def end_headers(self) -> None:
        if self.settings.cors_origin:
            self.send_header("Access-Control-Allow-Origin", self.settings.cors_origin)
            self.send_header("Vary", "Origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802 - stdlib handler API
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        path = urlsplit(self.path).path
        if path in {"/api/health", "/health"}:
            self._send_json(
                HTTPStatus.OK,
                {
                    "status": "ok",
                    "assistant": self.settings.assistant_name,
                    "backend": self.settings.backend,
                    "model": self.settings.model,
                    "streaming": True,
                    "auth_required": bool(self.settings.access_token),
                },
            )
            return
        if path == "/api/config":
            self._send_json(
                HTTPStatus.OK,
                {
                    "assistant": self.settings.assistant_name,
                    "backend": self.settings.backend,
                    "model": self.settings.model,
                    "chat_endpoint": "/api/chat",
                    "openai_endpoint": "/v1/chat/completions",
                    "auth_required": bool(self.settings.access_token),
                },
            )
            return
        if path.startswith("/api/") or path.startswith("/v1/"):
            self._send_error_json(HTTPStatus.NOT_FOUND, "API route not found")
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        path = urlsplit(self.path).path
        if path not in {"/api/chat", "/v1/chat/completions"}:
            self._send_error_json(HTTPStatus.NOT_FOUND, "API route not found")
            return
        if not self._authorized():
            self.close_connection = True
            self._send_json(
                HTTPStatus.UNAUTHORIZED,
                {"error": {"message": "missing or invalid bearer token"}},
                {
                    "WWW-Authenticate": 'Bearer realm="Pocket AI"',
                    "Connection": "close",
                },
            )
            return
        try:
            payload = self._read_json()
            parsed = (
                _friendly_request(payload, self.settings)
                if path == "/api/chat"
                else _openai_request(payload, self.settings)
            )
            messages, model, temperature, max_tokens, stream = parsed
            chunks = iter(
                self.backend_impl.stream(
                    messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
            # Pull once before committing HTTP 200 so immediate backend errors
            # can still be reported as a useful 502 JSON response.
            first = next(chunks, None)
        except RequestError as exc:
            self._send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
            return
        except BackendError as exc:
            self._send_error_json(HTTPStatus.BAD_GATEWAY, str(exc))
            return
        except Exception as exc:
            self.log_error("unexpected request failure: %s", exc)
            self._send_error_json(HTTPStatus.INTERNAL_SERVER_ERROR, "internal error")
            return

        if not stream:
            try:
                text = (first or "") + "".join(chunks)
            except BackendError as exc:
                self._send_error_json(HTTPStatus.BAD_GATEWAY, str(exc))
                return
            self._send_json(
                HTTPStatus.OK,
                {
                    "id": f"chatcmpl-{uuid4().hex}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": text},
                            "finish_reason": "stop",
                        }
                    ],
                },
            )
            return

        self._send_stream(chunks, first=first, model=model)

    def _read_json(self) -> object:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            raise RequestError("Content-Length is required")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise RequestError("invalid Content-Length") from exc
        if length <= 0 or length > MAX_REQUEST_BYTES:
            raise RequestError(f"request body must be 1 to {MAX_REQUEST_BYTES} bytes")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RequestError("request body must be valid UTF-8 JSON") from exc

    def _authorized(self) -> bool:
        expected = self.settings.access_token
        if not expected:
            return True
        supplied = self.headers.get("Authorization", "")
        prefix = "Bearer "
        if not supplied.startswith(prefix):
            return False
        return hmac.compare_digest(supplied[len(prefix) :], expected)

    def _send_json(
        self,
        status: HTTPStatus,
        payload: object,
        extra_headers: Mapping[str, str] | None = None,
    ) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)

    def _send_error_json(self, status: HTTPStatus, message: str) -> None:
        self._send_json(status, {"error": {"message": message}})

    def _sse(self, data: object, event: str | None = None) -> None:
        if event:
            self.wfile.write(f"event: {event}\n".encode("utf-8"))
        encoded = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
        self.wfile.write(f"data: {encoded}\n\n".encode("utf-8"))
        self.wfile.flush()

    def _send_stream(
        self, chunks: Iterable[str], *, first: str | None, model: str
    ) -> None:
        request_id = f"chatcmpl-{uuid4().hex}"
        created = int(time.time())
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

        def write_delta(text: str, finish_reason: str | None = None) -> None:
            delta = {"content": text} if text else {}
            self._sse(
                {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": delta,
                            "finish_reason": finish_reason,
                        }
                    ],
                }
            )

        try:
            if first:
                write_delta(first)
            for text in chunks:
                if text:
                    write_delta(text)
            write_delta("", "stop")
            self._sse("[DONE]")
        except BackendError as exc:
            self._sse({"error": {"message": str(exc)}}, event="error")
            self._sse("[DONE]")
        except (BrokenPipeError, ConnectionResetError):
            # The user navigated away or cancelled generation.
            return


def make_handler(
    settings: Settings, backend: ChatBackend | None = None
) -> type[PocketRequestHandler]:
    implementation: ChatBackend
    if backend is not None:
        implementation = backend
    elif settings.backend == "demo":
        implementation = DemoBackend()
    else:
        implementation = OpenAICompatibleBackend(
            settings.base_url, settings.api_key, settings.request_timeout
        )

    class ConfiguredHandler(PocketRequestHandler):
        pass

    ConfiguredHandler.settings = settings
    ConfiguredHandler.backend_impl = implementation
    ConfiguredHandler.ui_root = settings.ui_dir.resolve()
    return ConfiguredHandler


def build_server(
    settings: Settings, backend: ChatBackend | None = None
) -> ThreadingHTTPServer:
    settings.validate()
    return ThreadingHTTPServer(
        (settings.host, settings.port), make_handler(settings, backend)
    )


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the Pocket UI and proxy chat to a local model"
    )
    parser.add_argument("--host", help="listen address (default: environment/127.0.0.1)")
    parser.add_argument("--port", type=int, help="listen port (default: 8787)")
    parser.add_argument("--ui-dir", type=Path, help="directory containing index.html")
    parser.add_argument(
        "--demo", action="store_true", help="use deterministic demo replies; no model needed"
    )
    return parser.parse_args()


def main() -> None:
    args = _arguments()
    try:
        settings = Settings.from_env()
        overrides = {}
        if args.host is not None:
            overrides["host"] = args.host
        if args.port is not None:
            overrides["port"] = args.port
        if args.ui_dir is not None:
            overrides["ui_dir"] = args.ui_dir
        if args.demo:
            overrides["backend"] = "demo"
        settings = replace(settings, **overrides)
        server = build_server(settings)
    except ValueError as exc:
        raise SystemExit(f"Configuration error: {exc}") from None

    host, port = server.server_address[:2]
    if host in {"0.0.0.0", "::"}:
        print(f"{settings.assistant_name} is listening on all interfaces, port {port}")
        print(f"Browser on this computer: http://127.0.0.1:{port}")
        print(f"Device URL: http://<this-computer-private-LAN-IP>:{port}")
    else:
        print(f"{settings.assistant_name} is ready at http://{host}:{port}")
    if not _is_loopback_host(host):
        print("LAN mode is enabled; chat routes require POCKET_AI_TOKEN.")
    print(f"Backend: {settings.backend} / {settings.model}")
    if settings.backend != "demo":
        print(f"Local model endpoint: {chat_completions_url(settings.base_url)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Pocket.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
