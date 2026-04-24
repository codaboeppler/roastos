# 🔥 RoastOS — like macOS, but it talks back

A macOS menu-bar RAM / CPU / disk widget **with 9 AI-voiced characters** who
roast you while you kill processes. Chef Ramsay yells profanity at Chrome.
Bestie tells you you're being toxic. Chad reads you for filth. It's a
system monitor that's also a stand-up set.

> *"Chrome dead. Finally. It was using RAM like your ex takes everything and
> leaves nothing. Daniel, grow a spine, king."* — **Chad**

> *"WHAT THE FUCK are you DOING?! Twenty four GIGABYTES for ONE file?! You
> absolute SHIT-TROMBONE!"* — **Chef Ramsay**

> *"Ay my guy. Chrome had eighty four helpers. In my day we had ONE browser.
> And you walked to get there."* — **Mike from Brooklyn**

---

## What it does

- **Menu-bar live stats** — free RAM + color-coded pressure dot (🟢 / 🟡 / 🔴)
- **Click the icon** → rich popover with memory cards, CPU history, top-8 process kill list
- **Kill any process** → plays a 🪙 coin sound + the app's persona speaks its dying words via AI voice
- **Panic button** — mass-kills every non-protected app >200 MB, plays fanfare
- **Ambient voice commentary** — characters react when RAM crosses thresholds
- **Full-web dashboard** at `http://127.0.0.1:8765/` with sortable process table + mini CPU graph
- **All native macOS** — runs as a LaunchAgent, survives restarts, no browser tab needed

## The cast

| Character | Voice | Vibe |
|---|---|---|
| 🎩 **Dame Agatha** | fable | Victorian aristocrat. *"One does NOT simply kill processes without consulting me."* |
| 👩 **Bestie** | nova | Gen-Z toxic bestie. *"No fr bestie, this is giving toxic."* |
| 📣 **Coach Coral** | coral | Delusionally positive cheerleader. Every kill is a W. |
| 🍺 **Uncle Ron** | echo | Drunk uncle at the barbecue. *"Been at the bar since Tuesday."* |
| 🍳 **Chef Ramsay** | onyx | Maximum profanity. *"You absolute COCK-WOMBLING FUCKWIT!"* |
| 💼 **Karen** | alloy | Corporate HR psychopath. *"Have you considered a more asynchronous approach?"* |
| 🦾 **Chad** | ash | Tech-bro menace. Roasts you by name. Crude as hell. |
| 📢 **Hype** | verse | Stadium announcer meets stand-up. *"OH HE DEAD HE DEAD HE DEAAAAD!"* |
| 🗽 **Mike from BK** | ballad | Jaded New Yorker. Bodega philosophy. Calls you "my guy." |

Each of the 9 characters has 10–20 app-specific quips (Chrome, Slack, Unity,
Photoshop, etc.) plus ambient lines for RAM crossings. ~150 voice lines total.

---

## Requirements

- **macOS** (tested on Apple Silicon; Intel should work)
- **Python 3.10+** via Homebrew: `brew install python@3.10`
- **ElevenLabs API key** (free tier works — 10K chars/month) OR **OpenAI API key**
  for AI voices. Without a key, falls back to macOS built-in `say` voices
  (works but sounds robotic).

---

## Install (5 minutes)

### 1. Clone + enter

```bash
git clone https://github.com/codaboeppler/roastos.git
cd roastos
```

### 2. Install dependencies

```bash
python3.10 -m pip install psutil rumps pyobjc-framework-WebKit
```

Optional (for transparent-background image generation / rembg features — not
strictly required for the widget):

```bash
python3.10 -m pip install "rembg[cpu]" pillow
```

### 3. Run the installer

```bash
chmod +x INSTALL.command
./INSTALL.command
```

This:
- Installs a LaunchAgent so the widget starts at login
- Starts the menu-bar app
- Starts the local HTTP server on `127.0.0.1:8765`
- Opens the dashboard in your browser

