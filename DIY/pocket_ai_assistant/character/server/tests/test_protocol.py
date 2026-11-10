import os
import unittest

os.environ["POCKET_MEMORY_DB"] = ":memory:"  # tests never write the real memory file

from pocket_server import audio, protocol as P


class EmotionTagParserTest(unittest.TestCase):
    def feed_all(self, deltas):
        parser = P.EmotionTagParser()
        out = "".join(parser.feed(d) for d in deltas) + parser.flush()
        return parser.emotion, out

    def test_tag_in_one_piece(self):
        self.assertEqual(self.feed_all(["[happy] Hello there."]), ("happy", "Hello there."))

    def test_tag_split_across_deltas(self):
        self.assertEqual(self.feed_all(["[", "ha", "ppy", "] Hel", "lo"]), ("happy", "Hello"))

    def test_leading_whitespace_and_case(self):
        self.assertEqual(self.feed_all(["  [ Sad ]  oh no"]), ("sad", "oh no"))

    def test_no_tag(self):
        self.assertEqual(self.feed_all(["Hello ", "world"]), (None, "Hello world"))

    def test_unknown_tag_is_spoken(self):
        emotion, text = self.feed_all(["[banana] yes"])
        self.assertIsNone(emotion)
        self.assertEqual(text, "yes")

    def test_bracket_later_is_text(self):
        self.assertEqual(self.feed_all(["I said [sad] once"]), (None, "I said [sad] once"))

    def test_long_bracket_without_close_is_spoken(self):
        emotion, text = self.feed_all(["[this is not a tag and it keeps going on"])
        self.assertIsNone(emotion)
        self.assertTrue(text.startswith("[this is not"))


class MessageTest(unittest.TestCase):
    def test_round_trip(self):
        msg = P.state("speaking", "x")
        self.assertEqual(P.decode(P.encode(msg)), msg)

    def test_decode_rejects_junk(self):
        self.assertIsNone(P.decode("not json"))
        self.assertIsNone(P.decode("[1,2]"))
        self.assertIsNone(P.decode('{"type": 5}'))

    def test_audio_format(self):
        self.assertTrue(P.audio_format_ok({"rate": 16000, "bits": 16, "channels": 1, "codec": "pcm"}))
        self.assertTrue(P.audio_format_ok(None))
        self.assertFalse(P.audio_format_ok({"rate": 24000}))
        self.assertFalse(P.audio_format_ok({"codec": "opus"}))

    def test_unknown_emotion_becomes_neutral(self):
        self.assertEqual(P.emotion("bored")["emotion"], "neutral")


class AudioTest(unittest.TestCase):
    def test_frames_pad_last(self):
        pcm = bytes(P.FRAME_BYTES * 2 + 10)
        out = list(audio.frames(pcm))
        self.assertEqual(len(out), 3)
        self.assertTrue(all(len(f) == P.FRAME_BYTES for f in out))

    def test_resample_ratio(self):
        pcm = bytes(24000 * 2)  # one second at 24 kHz
        out = audio.resample(pcm, 24000, 16000)
        self.assertEqual(len(out), 16000 * 2)

    def test_wav_round_trip(self):
        pcm = audio.demo_voice("hello world")
        self.assertGreater(len(pcm), 1000)
        back, rate = audio.wav_to_pcm(audio.pcm_to_wav(pcm))
        self.assertEqual((back, rate), (pcm, P.SAMPLE_RATE))

    def test_demo_voice_is_quiet_enough(self):
        pcm = audio.demo_voice("a loud test sentence!")
        self.assertLess(max(abs(int.from_bytes(pcm[i:i + 2], "little", signed=True)) for i in range(0, len(pcm), 2)), 9000)


if __name__ == "__main__":
    unittest.main()
