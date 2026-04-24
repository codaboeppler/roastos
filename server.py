#!/usr/bin/env python3
"""Local server for the System Widget — AI voices + funnier quotes + panic kill.

Endpoints (localhost-only):
    GET  /            → index.html / popover.html (static)
    GET  /stats       → JSON snapshot (RAM/disk/CPU/top-20 + current settings)
    POST /kill?pid=X  → SIGTERM + coin sound + AI-voiced last words
                        (?force=1 for SIGKILL + dramatic error sound)
    POST /panic       → mercy-kill every non-protected process > 200 MB +
                        fanfare + randomly-selected victory line
    POST /settings    → update voice pack / mute flags / API keys
    POST /say?text=…  → speak arbitrary text (for the voice-preview button)
    POST /open_activity_monitor  → launch Apple's Activity Monitor
"""
import http.server
import json
import os
import signal
import socketserver
import subprocess
import threading
import time
import urllib.parse

import psutil
from personas import persona_for, random_ambient, AMBIENT_LINES, PROCESS_PERSONAS
import voice_tts

PORT = 8765
ROOT = os.path.dirname(os.path.abspath(__file__))

PROTECTED_NAMES = {
    "kernel_task", "launchd", "WindowServer", "loginwindow", "mds", "mds_stores",
    "coreaudiod", "cfprefsd", "Dock", "Finder", "SystemUIServer", "ControlCenter",
    "Python", "python3.10", "python3",
}

PANIC_MIN_RSS = 200 * 1024 * 1024  # 200 MB

# Track every scheduled Timer so we can cancel ALL pending audio when the user
# picks a new voice mid-audition (or clicks stop).
_scheduled_timers: list[threading.Timer] = []


def schedule(delay_s: float, fn):
    """threading.Timer wrapper that tracks the handle so /stop_audio can cancel it."""
    t = threading.Timer(delay_s, fn)
    _scheduled_timers.append(t)
    t.start()
    return t


def cancel_all_scheduled():
    """Cancel every queued voice/sound firing and forget them."""
    global _scheduled_timers
    for t in _scheduled_timers:
        try: t.cancel()
        except Exception: pass
    _scheduled_timers = []


# ── Settings ─────────────────────────────────────────────────────────
class Settings:
    """Persisted to settings.json, loaded on boot."""
    tts_provider     = "auto"   # "auto" | "openai" | "elevenlabs" | "macos"
    openai_key       = ""       # paste in settings UI
    elevenlabs_key   = ""
    default_voice    = "fable"  # fallback voice if a persona has none
    sound_on         = True
    voice_on         = True
    quiet_hours      = False

    @classmethod
    def path(cls): return os.path.join(ROOT, "settings.json")

    @classmethod
    def load(cls):
        try:
            with open(cls.path(), "r") as f:
                data = json.load(f)
            for k, v in data.items():
                if hasattr(cls, k): setattr(cls, k, v)
        except Exception: pass

    @classmethod
    def save(cls):
        try:
            with open(cls.path(), "w") as f:
                json.dump({
                    "tts_provider":   cls.tts_provider,
                    "openai_key":     cls.openai_key,
                    "elevenlabs_key": cls.elevenlabs_key,
                    "default_voice":  cls.default_voice,
                    "sound_on":       cls.sound_on,
                    "voice_on":       cls.voice_on,
                    "quiet_hours":    cls.quiet_hours,
                }, f)
        except Exception: pass

    @classmethod
    def public(cls):
        """What's safe to return to the client (no API keys)."""
        return {
            "tts_provider":     cls.tts_provider,
            "default_voice":    cls.default_voice,
            "sound_on":         cls.sound_on,
            "voice_on":         cls.voice_on,
            "has_openai_key":   bool(cls.openai_key),
            "has_elevenlabs_key": bool(cls.elevenlabs_key),
        }


