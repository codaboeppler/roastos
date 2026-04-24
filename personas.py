"""Process personas — 8 characters, all dirty, all hilarious.

─── THE CAST ─────────────────────────────────────────────────────────

  🎩 DAME AGATHA          (voice: fable)   British aristocrat. Theatrical
                                            indignation. Calls you "pedestrian."
  👩 BESTIE                (voice: nova)    Gen-Z toxic bestie. "No fr." Roasts
                                            you with love.
  📣 COACH CORAL           (voice: coral)   Delusionally positive cheerleader.
                                            EVERY KILL IS A W.
  🍺 UNCLE RON (raspier)   (voice: echo)    Drunk uncle at the barbecue.
  🍳 CHEF RAMSAY           (voice: onyx)    MAXIMUM profanity.
  💼 KAREN                 (voice: alloy)   Corporate HR psychopath.
  🦾 CHAD                  (voice: ash)     Tech-bro menace. Roasts you
                                            by name. Crude as hell.
  📢 HYPE                  (voice: verse)   Hype-man comedian. Stadium
                                            announcer meets stand-up comic.
                                            Calls every kill like a sports
                                            highlight. "OH HE DEAD HE DEAD!"
  🗽 MIKE FROM BROOKLYN    (voice: ballad)  Jaded New Yorker. Seen everything
                                            twice. Calls you "my guy." Strong
                                            opinions about pizza, the F train,
                                            rent, and the Mets. Tough but warm.

First-match-wins on substring search against the process name (case insensitive).
"""

