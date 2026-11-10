"""End-to-end over a real WebSocket with the demo brain and demo voice."""

import json
import os
import unittest

os.environ["POCKET_MEMORY_DB"] = ":memory:"  # tests never write the real memory file

from aiohttp import WSMsgType
from aiohttp.test_utils import AioHTTPTestCase

from pocket_server import protocol as P
from pocket_server.app import build_app
from pocket_server.config import Config

HELLO = {"type": "hello", "device": "test", "version": 1,
         "audio": {"rate": 16000, "bits": 16, "channels": 1, "frame_ms": 40, "codec": "pcm"}}


class DemoSessionTest(AioHTTPTestCase):
    async def get_application(self):
        cfg = Config(brain="demo", stt="demo", tts="demo", name="Pip").resolved()
        return build_app(cfg)

    async def collect(self, ws, until_idle=True):
        events, audio = [], bytearray()
        async for msg in ws:
            if msg.type == WSMsgType.BINARY:
                audio += msg.data
                continue
            if msg.type != WSMsgType.TEXT:
                break
            ev = json.loads(msg.data)
            events.append(ev)
            if until_idle and ev.get("type") == "state" and ev["state"] == "idle" and len(events) > 2:
                break
        return events, bytes(audio)

    async def test_health(self):
        async with self.client.get("/health") as r:
            body = await r.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["brain"], "demo")
        self.assertEqual(body["audio"]["rate"], 16000)

    async def test_text_turn_speaks_with_emotion(self):
        async with self.client.ws_connect("/ws") as ws:
            await ws.send_str(P.encode(HELLO))
            hello = json.loads((await ws.receive()).data)
            self.assertTrue(hello["ok"])
            self.assertEqual(hello["name"], "Pip")
            # initial idle + happy
            await ws.receive(); await ws.receive()
            await ws.send_str(P.encode({"type": "text", "text": "what is your name?"}))
            events, audio = await self.collect(ws)
        kinds = [(e["type"], e.get("state") or e.get("emotion") or e.get("action") or e.get("role")) for e in events]
        self.assertIn(("state", "thinking"), kinds)
        self.assertIn(("emotion", "happy"), kinds)
        self.assertIn(("transcript", "user"), kinds)
        self.assertIn(("audio", "start"), kinds)
        self.assertIn(("state", "speaking"), kinds)
        self.assertIn(("audio", "end"), kinds)
        self.assertEqual(kinds[-1], ("state", "idle"))
        self.assertGreater(len(audio), P.FRAME_BYTES * 5)
        self.assertEqual(len(audio) % P.FRAME_BYTES, 0)
        # emotion comes before the first audio frame
        self.assertLess(kinds.index(("emotion", "happy")), kinds.index(("audio", "start")))
        assistant = [e for e in events if e["type"] == "transcript" and e["role"] == "assistant"]
        self.assertTrue(assistant and assistant[0]["text"].startswith("My name is Pip"))
        # the reply text arrives as soon as the brain is done, not after the speech has been paced out
        self.assertLess(kinds.index(("transcript", "assistant")), kinds.index(("audio", "end")))

    async def test_voice_turn_with_silence_is_heard_as_nothing(self):
        async with self.client.ws_connect("/ws") as ws:
            await ws.send_str(P.encode(HELLO))
            await ws.receive(); await ws.receive(); await ws.receive()
            await ws.send_str(P.encode({"type": "listen", "action": "start"}))
            for _ in range(10):
                await ws.send_bytes(bytes(P.FRAME_BYTES))  # silence
            await ws.send_str(P.encode({"type": "listen", "action": "stop"}))
            events, audio = await self.collect(ws)
        states = [e["state"] for e in events if e["type"] == "state"]
        self.assertEqual(states[0], "listening")
        self.assertEqual(states[-1], "idle")
        self.assertEqual(audio, b"")
        self.assertIn("heard nothing", events[-1].get("message", ""))

    async def test_voice_turn_with_sound_gets_a_reply(self):
        from pocket_server.audio import demo_voice, frames
        async with self.client.ws_connect("/ws") as ws:
            await ws.send_str(P.encode(HELLO))
            await ws.receive(); await ws.receive(); await ws.receive()
            await ws.send_str(P.encode({"type": "listen", "action": "start"}))
            for frame in frames(demo_voice("this is me talking to you for a while")):
                await ws.send_bytes(frame)
            await ws.send_str(P.encode({"type": "listen", "action": "stop"}))
            events, audio = await self.collect(ws)
        self.assertGreater(len(audio), 0)
        user = [e for e in events if e["type"] == "transcript" and e["role"] == "user"]
        self.assertTrue(user and "you spoke for" in user[0]["text"])

    async def test_hello_refused_without_hello(self):
        async with self.client.ws_connect("/ws") as ws:
            await ws.send_str(P.encode({"type": "ping"}))
            reply = json.loads((await ws.receive()).data)
            self.assertFalse(reply["ok"])

    async def test_bad_audio_format_refused(self):
        async with self.client.ws_connect("/ws") as ws:
            await ws.send_str(P.encode({**HELLO, "audio": {"rate": 8000}}))
            reply = json.loads((await ws.receive()).data)
            self.assertFalse(reply["ok"])

    async def test_abort_stops_speaking(self):
        async with self.client.ws_connect("/ws") as ws:
            await ws.send_str(P.encode(HELLO))
            await ws.receive(); await ws.receive(); await ws.receive()
            await ws.send_str(P.encode({"type": "text", "text": "tell me a joke"}))
            # wait for speaking, then abort
            while True:
                msg = await ws.receive()
                if msg.type == WSMsgType.TEXT and json.loads(msg.data).get("state") == "speaking":
                    break
            await ws.send_str(P.encode({"type": "abort"}))
            events, _ = await self.collect(ws)
        self.assertEqual(events[-1]["state"], "idle")
        self.assertEqual(events[-1].get("message"), "aborted by device")


class TokenTest(AioHTTPTestCase):
    async def get_application(self):
        cfg = Config(brain="demo", stt="none", tts="none", token="secret-token-1234567").resolved()
        return build_app(cfg)

    async def test_wrong_token(self):
        async with self.client.ws_connect("/ws") as ws:
            await ws.send_str(P.encode({**HELLO, "token": "nope"}))
            reply = json.loads((await ws.receive()).data)
            self.assertEqual(reply, {"type": "hello", "ok": False, "error": "bad token"})

    async def test_right_token_and_no_tts(self):
        async with self.client.ws_connect("/ws") as ws:
            await ws.send_str(P.encode({**HELLO, "token": "secret-token-1234567"}))
            reply = json.loads((await ws.receive()).data)
            self.assertTrue(reply["ok"])
            await ws.receive(); await ws.receive()
            await ws.send_str(P.encode({"type": "text", "text": "hi"}))
            events = []
            async for msg in ws:
                ev = json.loads(msg.data)
                events.append(ev)
                if ev.get("state") == "idle":
                    break
        kinds = [e["type"] for e in events]
        self.assertNotIn("audio", kinds)        # tts=none: no audio at all
        self.assertIn("transcript", kinds)      # but the text still comes back


if __name__ == "__main__":
    unittest.main()
