"""Long-term memory: the conversation history, the character's evolving persona and name, and a
profile of the person it talks to. One SQLite file, shared by every session and every day.

Tables:
  messages(id, ts, device, role, text)   every user and assistant line, forever
  kv(key, value)                         name · user_profile · persona_notes · summary · counters
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import threading
import time
from datetime import datetime
from typing import Any

log = logging.getLogger("pocket.memory")

Message = dict[str, str]

# "your name is Pip", "I'll call you Nova", "call yourself Bolt", "change your name to Zed",
# "from now on you are Max", "rename yourself to Ada", "you are now called Kit"
_RENAME = re.compile(
    r"(?:your name is|your name will be|your new name is|i(?:'ll| will| want to) call you|call yourself|"
    r"change your name to|rename yourself(?: to| as)?|from now on(?:,)? (?:you are|you're|your name is)|"
    r"you are now called|you're now called|be called|go by)\s+(?:the name\s+)?\"?([A-Za-z][A-Za-z'\-]{0,24})\"?",
    re.IGNORECASE,
)
_NOT_NAMES = {"pip", "not", "my", "the", "a", "an", "still", "also", "now", "what", "who", "called"}

MAX_PROFILE = 2000     # characters kept for the user profile
MAX_NOTES = 1500       # characters kept for the persona notes
MAX_SUMMARY = 1500     # characters kept for the rolling summary of old talk


def rename_request(text: str) -> str | None:
    """A new name if the sentence asks the character to change its name, else None."""
    m = _RENAME.search(text)
    if not m:
        return None
    name = m.group(1).strip("'\"-")
    if not name or name.lower() in _NOT_NAMES or name.lower() in ("pip",) and "pip" not in text.lower():
        return None
    return name[:1].upper() + name[1:]


class Memory:
    def __init__(self, path: str, default_name: str = "Pip") -> None:
        self.path = path
        self.default_name = default_name
        if path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._lock = threading.Lock()
        with self._lock:
            self._db.executescript(
                "CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, ts REAL NOT NULL, device TEXT, "
                "role TEXT NOT NULL, text TEXT NOT NULL);"
                "CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, value TEXT NOT NULL);"
            )
            self._db.commit()

    # ---- key/value -----------------------------------------------------------------------

    def get(self, key: str, default: str = "") -> str:
        with self._lock:
            row = self._db.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set(self, key: str, value: str) -> None:
        with self._lock:
            self._db.execute("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                             (key, value))
            self._db.commit()

    @property
    def name(self) -> str:
        return self.get("name", self.default_name)

    def set_name(self, name: str) -> None:
        old = self.name
        self.set("name", name)
        if old != name:
            log.info("character renamed: %s -> %s", old, name)
            self.add_message("system", f"The character's name changed from {old} to {name}.", device="memory")

    @property
    def user_profile(self) -> str:
        return self.get("user_profile", "")

    @property
    def persona_notes(self) -> str:
        return self.get("persona_notes", "")

    @property
    def summary(self) -> str:
        return self.get("summary", "")

    # ---- messages ------------------------------------------------------------------------

    def add_message(self, role: str, text: str, device: str = "") -> None:
        with self._lock:
            self._db.execute("INSERT INTO messages(ts,device,role,text) VALUES(?,?,?,?)", (time.time(), device, role, text))
            self._db.commit()

    def recent(self, turns: int) -> list[Message]:
        """The last `turns` user/assistant exchanges, oldest first, as chat messages."""
        with self._lock:
            rows = self._db.execute(
                "SELECT role, text FROM messages WHERE role IN ('user','assistant') ORDER BY id DESC LIMIT ?",
                (2 * turns,)).fetchall()
        return [{"role": r, "content": t} for r, t in reversed(rows)]

    def count(self) -> int:
        with self._lock:
            return int(self._db.execute("SELECT COUNT(*) FROM messages WHERE role IN ('user','assistant')").fetchone()[0])

    def last_seen(self) -> float | None:
        with self._lock:
            row = self._db.execute("SELECT MAX(ts) FROM messages WHERE role='user'").fetchone()
        return float(row[0]) if row and row[0] else None

    # ---- prompt context ------------------------------------------------------------------

    def context_block(self) -> str:
        now = datetime.now()
        parts = [f"Right now it is {now.strftime('%A %d %B %Y, %H:%M')}."]
        seen = self.last_seen()
        if seen:
            gap = time.time() - seen
            if gap > 6 * 3600:
                hours = gap / 3600
                parts.append(f"You last spoke with them about {hours / 24:.0f} days ago." if hours > 48
                             else f"You last spoke with them about {hours:.0f} hours ago.")
        if self.user_profile:
            parts.append("What you know about the person you talk to (your builder and friend):\n" + self.user_profile)
        if self.persona_notes:
            parts.append("Notes about yourself and your relationship with them, which you keep up to date:\n" + self.persona_notes)
        if self.summary:
            parts.append("Summary of earlier conversations:\n" + self.summary)
        parts.append("Use this knowledge naturally, the way a close friend remembers things; never recite it as a list, "
                     "and never claim to remember something that is not in it.")
        return "\n\n".join(parts)

    # ---- reflection ----------------------------------------------------------------------

    def reflection_prompt(self, exchange: list[Message]) -> list[Message]:
        """Messages for the brain: update the profile, the notes, the summary and maybe the name."""
        convo = "\n".join(f"{m['role']}: {m['content']}" for m in exchange)
        instructions = (
            f"You are the memory of a small robot companion currently named {self.name}. "
            "Given the current notes and the latest exchange, return the UPDATED notes as JSON with exactly these keys: "
            "user_profile, persona_notes, summary, name.\n"
            "- user_profile: everything worth remembering about the person: name, how they like to be addressed, work, "
            "projects, people and pets they mention, preferences, routines, moods, important dates, things they asked you "
            "to remember. Merge new facts into the old text; keep it under 1800 characters; plain prose or short lines.\n"
            "- persona_notes: who the robot is becoming with this person: running jokes, nicknames, promises, things to follow "
            "up on, how close you are, what they like about you. Under 1300 characters.\n"
            "- summary: a rolling summary of earlier conversations, updated with anything the latest exchange settles. "
            "Under 1300 characters.\n"
            "- name: the robot's name. Keep it unchanged unless the person explicitly asked the robot to take a new name "
            "in this exchange.\n"
            "Only record what was actually said. Do not invent. Output only the JSON object, no commentary, no code fences."
        )
        current = json.dumps({"user_profile": self.user_profile, "persona_notes": self.persona_notes,
                              "summary": self.summary, "name": self.name}, ensure_ascii=False)
        return [
            {"role": "system", "content": instructions},
            {"role": "user", "content": f"CURRENT NOTES:\n{current}\n\nLATEST EXCHANGE:\n{convo}\n\nUPDATED NOTES (JSON):"},
        ]

    def apply_reflection(self, raw: str) -> bool:
        data = _parse_json(raw)
        if not isinstance(data, dict):
            log.warning("reflection returned no JSON (%d chars)", len(raw or ""))
            return False
        changed = False
        for key, cap in (("user_profile", MAX_PROFILE), ("persona_notes", MAX_NOTES), ("summary", MAX_SUMMARY)):
            value = data.get(key)
            if isinstance(value, str):
                value = value.strip()[:cap]
                if value and value != self.get(key, ""):
                    self.set(key, value)
                    changed = True
        name = data.get("name")
        if isinstance(name, str):
            name = name.strip()[:25]
            if name and name != self.name and re.fullmatch(r"[A-Za-z][A-Za-z'\- ]{0,24}", name):
                self.set_name(name)
                changed = True
        self.set("reflections", str(int(self.get("reflections", "0")) + 1))
        return changed

    def stats(self) -> dict[str, Any]:
        return {"name": self.name, "messages": self.count(), "profile_chars": len(self.user_profile),
                "persona_chars": len(self.persona_notes), "summary_chars": len(self.summary),
                "reflections": int(self.get("reflections", "0")), "path": self.path}


def _parse_json(raw: str) -> Any:
    if not raw:
        return None
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except ValueError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except ValueError:
            return None
    return None