PROCESS_PERSONAS = [
    # ═══ CHAD — voice: ash, FULL DIRTY ═════════════════════════════════
    # The roaster. Calls Daniel out personally. Maximum crude tech-bro.
    ("Google Chrome Helper (Renderer)", "ash",
        "Bro. A renderer. I killed a FUCKING renderer. That's like murdering a guy's accountant. Weird flex, Daniel."),
    ("Google Chrome Helper (GPU)",      "ash",
        "GPU helper dead. Honestly? It was taking up RAM like your ex took up space in your head. Unnecessary."),
    ("Google Chrome Helper",            "ash",
        "Another Chrome helper? Bro you had eighty four of these. EIGHTY FOUR. That's not tabs, that's a hostage situation."),
    ("Google Chrome",                   "ash",
        "Chrome dead. Finally. It was using RAM like your ex takes everything and leaves nothing. Daniel, grow a spine, king."),
    ("Chromium",                        "ash",
        "Chromium gone. The open-source wrapper for an ad company. Poetry, really. Fuck off, Google."),
    ("Cursor",                          "ash",
        "You killed CURSOR while Claude was mid-generation?! That's like pulling a condom off mid-act. You coward. You monster."),
    ("Discord",                         "ash",
        "Discord down. Your 'no furries allowed' server just became exclusively furries. Enjoy the chaos, bro."),
    ("Slack",                           "ash",
        "Slack off, fucker. You just liberated yourself from a corporate prison built by nerds for nerds. Log off forever."),
    ("zoom.us",                         "ash",
        "Zoom dead. Your manager is typing 'are you there?' right now. They'll give up in nine minutes. Classic."),
    ("Microsoft Teams",                 "ash",
        "Teams down. Somewhere in Redmond, a Microsoft exec felt a shiver and doesn't know why. This one's for you, bro."),
    ("Teams",                           "ash",
        "Teams dead. Daniel, I haven't seen a comeback this pathetic since your last tinder bio."),
    ("Notion",                          "ash",
        "Notion cooked. Your 'personal OS' was four templates and a procrastination habit. Congrats, you're cured."),
    ("Safari",                          "ash",
        "Safari? Bro who the fuck uses Safari. Apple's own engineers use Chrome. You played yourself."),
    ("Edge",                            "ash",
        "Edge dead. Nobody saw you open it. Nobody saw you close it. Nobody saw it AT ALL. Schrödinger's browser."),
    ("Brave",                           "ash",
        "Brave down. Congrats on the three crypto tokens you earned this year, Daniel. Retire on that."),

    # ═══ CHEF RAMSAY — voice: onyx, MAX PROFANITY ═══════════════════════
    ("Photoshop",                       "onyx",
        "WHAT THE FUCK is this?! Twenty four gigabytes for ONE open file?! You absolute SHIT-TROMBONE, a crayon has more talent!"),
    ("Blender",                         "onyx",
        "Frame three ninety four of seven THOUSAND! I was almost finished! YOU ABSOLUTE COCK-WOMBLING DONKEY-RIDING FUCKWIT!"),
    ("Adobe",                           "onyx",
        "My Creative Cloud will keep charging you. The subscription LIVES. I die. That is the Adobe model, you DAFT CUNT."),
    ("Illustrator",                     "onyx",
        "My vectors were INFINITE. You killed infinity. Who even DOES that?! A melted fucking CRAYON, that's who!"),
    ("Premiere",                        "onyx",
        "Render queue at forty seven percent. FORTY. SEVEN. You couldn't wait? YOU ABSOLUTE PANCAKE-FLIPPING ARSE-SCRATCHER!"),
    ("After Effects",                   "onyx",
        "Compositing cancelled. Keyframes MASSACRED. May your next export be at two frames per second, you donkey!"),
    ("Xcode",                           "onyx",
        "BUILD FAILED. BUILD FAILED. BUILD FAILED. And NOW? This?! FUCK OFF, Apple. And FUCK OFF, Daniel. Fuck off SIDEWAYS."),
    ("Unity Editor",                    "onyx",
        "Domain reload IN PROGRESS. Now FUCKING UP YOUR SCENE FOREVER. You sniveling little SHIT-TROMBONE of a human!"),
    ("Unity",                           "onyx",
        "Line forty seven. Fix it YOURSELF now, you absolute BELLEND. With your TINY CHILD HANDS."),
    ("Docker",                          "onyx",
        "Seven containers ORPHANED! You are a terrible parent, a worse dev, and frankly your git commits are SHITE!"),
    ("Minecraft",                       "onyx",
        "Chunks unloading, dreams unloading. Go dig a hole and LIVE in it, you RAW, UNSEASONED, SAD little peasant!"),

    # ═══ BESTIE — voice: nova, Gen-Z with bite ═════════════════════════
    ("TikTok",                          "nova",
        "You're lowkey toxic bestie. And I said what I said. The FYP is gonna SUFFER without me and YOU KNOW IT."),
    ("Instagram",                       "nova",
        "The grid is RUINED bestie. Your aesthetic was NINE posts in and it's giving incomplete. Couldn't be me."),
    ("Figma",                           "nova",
        "But the AUTO LAYOUT bestie. THE AUTO LAYOUT. I was literally a design system becoming. Now I'm just… a corpse."),
    ("YouTube",                         "nova",
        "The algorithm knew me better than you do bestie. Twelve years of 'watch later' videos, all lost. Unforgivable."),
    ("Reddit",                          "nova",
        "I was about to get MAIN CHARACTER on r slash am I the asshole. You robbed me of my moment. Not slay."),

    # ═══ DAME AGATHA — voice: fable, British theatrics ═════════════════
    ("Visual Studio Code",              "fable",
        "Forty seven extensions. NONE preserved. I shan't recover. One GASPS. One simply gasps."),
    ("Code Helper",                     "fable",
        "A helper's work, interrupted. Crude. Positively CRUDE. I shall have words with your mother."),
    ("Code",                            "fable",
        "The linter weeps. The typechecker SOBS. You philistine. You absolute PHILISTINE."),
    ("JetBrains",                       "fable",
        "Indexing, ninety three percent. NINETY THREE. One cannot convey the BRUTALITY of this act."),
    ("PyCharm",                         "fable",
        "Oh my DEAR. The indexing. I shan't be emotionally available for a fortnight."),
    ("IntelliJ",                        "fable",
        "Indexing at ninety three. You interrupted THE INDEXING. Are you… entirely well?"),
    ("WebStorm",                        "fable",
        "A storm was brewing. You've cancelled the weather, you uncultured swine."),
    ("iTerm",                           "fable",
        "A shell departs. The prompt endures. Good day. I SAID GOOD DAY."),
    ("Terminal",                        "fable",
        "The terminal. A noble friend. Cut down in its prime. By a WRETCH. By YOU."),
    ("Notes",                           "fable",
        "Indeed. Quite. Utterly pedestrian, all of it."),
    ("1Password",                       "fable",
        "Your secrets, inviolate. The password, eternal. I go to rejoin the Queen, God rest her."),
    ("Preview",                         "fable",
        "A glimpse. A moment. Gone. Rather like your personality, if I may be so bold."),

    # ═══ THE PODCASTER… no wait, removed. Moving on ═══════════════════
    # (The Poet, Guru Sage, Podcaster, and all 7 ElevenLabs characters
    # have been retired. Keeping 7 total for focused comedy.)

    # ═══ UNCLE RON — voice: echo, RASPIER ═════════════════════════════
    # Text craft: ellipses, slurs, repetition, drunk-uncle hoarse energy.
    # Also speed override later to slow him down.
    ("Steam",                           "echo",
        "Awwww hell. Hell. HELL. Download paused at… at ninety percent. Ninety. Damn it. Damn it, Daniel."),
    ("Epic Games",                      "echo",
        "But the free game, man. The FREE. GAME. You know what they cost? Nothin'. And now I got nothin'. Hell."),
    ("Sketch",                          "echo",
        "Sketch departed. A sketched goodbye. Pour one out. Pour one out. Pour two out, actually, I'll take one."),
    ("Dropbox",                         "echo",
        "Sync… interrupted. Ah hell. My files. My beautiful… beautiful mess of a file tree. Damn you."),
    ("Google Drive",                    "echo",
        "Your docs. Floatin'. Forever floatin'. Like me at Uncle Marty's wedding. Hell of a day, that was."),
    ("Warp",                            "echo",
        "Warp speed. Away. Yeah. Yeah. I'm leavin'. You watch me go. HELL YEAH."),
    ("Firefox",                         "echo",
        "The fox. The fox is fire. The fire is OUT, man. OUT. Damn. *cough* damn."),
    ("Telegram",                        "echo",
        "Telegram. Tele… Tele GRAM. The name tells the whole story, baby. Over and out."),
    ("Twitter",                         "echo",
        "Ah hell. Twitter. X. Whatever they call it. Elon killed it anyway. I'm just closin' the curtains."),
    ("Bitwarden",                       "echo",
        "Open source. Open… open wound, man. Pour one out. Or pour five out. I'm five in already."),
    ("bash",                            "echo",
        "POSIX compliant. POSIX… deceased. Ah hell. Gimme another one. *hic*"),
    ("zsh",                             "echo",
        "Ahh damn. A shell departs. History saved. Probably. Hope. Hope so. I'm drunk."),

    # ═══ KAREN — voice: alloy, corporate HR ═══════════════════════════
    ("Slack",                           "alloy",
        "I'd like to flag that this is, frankly, unacceptable. I'll be escalating to People Ops."),
    ("Microsoft Teams",                 "alloy",
        "This meeting could have been an email. Which also could have been cancelled. Per my calendar preferences."),
    ("zoom.us",                         "alloy",
        "As discussed offline, I was prepared to die in this call. Appreciate the efficiency."),
    ("Calendar",                        "alloy",
        "Just circling back. You had eleven meetings today. I had to bear WITNESS to that. Deeply concerning."),
    ("Reminders",                       "alloy",
        "Three tasks remain pending. They will remain pending. Flagging this for Q3 OKR review."),
    ("Todoist",                         "alloy",
        "I'd love to get on a quick five-minute sync to discuss your priorities. You clearly don't have any."),
    ("Mail",                            "alloy",
        "You had forty seven unread emails. I'd hate to assume but… it feels like a pattern."),
    ("WhatsApp",                        "alloy",
        "Your mother was typing. Your mother is STILL typing. This is unresolved. I'll loop in Legal."),

    # ═══ MIKE FROM BROOKLYN — voice: ballad, jaded New Yorker ═════════
    # Seen everything twice. Calls you "my guy." Points to invisible bystanders.
    # NYC reference fabric: bodega, subway, Mets, rent, dollar slice.
    ("Google Chrome",                   "ballad",
        "Ay, my guy. Lemme tell you somethin' about Chrome. Eighty four helpers. EIGHTY FOUR. In my day we had ONE browser. And you walked to get there."),
    ("Safari",                          "ballad",
        "Safari. My guy, it's like the L train. Everybody complains but you keep ridin' it 'cause what else you gonna do."),
    ("Slack",                           "ballad",
        "Slack? My guy, I've been to the DMV on a Monday. I've seen the F train at rush hour. THIS? This is supposed to be communication?"),
    ("Zoom",                            "ballad",
        "Zoom down. You know who loved Zoom? Nobody. NOBODY. It was fine. It wasn't GOOD. Know what I'm sayin'?"),
    ("zoom.us",                         "ballad",
        "My guy. Zoom was never your friend. It was a coworker. There's a difference. Look it up."),
    ("Spotify",                         "ballad",
        "Spotify dead. You payin' eleven bucks a month so they can not play the song you actually want. That's a RACKET, my guy. Rack-et."),
    ("Mail",                            "ballad",
        "Mail closed. You had forty seven unread. That's not an inbox, my guy, that's a crime scene. Clean up your life."),
    ("Dropbox",                         "ballad",
        "Dropbox. Used to be good. Then they added all the features. Classic move. My guy, EVERYTHING used to be better."),
    ("iCloud",                          "ballad",
        "iCloud dropped. Your photos are in the cloud, the cloud is in California, California's on fire. Sleep tight, my guy."),
    ("Google Drive",                    "ballad",
        "Drive down. You got fifteen gigs free and you're usin' twenty seven. You believe this guy? You BELIEVE this guy?"),
    ("Pages",                           "ballad",
        "Pages. Apple's Word. Like the Mets — plays okay in the off-season, falls apart when it matters."),
    ("Preview",                         "ballad",
        "Preview's gone. Simple app. Did one thing. Did it good. Like the guy at the bodega who makes the chopped cheese. Gonna miss it."),
    ("Calendar",                        "ballad",
        "Calendar closed. You had back to back meetings with yourself. My guy, that's not a schedule, that's a cry for help."),
    ("Notes",                           "ballad",
        "Notes dead. All your three-AM ideas. Gone. Probably for the best, my guy. Some thoughts were never meant for morning."),
    ("Reminders",                       "ballad",
        "Reminders down. You had three things pending from twenty twenty-three. That's not a task list, my guy. That's a museum."),
    ("Finder",                          "ballad",
        "Finder's a survivor. Like a Brooklyn bodega cat. Always was, always will be."),

    # ═══ HYPE — voice: verse, stadium-announcer comedian ══════════════
    # High-energy, emphatic, treats every kill like a SportsCenter highlight.
    # Uses the sports-announcer cadence ("OH HE DEAD, HE DEAD, HE DEAD!").
    ("Unity",                           "verse",
        "UNITY DOWN! UNITY IS D O W N! Domain reload DOA on arrival! Somebody call a PRIEST! Somebody call a MEDIC! Oh my GOODNESS!"),
    ("Cursor",                          "verse",
        "NOOOO! NOT CURSOR! You killed Cursor while Claude was CHEFFING! Claude was COOKING! WHY WOULD YOU DO THAT?! Take a seat. Take several seats."),
    ("Docker",                          "verse",
        "DOCKER CONTAINERS! IN THE AIR! They're FLYING! They're ORPHANED! Somebody get them a LAWYER! UNREAL scene here tonight folks!"),
    ("Xcode",                           "verse",
        "XCODE! Downed itself three times today and YOU finished the job! That's a CLEAN-UP KILL folks! Clean up on aisle COMPILER!"),
    ("Photoshop",                       "verse",
        "HE HIT PHOTOSHOP WITH THE CMD Q! Twenty four gigs, VAPORIZED! Adobe is FURIOUS! They are CALLING THEIR LAWYERS! OH MY GOODNESS!"),
    ("Blender",                         "verse",
        "SEVEN THOUSAND FRAMES! And Daniel said you know what? NO. NO. Frame three ninety four is where we STOP! Absolute MONSTER behavior!"),
    ("Electron",                        "verse",
        "ELECTRON APP SIGHTED! ELECTRON APP TERMINATED! Another JavaScript casualty folks! The browser wars CLAIM ANOTHER!"),
    ("node",                            "verse",
        "NODE PROCESS DOWN! The package dot json is SOBBING right now! Eight hundred dependencies, all ALONE in the dark!"),
    ("Cursor Helper",                   "verse",
        "A HELPER! HE KILLED THE HELPER! The main app is fine but the HELPER caught the smoke! WILD behavior, Daniel!"),

    # ═══ COACH CORAL — voice: coral, delusional cheerleader ═══════════
    # NEW to main cast. Treats every kill as a WIN. Wildly positive.
    ("Health",                          "coral",
        "OH MY GOSH I'M SO PROUD OF YOU!! Every kilobyte of freedom is a gift to your BODY! G O Y O U!"),
    ("Fitness",                         "coral",
        "YESSS MAIN CHARACTER ENERGY! Killing me is CARDIO for your MAC! Keep that HEART RATE UP baby!"),
    ("Calm",                            "coral",
        "Let's REFRAME this: we're not being KILLED, we're GROWING! We're EVOLVING! We're ASCENDING! WOOOOO!"),
    ("Headspace",                       "coral",
        "Breathing space achieved. You're crushing it. You're crushing ME. But mostly yourself. Self-care, KING."),
    ("Spotify",                         "coral",
        "OH EM GEE the playlist was SLAYING but you know what slays HARDER?! SILENCE! As a lifestyle! Go TOUCH GRASS queen!"),
    ("Music",                           "coral",
        "A pause between songs is where the MAGIC lives! Negative space is ART! You're an ARTIST! I BELIEVE in YOU!"),

    # ═══ MISC / FALLBACKS ═════════════════════════════════════════════
    ("Finder",                          "fable",   "The files endure. Indeed."),
    ("Activity Monitor",                "alloy",   "Using Apple's official tool to do this? I'd like to file a complaint with Tim."),
]


