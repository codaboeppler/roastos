"""AI voice synthesis with caching.

Priorities, in order:
    1. OpenAI TTS (if OPENAI_API_KEY set)  → 6 natural neural voices, ~$0.015/1K chars
    2. ElevenLabs   (if ELEVENLABS_API_KEY set)  → character voices, free tier 10K chars/mo
    3. macOS `say`  (always available)  → built-in voices, zero cost

Every synthesized line is cached to voice_cache/<hash>.mp3 so we only hit the
API once per (voice, text) combo — killing Chrome 50 times costs 1 API call.
"""
import hashlib
import json
import os
import subprocess
import threading
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(ROOT, "voice_cache")

# ── Voice catalog ────────────────────────────────────────────────────
# OpenAI TTS voices — include newer voices (ash, ballad, coral, sage, verse)
# which tts-1-hd accepts for more variety.
OPENAI_VOICES = {
    "alloy":   "neutral narrator",
    "echo":    "warm male",
    "fable":   "British male",
    "onyx":    "deep male",
    "nova":    "bright female",
    "shimmer": "soft female (ASMR replacement)",
    "ash":     "confident tech-bro",
    "ballad":  "smooth male narrator",
    "coral":   "bright warm female",
    "sage":    "calm thoughtful male",
    "verse":   "conversational male",
}

# ElevenLabs voice IDs — using ONLY premade voices that work on the free tier.
# (Library voices like the original "Rachel 21m00T..." require a paid plan.)
# Mapped by OpenAI voice name so when a user is on ElevenLabs provider, picking
# our character voices ("fable" for Dame Agatha, etc.) routes to the best-fit
# premade ElevenLabs voice that actually has the right vibe.
ELEVENLABS_VOICES = {
    # character-fit mappings from OpenAI voice names → ElevenLabs premade IDs
    "fable":   "JBFqnCBsd6RMkjVDRZzb",  # George — warm storyteller (Dame Agatha)
    "nova":    "cgSgspJ2msm6clMCkdW9",  # Jessica — playful, bright (Bestie)
    "coral":   "FGY2WhTYpPnrIDTdsKH5",  # Laura — enthusiast (Coach Coral)
    "echo":    "N2lVS1w4EtoT3dr4eOWO",  # Callum — husky trickster (Uncle Ron)
    "onyx":    "SOYHLrjzK2X1ezoPC6cr",  # Harry — fierce warrior (Chef Ramsay)
    "alloy":   "XrExE9yKIg1WjnnlVkGX",  # Matilda — professional (Karen)
    "ash":     "TX3LPaxmHKxFdv7VOQHJ",  # Liam — social media creator (Chad)
    "verse":   "CwhRBWXzGAHq8TQ4Fs17",  # Roger — laid-back, resonant (Hype)
    "ballad":  "cjVigY5qzO86Huf0OWal",  # Eric — smooth, trustworthy (Mike from Brooklyn)

    # also accept ElevenLabs voice names directly (all premade, all free)
    "roger":    "CwhRBWXzGAHq8TQ4Fs17",  # Laid-Back, Casual, Resonant
    "sarah":    "EXAVITQu4vr4xnSDxMaL",  # Mature, Reassuring, Confident
    "laura":    "FGY2WhTYpPnrIDTdsKH5",  # Enthusiast, Quirky Attitude
    "charlie":  "IKne3meq5aSn9XLyUdCD",  # Deep, Confident, Energetic
    "george":   "JBFqnCBsd6RMkjVDRZzb",  # Warm, Captivating Storyteller
    "callum":   "N2lVS1w4EtoT3dr4eOWO",  # Husky Trickster
    "river":    "SAz9YHcvj6GT2YYXdXww",  # Relaxed, Neutral, Informative
    "harry":    "SOYHLrjzK2X1ezoPC6cr",  # Fierce Warrior
    "liam":     "TX3LPaxmHKxFdv7VOQHJ",  # Energetic, Social Media Creator
    "alice":    "Xb7hH8MSUJpSbSDYk0k2",  # Clear, Engaging Educator
    "matilda":  "XrExE9yKIg1WjnnlVkGX",  # Knowledgable, Professional
    "will":     "bIHbv24MWmeRgasZH58o",  # Relaxed Optimist
    "jessica":  "cgSgspJ2msm6clMCkdW9",  # Playful, Bright, Warm
    "eric":     "cjVigY5qzO86Huf0OWal",  # Smooth, Trustworthy
}