### 4. Add an API key (optional but recommended)

1. Click the menu-bar icon (top-right)
2. Click **⚙** to open settings
3. Copy your API key to clipboard (OpenAI or ElevenLabs)
4. Click **📋 paste OpenAI** or **📋 paste ElevenLabs**
5. Pick a character from the grid — they'll auto-preview in their voice

**Where to get keys:**
- OpenAI: <https://platform.openai.com/api-keys>
- ElevenLabs: <https://elevenlabs.io/app/api/api-keys>
  - Grant the key **Text to Speech: Access** + **Voices: Read**
  - Keep monthly credit limit at ~10K to bound your spend

---

## Cost

Runs entirely locally after setup. Your costs:

| Scenario | Cost |
|---|---|
| No API keys — macOS `say` fallback | **$0** |
| OpenAI TTS | ~$0.015 per 1,000 chars (~$1-3/month casual use) |
| ElevenLabs free tier | 10K chars/month included; enough for ~200 kills |
| ElevenLabs Starter | $5/month for 30K chars |

Every synthesized line is **cached to disk** (`voice_cache/`), so killing Chrome 50 times
costs one API call. First-week active use typically consumes ~3-5K chars total.

---

## How it works

```
┌─────────────────────┐         ┌──────────────────┐
│  menu_popover.py    │         │    server.py     │
│  (native NSStatus)  │◄───────►│    (HTTP API)    │
│  WKWebView inside   │         │    psutil        │
│  popover shows HTML │         │    TTS proxy     │
└──────────┬──────────┘         └────────┬─────────┘
           │                              │
           ▼                              ▼
    ┌──────────────┐            ┌────────────────┐
    │ popover.html │            │  personas.py   │
    │ cast cards   │            │  (9 characters,│
    │ + controls   │            │   150+ quips)  │
    └──────────────┘            └────────┬───────┘
                                         │
                                         ▼
                                ┌────────────────┐
                                │  voice_tts.py  │
                                │  OpenAI or     │
                                │  ElevenLabs    │
                                │  + mp3 cache   │
                                └────────────────┘
```

---

## File tour

```
roastos/
├── menubar_popover.py   # native AppKit menu bar + WKWebView
├── server.py            # local HTTP server (stats, kill, panic, say)
├── personas.py          # 9 characters, ~150 quips, ambient lines
├── voice_tts.py         # OpenAI + ElevenLabs + macOS fallback + caching
├── popover.html         # compact popover UI (character card grid)
├── index.html           # full browser dashboard
├── INSTALL.command      # one-click installer (LaunchAgent + launch)
└── settings.example.json  # copy to settings.json with your keys
```

---

## Uninstall

```bash
launchctl unload ~/Library/LaunchAgents/com.danielboeppler.roastos.plist
rm ~/Library/LaunchAgents/com.danielboeppler.roastos.plist
```

---

## Roadmap / ideas welcome

- [ ] Homebrew tap formula (`brew install system-widget`)
- [ ] Shared-cache CDN so new users get instant voice playback
- [ ] More characters (conspiracy uncle? radio DJ? HR therapy chatbot?)
- [ ] Keyboard shortcut to panic-kill
- [ ] Customizable thresholds per-voice
- [ ] Linux port (rumps → pystray, WKWebView → PyQt)

PRs welcome.

---

## Acknowledgments

- Voices by [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech) & [ElevenLabs](https://elevenlabs.io)
- Menu-bar magic via [rumps](https://github.com/jaredks/rumps) / [PyObjC](https://pyobjc.readthedocs.io)
- System stats via [psutil](https://github.com/giampaolo/psutil)
- macOS built-in sounds (Pop.aiff, Hero.aiff, Basso.aiff) — Apple Inc.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, sell it, whatever. Just don't blame me when Chef Ramsay makes your coworkers uncomfortable in the open office.

---

*Built while procrastinating on a Unity game. Sometimes the side quest is the whole quest.*