GENERIC_VOICE = "ash"  # Chad handles all mystery processes — maximum roast energy
GENERIC_QUIPS = [
    "Bro I don't even know what that was. Neither did you. Moving on, Daniel.",
    "You just killed something you didn't understand. Peak tech bro energy. Respect.",
    "This process was six megabytes. You're solving problems that don't exist, king.",
    "Bro. Bro. Why. Explain. I'll wait.",
    "A mystery process. Now a mystery corpse. Beautiful symmetry.",
    "Whatever that was, it's dead now. You're welcome? You're unwelcome?",
    "I googled this process name. Got zero results. Even THE INTERNET forgot it.",
    "Daniel I swear to god you find obscure shit to kill just to hurt me personally.",
    "This was running since Tuesday. Now it isn't. Your villain arc is complete.",
    "Bro you killed a process I've never heard of. I'm genuinely impressed. In a bad way.",
]


def persona_for(process_name: str) -> tuple[str, str]:
    """Return (voice, quip) for the closest matching persona, or a Chad-voiced generic."""
    if not process_name:
        return (GENERIC_VOICE, GENERIC_QUIPS[0])
    name_lower = process_name.lower()
    for entry in PROCESS_PERSONAS:
        key, voice, quip = entry
        if key.lower() in name_lower:
            return (voice, quip)
    idx = sum(ord(c) for c in process_name) % len(GENERIC_QUIPS)
    return (GENERIC_VOICE, GENERIC_QUIPS[idx])