def _cache_path(provider: str, voice: str, text: str) -> str:
    key = hashlib.md5(f"{provider}|{voice}|{text}".encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{key}.mp3")


# ── OpenAI TTS ────────────────────────────────────────────────────────
def synthesize_openai(text: str, voice: str, api_key: str) -> str | None:
    """Returns path to cached MP3, or None on failure."""
    voice = voice if voice in OPENAI_VOICES else "nova"
    path = _cache_path("openai", voice, text)
    if os.path.exists(path):
        return path
    # tts-1-hd supports ALL voices (including ash/verse/etc); tts-1 is the older,
    # faster 6-voice model. Use hd when a newer voice is requested.
    newer_voices = {"ash", "ballad", "coral", "sage", "verse"}
    model = "tts-1-hd" if voice in newer_voices else "tts-1"
    # Per-voice speed tuning — slower for drunk/theatrical, faster for manic.
    # 0.85 is the lowest we go (below that = unintelligible slurring).
    VOICE_SPEED = {
        "echo":    0.88,   # Uncle Ron — drunk drawl
        "onyx":    1.10,   # Chef Ramsay — manic shouting
        "ash":     1.10,   # Chad — punchy roast energy
        "nova":    1.08,   # Bestie — fast gen-z cadence
        "alloy":   0.98,   # Karen — deliberate corporate pace
        "fable":   0.95,   # Dame Agatha — theatrical drawn-out
        "shimmer": 0.90,   # (unused)
        "coral":   1.08,   # Coach Coral — excitable
        "verse":   1.10,   # Hype — sports-announcer urgency
        "ballad":  0.95,   # Mike from Brooklyn — casual Jaded drawl
    }
    speed = VOICE_SPEED.get(voice, 1.05)
    try:
        body = json.dumps({
            "model": model,
            "voice": voice,
            "input": text,
            "response_format": "mp3",
            "speed": speed,
        }).encode("utf-8")
        req = Request(
            "https://api.openai.com/v1/audio/speech",
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        resp = urlopen(req, timeout=15)
        data = resp.read()
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path
    except (HTTPError, URLError, Exception) as e:
        print(f"[tts] OpenAI synth failed: {e}")
        return None


# ── ElevenLabs TTS ────────────────────────────────────────────────────
def synthesize_elevenlabs(text: str, voice: str, api_key: str) -> str | None:
    voice_id = ELEVENLABS_VOICES.get(voice.lower())
    if not voice_id:
        voice_id = ELEVENLABS_VOICES["rachel"]
        voice = "rachel"
    path = _cache_path("elevenlabs", voice, text)
    if os.path.exists(path):
        return path
    try:
        body = json.dumps({
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }).encode("utf-8")
        req = Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            data=body,
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
        )
        resp = urlopen(req, timeout=15)
        data = resp.read()
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception as e:
        print(f"[tts] ElevenLabs synth failed: {e}")
        return None


# ── Playback ─────────────────────────────────────────────────────────
def play_file(path: str):
    """Fire-and-forget audio playback via afplay."""
    subprocess.Popen(
        ["afplay", path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def speak_fallback_say(text: str, voice: str):
    """Last-resort macOS `say` — used when no API key is configured OR a request fails."""
    # Map "AI voice" names (e.g. 'nova', 'fable') to best-match macOS voices.
    MAP = {
        "alloy":   "Samantha",
        "echo":    "Alex",
        "fable":   "Daniel",
        "onyx":    "Fred",
        "nova":    "Kathy",
        "shimmer": "Whisper",
        "rachel":  "Samantha",
        "domi":    "Karen",
        "bella":   "Kathy",
        "antoni":  "Alex",
        "elli":    "Samantha",
        "josh":    "Fred",
        "adam":    "Daniel",
        "sam":     "Fred",
    }
    v = MAP.get(voice.lower(), voice)
    subprocess.Popen(
        ["say", "-v", v, text],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


# ── Public entry point ───────────────────────────────────────────────
def speak(text: str, voice: str, settings) -> str:
    """Speak text in the best available voice. Returns the provider used."""
    if not text: return "none"
    provider = (settings.tts_provider or "auto").lower()

    if provider in ("auto", "openai") and settings.openai_key:
        path = synthesize_openai(text, voice, settings.openai_key)
        if path:
            play_file(path)
            return "openai"

    if provider in ("auto", "elevenlabs") and settings.elevenlabs_key:
        path = synthesize_elevenlabs(text, voice, settings.elevenlabs_key)
        if path:
            play_file(path)
            return "elevenlabs"

    # Fallback — always works
    speak_fallback_say(text, voice)
    return "macos"


def warm_cache(lines: list[tuple[str, str]], settings):
    """Pre-synthesize a batch of (voice, text) pairs in background threads.
    Call once at startup to eliminate first-play latency for common quips."""
    def _go():
        for voice, text in lines:
            provider = (settings.tts_provider or "auto").lower()
            if provider in ("auto", "openai") and settings.openai_key:
                synthesize_openai(text, voice, settings.openai_key)
            elif provider in ("auto", "elevenlabs") and settings.elevenlabs_key:
                synthesize_elevenlabs(text, voice, settings.elevenlabs_key)
    threading.Thread(target=_go, daemon=True).start()
