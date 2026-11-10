import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import threading
import unittest
from unittest import mock
from urllib.error import HTTPError
from urllib.request import Request, urlopen


SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

from server import (  # noqa: E402
    DemoBackend,
    OpenAICompatibleBackend,
    Settings,
    build_server,
    chat_completions_url,
)


class FakeBackend:
    def __init__(self, chunks=("hello ", "there")):
        self.chunks = chunks
        self.calls = []

    def stream(self, messages, *, model, temperature, max_tokens):
        self.calls.append(
            {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        yield from self.chunks


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        ui_dir = Path(self.temp_dir.name)
        (ui_dir / "index.html").write_text("<h1>Pocket test</h1>", encoding="utf-8")
        self.backend = FakeBackend()
        self.settings = Settings(
            host="127.0.0.1",
            port=0,
            backend="demo",
            model="test-model",
            api_key="do-not-leak",
            cors_origin="http://ui.example",
            ui_dir=ui_dir,
        )
        self.server = build_server(self.settings, self.backend)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp_dir.cleanup()

    def get(self, path):
        with urlopen(f"{self.base}{path}", timeout=2) as response:
            return response, response.read()

    def post(self, path, payload):
        data = json.dumps(payload).encode()
        request = Request(
            f"{self.base}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=2) as response:
            return response, response.read()

    def test_health_config_and_static_ui(self):
        response, body = self.get("/api/health")
        health = json.loads(body)
        self.assertEqual(response.status, 200)
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"], "http://ui.example"
        )
        self.assertEqual(health["backend"], "demo")
        self.assertTrue(health["streaming"])

        _, body = self.get("/api/config")
        config = json.loads(body)
        self.assertEqual(config["model"], "test-model")
        self.assertNotIn("do-not-leak", body.decode())

        _, body = self.get("/")
        self.assertIn(b"Pocket test", body)

    def test_friendly_chat_streams_openai_sse(self):
        response, body = self.post(
            "/api/chat",
            {
                "message": "How are you?",
                "history": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello!"},
                ],
            },
        )
        text = body.decode()
        self.assertEqual(response.headers.get_content_type(), "text/event-stream")
        self.assertIn('"content": "hello "', text)
        self.assertIn('"content": "there"', text)
        self.assertTrue(text.rstrip().endswith("data: [DONE]"))
        call = self.backend.calls[0]
        self.assertEqual(call["messages"][-1], {"role": "user", "content": "How are you?"})
        self.assertEqual(call["messages"][0]["role"], "system")

    def test_openai_nonstreaming_compatibility(self):
        response, body = self.post(
            "/v1/chat/completions",
            {
                "model": "another-model",
                "messages": [{"role": "user", "content": "hello"}],
                "stream": False,
            },
        )
        payload = json.loads(body)
        self.assertEqual(response.status, 200)
        self.assertEqual(payload["choices"][0]["message"]["content"], "hello there")
        self.assertEqual(self.backend.calls[0]["model"], "another-model")

    def test_invalid_history_is_a_json_400(self):
        data = json.dumps(
            {"message": "hi", "history": [{"role": "system", "content": "bad"}]}
        ).encode()
        request = Request(
            f"{self.base}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=2)
        self.assertEqual(caught.exception.code, 400)
        error = json.loads(caught.exception.read())
        caught.exception.close()
        self.assertIn("history roles", error["error"]["message"])

    def test_optional_bearer_token_guards_chat(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        protected = Settings(
            host="127.0.0.1",
            port=0,
            backend="demo",
            model="test-model",
            access_token="correct-token",
            ui_dir=Path(self.temp_dir.name),
        )
        self.server = build_server(protected, self.backend)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

        payload = json.dumps({"message": "hello"}).encode()
        missing = Request(f"{self.base}/api/chat", data=payload, method="POST")
        with self.assertRaises(HTTPError) as caught:
            urlopen(missing, timeout=2)
        self.assertEqual(caught.exception.code, 401)
        caught.exception.close()

        allowed = Request(
            f"{self.base}/api/chat",
            data=payload,
            headers={"Authorization": "Bearer correct-token"},
            method="POST",
        )
        with urlopen(allowed, timeout=2) as response:
            self.assertIn(b"data: [DONE]", response.read())


class BackendTests(unittest.TestCase):
    def test_non_loopback_bind_requires_access_token(self):
        with self.assertRaisesRegex(ValueError, "POCKET_AI_TOKEN is required"):
            Settings(host="0.0.0.0", access_token="").validate()

        Settings(host="0.0.0.0", access_token="long-test-token").validate()
        Settings(host="127.0.0.1", access_token="").validate()

    def test_base_url_normalization(self):
        self.assertEqual(
            chat_completions_url("http://127.0.0.1:11434"),
            "http://127.0.0.1:11434/v1/chat/completions",
        )
        self.assertEqual(
            chat_completions_url("http://localhost:8080/v1"),
            "http://localhost:8080/v1/chat/completions",
        )

    def test_openai_backend_parses_sse_without_external_model(self):
        class FakeResponse:
            headers = {"Content-Type": "text/event-stream"}

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def __iter__(self):
                return iter(
                    [
                        b'data: {"choices":[{"delta":{"content":"Hi"}}]}\n',
                        b'data: {"choices":[{"delta":{"content":"!"}}]}\n',
                        b"data: [DONE]\n",
                    ]
                )

        backend = OpenAICompatibleBackend(
            "http://127.0.0.1:11434", api_key="secret", timeout=1
        )
        with mock.patch("server.urlopen", return_value=FakeResponse()) as opened:
            result = list(
                backend.stream(
                    [{"role": "user", "content": "Hi"}],
                    model="tiny",
                    temperature=0.2,
                    max_tokens=32,
                )
            )
        self.assertEqual(result, ["Hi", "!"])
        request = opened.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        sent = json.loads(request.data)
        self.assertTrue(sent["stream"])
        self.assertEqual(sent["model"], "tiny")

    def test_demo_backend_is_deterministic(self):
        backend = DemoBackend()
        kwargs = {"model": "ignored", "temperature": 0.7, "max_tokens": 100}
        messages = [{"role": "user", "content": "test the face"}]
        first = "".join(backend.stream(messages, **kwargs))
        second = "".join(backend.stream(messages, **kwargs))
        self.assertEqual(first, second)
        self.assertIn("test the face", first)


if __name__ == "__main__":
    unittest.main()