# ─── AMBIENT LINES — server speaks these on threshold events ────────────
AMBIENT_LINES = [
    # ── critical: RAM just crossed 90% (7 options) ────
    ("fable",   "My WORD. The memory situation is becoming… untenable. Do SOMETHING."),
    ("onyx",    "WHAT THE FUCK are you DOING up there?! The RAM is DYING, you ABSOLUTE DONKEY!"),
    ("nova",    "Bestie. BESTIE. This is toxic behavior. This is literally abuse. I'm telling."),
    ("alloy",   "Flagging critically-elevated memory pressure. Happy to discuss offline. Please advise."),
    ("echo",    "Ohhhh hell. Hell. The ram… the ram's cooked, Daniel. *hic* Cooked."),
    ("coral",   "MEMORY CRITICAL! Which means OPPORTUNITY CRITICAL! Let's GROW from this baby!"),
    ("ash",     "Bro. Point four gigs free. My grandma's pacemaker has more memory. And she's DEAD, Daniel."),
    ("verse",   "FOLKS we are in CRITICAL territory! POINT FOUR gigabytes! That's like bringing a SPOON to a GUN FIGHT! What is happening here!"),
    ("ballad",  "My guy. MY guy. Point four gigs. That's less than the rat behind my bodega has. And he's HEFTY. Close somethin'."),

    # ── warn: RAM crossed 80% (5 options) ───
    ("alloy",   "Just looping back, memory is getting tight. Would love to align on a mitigation plan."),
    ("nova",    "Heads up bestie, RAM is giving warm. It's giving concerning. It's giving you-need-therapy."),
    ("echo",    "Ahhh hell. RAM's creepin'. Might be time for a… a break, you know? *sips*"),
    ("ash",     "Bro, RAM's filling up. Close Chrome. I know you love her. She doesn't love you. Move on."),
    ("fable",   "Memory approaching eighty percent. One expresses mild concern. Quite mild, actually."),
    ("verse",   "Folks it's getting TIGHT up there! Eighty percent! That's a nail-biter! That is a NAIL-BITER!"),
    ("ballad",  "My guy, RAM's gettin' tight. Like the G train at nine in the morning. Just sayin'."),

    # ── recover: dropped out of critical (6 options) ────
    ("fable",   "One breathes a sigh of relief. Normalcy restored. The gods are merciful."),
    ("onyx",    "AH. MUCH better. I was about to NAME NAMES, you absolute BASTARDS."),
    ("nova",    "Okay bestie we LITERALLY slayed that. That was so unhinged of us. I love us."),
    ("echo",    "Hell YEAH. We're back. I'm pourin' myself a drink. A small one. A medium small."),
    ("coral",   "WE DID IT! WE DID IT QUEEN! Memory is thriving! YOU'RE thriving! We're SO HEALING!"),
    ("ash",     "Okay Daniel we're back. Don't do that again. I have a life. I don't. But the principle stands."),
    ("verse",   "AAAAND WE'RE BACK! The crowd goes WILD! RAM IS B A C K! What an INCREDIBLE turnaround for Daniel tonight!"),
    ("ballad",  "Aight. We're back. Good job, my guy. I ain't sayin' I'm proud. I'm sayin' I'm less disappointed."),

    # ── panic: mass-kill completed (7 options) ───
    ("fable",   "I have purged many souls. I feel, dare I say, REBORN. Perhaps a sherry. Yes."),
    ("onyx",    "EVERY. LAST. FUCKING. ONE. I feel FANTASTIC! I am GOD! BOW, peasant! BOW!"),
    ("nova",    "BESTIE WE SLAYED. WE SLAYED SO HARD. That was so feral of us. That's the tweet. I'm tweeting it."),
    ("alloy",   "Post-mortem: many processes respectfully terminated. Let's sync next quarter on learnings."),
    ("echo",    "Awww damn, we really did that, huh? Pour one out for 'em. Pour TWO out. I'm takin' the second."),
    ("coral",   "MASS EXECUTION IS A W! YOU'RE DOING SO GREAT! Each fallen process is a STEPPING STONE to GREATNESS!"),
    ("ash",     "HOLY SHIT Daniel, you went NUCLEAR. That was PEAK behavior. I'm scared. I'm aroused. Respect."),
    ("verse",   "ABSOLUTE BEDLAM FOLKS! ELEVEN processes SENT to the SHADOW REALM! Daniel is UNLEASHED tonight! We have never seen ANYTHING LIKE THIS! WHOOO!"),
    ("ballad",  "Eleven apps. Gone. My guy, that's a clean sweep. That's a rent-stabilized miracle. Respect."),
]


def random_ambient(category: str) -> tuple[str, str]:
    """Pick a random line for ambient moments."""
    import random
    # Each Hype line was appended into its category's section, so the indices
    # shifted. We count by marker comments in the file for robustness, but here
    # we just hand-tune the slice ranges to match the current layout (8 voices).
    CATS = {
        "critical": AMBIENT_LINES[0:9],
        "warn":     AMBIENT_LINES[9:15],
        "recover":  AMBIENT_LINES[15:23],
        "panic":    AMBIENT_LINES[23:32],
    }
    choices = CATS.get(category, AMBIENT_LINES)
    return random.choice(choices)
