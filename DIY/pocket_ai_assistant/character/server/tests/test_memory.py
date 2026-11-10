import os, tempfile, unittest
from pocket_server.memory import Memory, rename_request


class RenameTest(unittest.TestCase):
    def test_detects_requests(self):
        for text, name in [("From now on your name is Nova.", "Nova"), ("I'll call you Bolt", "Bolt"),
                           ("Can you change your name to Ada?", "Ada"), ("call yourself zed", "Zed"),
                           ("you are now called Kit!", "Kit")]:
            self.assertEqual(rename_request(text), name, text)

    def test_ignores_ordinary_talk(self):
        for text in ["What is your name?", "My name is Jae", "The weather is nice", "I call you every day"]:
            self.assertIsNone(rename_request(text), text)


class MemoryTest(unittest.TestCase):
    def test_history_persists_across_reopen(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "m.sqlite3")
            m = Memory(path, "Pip")
            m.add_message("user", "hello", "dev"); m.add_message("assistant", "hi there", "dev")
            m.set_name("Nova")
            m2 = Memory(path, "Pip")
            self.assertEqual(m2.name, "Nova")
            self.assertEqual([x["content"] for x in m2.recent(5)], ["hello", "hi there"])
            self.assertEqual(m2.count(), 2)

    def test_reflection_updates_notes_and_name(self):
        m = Memory(":memory:", "Pip")
        raw = '```json\n{"user_profile": "Builder named Jae, likes brass.", "persona_notes": "Calls them boss.", "summary": "Met today.", "name": "Nova"}\n```'
        self.assertTrue(m.apply_reflection(raw))
        self.assertEqual(m.user_profile, "Builder named Jae, likes brass.")
        self.assertEqual(m.name, "Nova")
        self.assertIn("Builder named Jae", m.context_block())
        self.assertFalse(m.apply_reflection("not json at all"))

    def test_context_has_the_clock(self):
        m = Memory(":memory:", "Pip")
        self.assertIn("Right now it is", m.context_block())


if __name__ == "__main__":
    unittest.main()
