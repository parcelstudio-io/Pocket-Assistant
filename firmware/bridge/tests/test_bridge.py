import base64
import asyncio
import json
import math
from array import array
from types import SimpleNamespace
import unittest

from aiohttp import WSMsgType
from aiohttp.test_utils import TestClient, TestServer

from bridge.audio import (INPUT_SAMPLES, OUTPUT_FRAME_BYTES, OUTPUT_SAMPLES,
                          OpusDecoder, OpusEncoder, upsample_16_to_24)
from bridge.server import Config, VoiceSession, create_app


class FakeSocket:
    def __init__(self):
        self.json = []
        self.audio = []

    async def send_json(self, event):
        self.json.append(event)

    async def send_bytes(self, frame):
        self.audio.append(frame)


class FakeRealtime(FakeSocket):
    def __init__(self):
        super().__init__()
        self.events = asyncio.Queue()

    async def emit(self, event):
        await self.events.put(SimpleNamespace(type=WSMsgType.TEXT, data=json.dumps(event)))

    async def close(self):
        await self.events.put(None)

    async def __aiter__(self):
        while (event := await self.events.get()) is not None:
            yield event


class AudioTests(unittest.TestCase):
    def test_opus_roundtrip_and_rate(self):
        pcm = array("h", (int(10000 * math.sin(2 * math.pi * 440 * n / 24000))
                          for n in range(OUTPUT_SAMPLES))).tobytes()
        encoder = OpusEncoder()
        decoder = OpusDecoder()
        try:
            encoded = encoder.encode(pcm)
            self.assertGreater(len(encoded), 0)
            # Input decoder runs at 16 kHz; Opus handles rate conversion.
            decoded = decoder.decode(encoded)
            self.assertEqual(len(decoded), INPUT_SAMPLES * 2)
            self.assertEqual(len(upsample_16_to_24(decoded)), OUTPUT_FRAME_BYTES)
        finally:
            encoder.close()
            decoder.close()


class SessionTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.config = Config("test-key", "a" * 16, "b" * 24, "192.168.1.10")
        self.device = FakeSocket()
        self.upstream = FakeSocket()
        self.session = VoiceSession(self.device, self.upstream, self.config)

    async def asyncTearDown(self):
        self.session.decoder.close()
        self.session.encoder.close()

    async def activate_response(self, response_id="resp_1"):
        await self.session.handle_device_text('{"type":"listen","state":"start"}')
        for kind in ("input_audio_buffer.speech_started",
                     "input_audio_buffer.speech_stopped",
                     "input_audio_buffer.committed"):
            await self.session.handle_realtime_event({"type": kind})
        create = self.upstream.json[-1]
        self.assertEqual(create["type"], "response.create")
        tag = create["response"]["metadata"]["a1_turn"]
        await self.session.handle_realtime_event({
            "type": "response.created",
            "response": {"id": response_id, "metadata": {"a1_turn": tag}},
        })
        return tag

    async def test_hello_and_session_update(self):
        await self.session.hello()
        self.assertEqual(self.device.json[0]["audio_params"]["sample_rate"], 24000)
        update = self.upstream.json[0]
        self.assertEqual(update["type"], "session.update")
        self.assertEqual(update["session"]["audio"]["input"]["turn_detection"]["type"],
                         "server_vad")
        self.assertFalse(update["session"]["audio"]["input"]["turn_detection"]["create_response"])
        self.assertEqual(update["session"]["audio"]["input"]["transcription"]["model"],
                         "gpt-4o-mini-transcribe")
        self.assertEqual(update["session"]["model"], "gpt-realtime-2.1-mini")
        self.assertNotIn("test-key", json.dumps(update))

    async def test_device_audio_to_realtime_and_stop_silence(self):
        await self.session.handle_device_text('{"type":"listen","state":"start"}')
        pcm = bytes(OUTPUT_FRAME_BYTES)
        encoder = OpusEncoder()
        try:
            await self.session.handle_device_audio(encoder.encode(pcm))
        finally:
            encoder.close()
        append = self.upstream.json[-1]
        self.assertEqual(append["type"], "input_audio_buffer.append")
        self.assertEqual(len(base64.b64decode(append["audio"])), OUTPUT_FRAME_BYTES)
        await self.session.handle_device_text('{"type":"listen","state":"stop"}')
        self.assertEqual(len(base64.b64decode(self.upstream.json[-1]["audio"])),
                         24000 * 2 * 600 // 1000)

    async def test_output_tts_order_partial_frame_and_interrupt(self):
        await self.activate_response()
        first = bytes(1000)
        second = bytes(OUTPUT_FRAME_BYTES - 1000)
        for pcm in (first, second):
            await self.session.handle_realtime_event({
                "type": "response.output_audio.delta", "response_id": "resp_1",
                "item_id": "item_1", "content_index": 0,
                "delta": base64.b64encode(pcm).decode(),
            })
        self.assertEqual([x["state"] for x in self.device.json], ["start"])
        self.assertEqual(len(self.device.audio), 1)
        await self.session.handle_realtime_event({"type": "input_audio_buffer.speech_started"})
        self.assertEqual([x["state"] for x in self.device.json], ["start", "stop"])
        self.assertIn({"type": "response.cancel", "response_id": "resp_1"},
                      self.upstream.json)
        self.assertIn({"type": "conversation.item.truncate", "item_id": "item_1",
                       "content_index": 0, "audio_end_ms": 0}, self.upstream.json)
        await self.session.handle_realtime_event({
            "type": "response.output_audio.delta", "response_id": "resp_1",
            "delta": base64.b64encode(bytes(OUTPUT_FRAME_BYTES)).decode(),
        })
        self.assertEqual(len(self.device.audio), 1)

    async def test_last_partial_frame_is_padded_then_stopped(self):
        await self.activate_response()
        await self.session.handle_realtime_event({
            "type": "response.output_audio.delta", "response_id": "resp_1",
            "item_id": "item_1", "content_index": 0,
            "delta": base64.b64encode(bytes(800)).decode(),
        })
        await self.session.handle_realtime_event({"type": "response.output_audio.done",
                                                  "response_id": "resp_1"})
        self.assertEqual(len(self.device.audio), 1)
        self.assertEqual([x["state"] for x in self.device.json], ["start", "stop"])

    async def test_late_response_cannot_reopen_playback_after_new_listen(self):
        old_tag = await self.activate_response("resp_old")
        await self.session.handle_realtime_event({
            "type": "response.output_audio.delta", "response_id": "resp_old",
            "item_id": "item_old", "content_index": 0,
            "delta": base64.b64encode(bytes(OUTPUT_FRAME_BYTES)).decode(),
        })
        self.assertEqual(len(self.device.audio), 1)
        await self.session.handle_device_text('{"type":"listen","state":"start"}')
        self.assertIn({"type": "response.cancel", "response_id": "resp_old"},
                      self.upstream.json)
        self.assertIn({"type": "conversation.item.truncate", "item_id": "item_old",
                       "content_index": 0, "audio_end_ms": 0}, self.upstream.json)
        await self.session.handle_realtime_event({
            "type": "response.created",
            "response": {"id": "resp_stale", "metadata": {"a1_turn": old_tag}},
        })
        self.assertIn({"type": "response.cancel", "response_id": "resp_stale"},
                      self.upstream.json)
        for response_id in ("resp_old", "resp_stale"):
            await self.session.handle_realtime_event({
                "type": "response.output_audio.delta", "response_id": response_id,
                "item_id": "item_stale",
                "delta": base64.b64encode(bytes(OUTPUT_FRAME_BYTES)).decode(),
            })
        self.assertEqual(len(self.device.audio), 1)
        for kind in ("input_audio_buffer.speech_started",
                     "input_audio_buffer.speech_stopped",
                     "input_audio_buffer.committed"):
            await self.session.handle_realtime_event({"type": kind})
        new_tag = self.upstream.json[-1]["response"]["metadata"]["a1_turn"]
        await self.session.handle_realtime_event({
            "type": "response.created",
            "response": {"id": "resp_new", "metadata": {"a1_turn": new_tag}},
        })
        await self.session.handle_realtime_event({
            "type": "response.output_audio.delta", "response_id": "resp_new",
            "item_id": "item_new", "content_index": 0,
            "delta": base64.b64encode(bytes(OUTPUT_FRAME_BYTES)).decode(),
        })
        self.assertEqual(len(self.device.audio), 2)

    async def test_abort_without_active_response_does_not_cancel(self):
        await self.session.handle_device_text('{"type":"abort"}')
        self.assertFalse(any(item["type"] == "response.cancel"
                             for item in self.upstream.json))
        await self.session.handle_realtime_event({
            "type": "error", "error": {"code": "response_cancel_not_active"}})

    async def test_abort_truncates_active_speech(self):
        await self.activate_response("resp_abort")
        await self.session.handle_realtime_event({
            "type": "response.output_audio.delta", "response_id": "resp_abort",
            "item_id": "item_abort", "content_index": 0,
            "delta": base64.b64encode(bytes(OUTPUT_FRAME_BYTES)).decode(),
        })
        await self.session.handle_device_text('{"type":"abort"}')
        self.assertIn({"type": "response.cancel", "response_id": "resp_abort"},
                      self.upstream.json)
        self.assertIn({"type": "conversation.item.truncate", "item_id": "item_abort",
                       "content_index": 0, "audio_end_ms": 0}, self.upstream.json)
        self.assertEqual([x["state"] for x in self.device.json], ["start", "stop"])

    async def test_input_transcript_reaches_a1_display(self):
        await self.session.handle_realtime_event({
            "type": "conversation.item.input_audio_transcription.completed",
            "transcript": "Turn the light on.",
        })
        self.assertEqual(self.device.json[-1]["type"], "stt")
        self.assertEqual(self.device.json[-1]["text"], "Turn the light on.")


class HttpTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.config = Config("test-key", "a" * 16, "b" * 24, "192.168.1.10")
        self.upstream = FakeRealtime()

        async def upstream_factory(client_session, device_id):
            self.assertEqual(device_id, "a1-test")
            return self.upstream

        self.client = TestClient(TestServer(create_app(self.config, upstream_factory)))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()

    async def test_ota_bootstrap_and_websocket_auth(self):
        response = await self.client.post("/ota/" + "c" * 24, json={"board": "test"})
        self.assertEqual(response.status, 404)
        response = await self.client.post("/ota/" + "b" * 24, json={"board": "test"})
        self.assertEqual(response.status, 200)
        data = await response.json()
        self.assertEqual(data["websocket"], {
            "url": "ws://192.168.1.10:8765/ws", "token": "a" * 16, "version": 1,
        })
        self.assertNotIn("test-key", json.dumps(data))
        response = await self.client.get("/ws")
        self.assertEqual(response.status, 401)

    async def test_complete_mock_websocket_voice_exchange(self):
        ws = await self.client.ws_connect(
            "/ws", headers={"Authorization": "Bearer " + "a" * 16,
                            "Device-Id": "a1-test", "Protocol-Version": "1"})
        try:
            await ws.send_json({
                "type": "hello", "version": 1, "transport": "websocket",
                "audio_params": {"format": "opus", "sample_rate": 16000,
                                 "channels": 1, "frame_duration": 60},
            })
            reply = await ws.receive_json(timeout=2)
            self.assertEqual(reply["type"], "hello")
            self.assertEqual(reply["audio_params"]["sample_rate"], 24000)
            self.assertEqual(self.upstream.json[0]["type"], "session.update")

            await ws.send_json({"type": "listen", "state": "start", "mode": "auto"})
            encoder = OpusEncoder()
            try:
                await ws.send_bytes(encoder.encode(bytes(OUTPUT_FRAME_BYTES)))
            finally:
                encoder.close()
            for _ in range(50):
                if any(item["type"] == "input_audio_buffer.append" for item in self.upstream.json):
                    break
                await asyncio.sleep(0.01)
            self.assertTrue(any(item["type"] == "input_audio_buffer.append"
                                for item in self.upstream.json))

            for kind in ("input_audio_buffer.speech_started",
                         "input_audio_buffer.speech_stopped",
                         "input_audio_buffer.committed"):
                await self.upstream.emit({"type": kind})
            for _ in range(50):
                creates = [item for item in self.upstream.json
                           if item["type"] == "response.create"]
                if creates:
                    break
                await asyncio.sleep(0.01)
            self.assertTrue(creates)
            tag = creates[-1]["response"]["metadata"]["a1_turn"]
            await self.upstream.emit({"type": "response.created",
                                      "response": {"id": "resp_1", "metadata": {
                                          "a1_turn": tag}}})
            await self.upstream.emit({"type": "response.output_audio.delta",
                                      "response_id": "resp_1", "item_id": "item_1",
                                      "content_index": 0,
                                      "delta": base64.b64encode(bytes(OUTPUT_FRAME_BYTES)).decode()})
            await self.upstream.emit({"type": "response.output_audio.done",
                                      "response_id": "resp_1"})
            tts_start = await ws.receive_json(timeout=2)
            self.assertEqual((tts_start["type"], tts_start["state"]), ("tts", "start"))
            audio = await ws.receive(timeout=2)
            self.assertEqual(audio.type, WSMsgType.BINARY)
            self.assertGreater(len(audio.data), 0)
            tts_stop = await ws.receive_json(timeout=2)
            self.assertEqual((tts_stop["type"], tts_stop["state"]), ("tts", "stop"))
        finally:
            await ws.close()


if __name__ == "__main__":
    unittest.main()
