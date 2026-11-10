"""Local speech engines: synthesise a sentence with Kokoro, hear it back with Whisper."""

import importlib.util
import os
import unittest

os.environ["POCKET_MEMORY_DB"] = ":memory:"  # tests never write the real memory file

from pocket_server import audio
from pocket_server.config import Config

HAVE_LOCAL = importlib.util.find_spec("faster_whisper") and importlib.util.find_spec("kokoro")


@unittest.skipUnless(HAVE_LOCAL, "faster-whisper and kokoro are not installed in this interpreter")
class LocalRoundTripTest(unittest.IsolatedAsyncioTestCase):
    async def test_kokoro_to_whisper(self):
        from pocket_server.speech import LocalSTT, LocalTTS

        cfg = Config(stt="local", tts="local").resolved()
        tts, stt = LocalTTS(cfg), LocalSTT(cfg)
        pcm = b"".join([c async for c in tts.speak("The brass frame keeps the antenna in open air.")])
        self.assertGreater(len(pcm) / 2 / 16000, 1.5)          # a sentence of 16 kHz audio came out
        self.assertEqual(len(pcm) % 2, 0)
        heard = (await stt.transcribe(pcm)).lower()
        for word in ("brass", "frame", "antenna", "air"):
            self.assertIn(word, heard)

    async def test_silence_is_nothing(self):
        from pocket_server.speech import LocalSTT

        stt = LocalSTT(Config(stt="local").resolved())
        self.assertEqual(await stt.transcribe(bytes(16000 * 2)), "")