# ── Audio helpers ────────────────────────────────────────────────────
def play_sound(name: str):
    """Play a macOS system sound by short name or filename."""
    if not Settings.sound_on: return
    SOUND_MAP = {
        "coin":      "Pop.aiff",
        "fanfare":   "Hero.aiff",
        "victory":   "Hero.aiff",
        "ding":      "Glass.aiff",
        "error":     "Basso.aiff",
        "critical":  "Basso.aiff",
        "recovered": "Submarine.aiff",
        "sosumi":    "Sosumi.aiff",
        "funk":      "Funk.aiff",
        "tink":      "Tink.aiff",
    }
    fname = SOUND_MAP.get(name, name)
    path = os.path.join("/System/Library/Sounds", fname)
    if not os.path.exists(path): return
    subprocess.Popen(["afplay", path],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def speak(text: str, voice: str | None = None):
    """Speak text via configured AI voice (OpenAI/ElevenLabs) or macOS fallback."""
    if not Settings.voice_on or not text: return
    v = voice or Settings.default_voice
    voice_tts.speak(text, v, Settings)


# ── Ambient event detector ───────────────────────────────────────────
class Events:
    """Fires voice lines when RAM pressure changes — with cooldowns so we
    don't become a chatterbox during sustained high pressure."""
    last_pressure = "calm"
    last_fire = {}

    @classmethod
    def cooldown_ok(cls, name, seconds):
        t = time.time()
        if t - cls.last_fire.get(name, 0) < seconds: return False
        cls.last_fire[name] = t
        return True

    @classmethod
    def on_stats(cls, pressure):
        if pressure == "critical" and cls.last_pressure != "critical":
            if cls.cooldown_ok("critical", 180):
                play_sound("critical")
                voice, quip = random_ambient("critical")
                schedule(0.6, lambda: speak(quip, voice=voice))
        elif pressure == "high" and cls.last_pressure in ("calm", "warm"):
            if cls.cooldown_ok("warn", 300):
                voice, quip = random_ambient("warn")
                speak(quip, voice=voice)
        elif cls.last_pressure == "critical" and pressure in ("calm", "warm"):
            if cls.cooldown_ok("recover", 60):
                play_sound("recovered")
                voice, quip = random_ambient("recover")
                schedule(0.7, lambda: speak(quip, voice=voice))
        cls.last_pressure = pressure


# ── Snapshot ─────────────────────────────────────────────────────────
def snapshot():
    mem  = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage("/")
    cpu  = psutil.cpu_percent(interval=None)

    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent"]):
        try:
            mi = p.info["memory_info"]
            if mi is None: continue
            procs.append({
                "pid":  p.info["pid"],
                "name": p.info["name"] or "?",
                "rss":  mi.rss,
                "cpu":  p.info["cpu_percent"] or 0,
            })
        except Exception: pass
    procs.sort(key=lambda x: -x["rss"])

    pressure = pressure_label(mem.percent)
    Events.on_stats(pressure)

    return {
        "ram":  {"total": mem.total, "used": mem.used, "available": mem.available,
                 "percent": mem.percent, "pressure": pressure},
        "swap": {"total": swap.total, "used": swap.used, "percent": swap.percent},
        "disk": {"total": disk.total, "used": disk.used, "free": disk.free,
                 "percent": disk.percent},
        "cpu":  {"percent": cpu},
        "top":  procs[:20],
        "protected": list(PROTECTED_NAMES),
        "settings":  Settings.public(),
    }


def pressure_label(pct):
    if pct >= 90: return "critical"
    if pct >= 80: return "high"
    if pct >= 65: return "warm"
    return "calm"


# ── HTTP handler ─────────────────────────────────────────────────────
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def translate_path(self, path):
        p = super().translate_path(path)
        real = os.path.realpath(p)
        if not real.startswith(os.path.realpath(ROOT)):
            return os.path.join(ROOT, "index.html")
        return p

    def do_GET(self):
        route = urllib.parse.urlparse(self.path).path.rstrip("/")
        if route == "/stats":
            self._json(200, snapshot()); return
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path.rstrip("/")
        qs = urllib.parse.parse_qs(parsed.query)

        if route == "/kill":                   self._handle_kill(qs);      return
        if route == "/panic":                  self._handle_panic();       return
        if route == "/settings":               self._handle_settings();    return
        if route == "/say":                    self._handle_say(qs);       return
        if route == "/open_activity_monitor":  self._handle_open_am();     return
        if route == "/paste_key":              self._handle_paste_key(qs); return
        if route == "/audition":               self._handle_audition();    return
        if route == "/stop_audio":             self._handle_stop_audio();  return
        self.send_response(404); self.end_headers()

    def _handle_kill(self, qs):
        try: pid = int(qs.get("pid", [""])[0])
        except ValueError:
            self._json(400, {"ok": False, "error": "bad pid"}); return
        force = qs.get("force", ["0"])[0] == "1"
        drama = qs.get("drama", ["1"])[0] == "1"

        try:
            proc = psutil.Process(pid)
            name = proc.name() or "?"
            rss  = proc.memory_info().rss
        except Exception:
            self._json(404, {"ok": False, "error": "process not found"}); return
        if name in PROTECTED_NAMES:
            self._json(403, {"ok": False, "error": f"{name} is protected"}); return

        try:
            os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)
        except PermissionError:
            self._json(403, {"ok": False, "error": "permission denied"}); return
        except ProcessLookupError:
            self._json(404, {"ok": False, "error": "already gone"}); return
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)}); return

        if drama:
            play_sound("error" if force else "coin")
            if rss > 2 * 1024 * 1024 * 1024:  # >2 GB — big kill gets extra fanfare
                schedule(0.25, lambda: play_sound("fanfare"))
            voice, quip = persona_for(name)
            # Speak slightly after the sound so they don't overlap.
            schedule(0.55, lambda: speak(quip, voice=voice))

        self._json(200, {"ok": True, "pid": pid, "name": name,
                         "signal": "SIGKILL" if force else "SIGTERM"})

    def _handle_panic(self):
        killed, failed = [], []
        for p in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                info = p.info
                if info["memory_info"] is None: continue
                rss  = info["memory_info"].rss
                name = info["name"] or ""
                if rss < PANIC_MIN_RSS: continue
                if name in PROTECTED_NAMES: continue
                os.kill(info["pid"], signal.SIGTERM)
                killed.append({"pid": info["pid"], "name": name, "rss": rss})
            except Exception as e:
                failed.append({"pid": info.get("pid") if info else 0, "error": str(e)})

        play_sound("fanfare")
        voice, quip = random_ambient("panic")
        # Personalize the line with the actual count
        filled = quip.replace("many", str(len(killed))).replace("Eleven", str(len(killed)))
        schedule(1.1, lambda: speak(filled, voice=voice))
        self._json(200, {"ok": True, "killed": killed, "failed": failed})

    def _handle_settings(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode() if length else "{}"
        try: data = json.loads(body or "{}")
        except Exception:
            self._json(400, {"ok": False, "error": "bad json"}); return

        changed_keys = False
        for k in ("tts_provider", "default_voice", "sound_on", "voice_on", "quiet_hours"):
            if k in data: setattr(Settings, k, data[k]); changed_keys = True
        if "openai_key" in data:
            Settings.openai_key = data["openai_key"].strip()
            changed_keys = True
        if "elevenlabs_key" in data:
            Settings.elevenlabs_key = data["elevenlabs_key"].strip()
            changed_keys = True
        if changed_keys: Settings.save()

        # (voice-change preview is handled client-side so the character's
        # signature line plays instead of a generic one)

        self._json(200, {"ok": True, "settings": Settings.public()})

    def _handle_say(self, qs):
        text = qs.get("text", [""])[0]
        voice = qs.get("voice", [None])[0]
        if text: speak(text, voice=voice)
        self._json(200, {"ok": True})

    def _handle_open_am(self):
        try:
            subprocess.Popen(["open", "-a", "Activity Monitor"])
            self._json(200, {"ok": True})
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)})

    def _handle_stop_audio(self):
        """Cancel every queued voice line + kill anything currently playing.
        Called when the user picks a new voice so the old character stops mid-sentence."""
        cancel_all_scheduled()
        # kill anything already being played — afplay for sounds/MP3s, say for macOS fallback
        for name in ("afplay", "say"):
            try:
                subprocess.run(["pkill", "-x", name],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            except Exception: pass
        self._json(200, {"ok": True})

    def _handle_audition(self):
        """Play all 7 characters back-to-back — ~30 seconds total."""
        cast = [
            ("fable",   "Hello. I am Dame Agatha. One does NOT simply kill processes without consulting me. Pedestrian."),
            ("nova",    "Hey bestie! I'm Bestie. I say 'literally' like, literally ten times per sentence. It's toxic and I'm aware."),
            ("coral",   "HEY CHAMP I'M COACH CORAL AND EVERY PROCESS WE KILL IS A W FOR OUR JOURNEY! LET'S GO LET'S GO!"),
            ("echo",    "Ahhhh hell. Name's Ron. Uncle Ron. I'm already a lil drunk. Been at the bar since Tuesday. Damn."),
            ("onyx",    "I am CHEF FUCKING RAMSAY and your memory management is ABSOLUTE SHIT! You absolute COCK-WOMBLE!"),
            ("alloy",   "Hi there. I'm Karen. I'd love to get on a quick sync to discuss how your RAM is, frankly, concerning."),
            ("ash",     "Bro. Name's Chad. I roast you while I murder your apps. Daniel, you have thirty four Chrome tabs open right now. Embarrassing."),
            ("verse",   "OH HE'S HERE FOLKS! The name's Hype! I call every kill like it's SportsCenter! LET'S GET IT!"),
            ("ballad",  "Ay, my guy. Name's Mike. From Brooklyn. I close the apps, I make the coffee, I take the F train. Respect."),
        ]
        for i, (voice, text) in enumerate(cast):
            schedule(i * 4.5, lambda v=voice, t=text: speak(t, voice=v))

        self._json(200, {
            "ok": True,
            "played": len(cast),
            "estimated_duration_s": round(len(cast) * 4.5, 1),
            "cast": [{"voice": v, "line": l} for v, l in cast],
        })

    def _handle_paste_key(self, qs):
        """Read the system clipboard via pbpaste, save as the requested key field.
        Works around WKWebView-in-popover not allowing keyboard paste into inputs."""
        field = qs.get("field", ["openai_key"])[0]
        if field not in ("openai_key", "elevenlabs_key"):
            self._json(400, {"ok": False, "error": "invalid field"}); return
        try:
            result = subprocess.run(
                ["pbpaste"], capture_output=True, text=True, timeout=2)
            value = (result.stdout or "").strip()
        except Exception as e:
            self._json(500, {"ok": False, "error": f"pbpaste failed: {e}"}); return

        if not value:
            self._json(400, {"ok": False, "error": "clipboard is empty"}); return
        # Sanity check the format so we don't silently save garbage
        if field == "openai_key" and not value.startswith("sk-"):
            self._json(400, {"ok": False,
                "error": "Clipboard doesn't look like an OpenAI key (should start with 'sk-')"}); return
        if field == "elevenlabs_key" and len(value) < 20:
            self._json(400, {"ok": False,
                "error": "Clipboard doesn't look like an ElevenLabs key (too short)"}); return

        setattr(Settings, field, value)
        Settings.save()
        # Preview the new voice via AI TTS so the user immediately hears the upgrade
        if Settings.voice_on:
            schedule(0.1, lambda: speak(
                f"{field.replace('_key', '')} key saved. Hello from your new voice.",
                voice=Settings.default_voice)).start()
        # Don't return the key itself; just confirm it's set
        self._json(200, {
            "ok": True,
            "field": field,
            "length": len(value),
            "preview": value[:6] + "…" + value[-4:] if len(value) > 12 else "…",
            "settings": Settings.public()
        })

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def warm_cache_on_boot():
    """Pre-synthesize every persona + ambient line in the background so the
    first kill of each app plays with no latency."""
    if not (Settings.openai_key or Settings.elevenlabs_key): return
    lines = []
    # Top 20 most-likely killed personas (keep cache small at boot)
    for key, voice, quip in PROCESS_PERSONAS[:25]:
        lines.append((voice, quip))
    lines.extend(AMBIENT_LINES)
    voice_tts.warm_cache(lines, Settings)


class ReusingTCPServer(socketserver.TCPServer):
    """Allow rebind after crash/restart without waiting for TIME_WAIT."""
    allow_reuse_address = True


def main():
    Settings.load()
    warm_cache_on_boot()
    os.chdir(ROOT)
    with ReusingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"◆ Widget server: http://127.0.0.1:{PORT}/")
        print(f"  provider: {Settings.tts_provider}  ·  default voice: {Settings.default_voice}")
        print(f"  openai_key set: {bool(Settings.openai_key)}  ·  elevenlabs_key set: {bool(Settings.elevenlabs_key)}")
        try: httpd.serve_forever()
        except KeyboardInterrupt: print("\nbye")


if __name__ == "__main__":
    main()
