import time
import math
import os
import sys
import redis
from prometheus_client import Counter, Gauge, start_http_server

SONGS_PLAYED = Counter(
    "player_songs_played_total",
    "Nombre total de chansons jouées"
)

CURRENT_BPM = Gauge(
    "player_current_bpm",
    "BPM de la chanson en cours"
)

ERRORS = Counter(
    "player_errors_total",
    "Nombre total d'erreurs"
)

def get_redis():
    try:
        r = redis.Redis(host="redis", port=6379, decode_responses=True)
        r.ping()
        return r
    except Exception:
        ERRORS.inc()
        return None

BARS   = " ▁▂▃▄▅▆▇█"
COLORS = {
    "purple": "\033[95m",
    "cyan":   "\033[96m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
}

def c(name, text):
    return f"{COLORS[name]}{text}{COLORS['reset']}"

PLAYLIST = [
    {"title": "Midnight Vibes",    "artist": "The Daemons",    "bpm": 128, "color": "purple"},
    {"title": "Kernel Panic",      "artist": "Stack Overflow", "bpm": 140, "color": "cyan"},
    {"title": "Heap of Love",      "artist": "Memory Leaks",   "bpm": 98,  "color": "green"},
    {"title": "sudo make music",   "artist": "Root Access",    "bpm": 160, "color": "yellow"},
]

def generate_bars(bpm, tick, width=40):
    bars = []
    beat_phase = (tick * bpm / 60) % 1.0
    for i in range(width):
        freq1 = math.sin(tick * 3.0 + i * 0.4) * 0.4
        freq2 = math.sin(tick * 7.0 + i * 0.9) * 0.25
        freq3 = math.sin(tick * 1.5 + i * 0.15) * 0.35
        kick  = math.exp(-((beat_phase) ** 2) / 0.01) * 0.8 if i < 8 else 0
        env   = 0.9 - (i / width) * 0.5
        raw   = (freq1 + freq2 + freq3 + kick) * env
        amp   = max(0.05, min(0.99, (raw + 1.0) / 2.0))
        bars.append(amp)
    return bars

def render_visualizer(bars, color):
    return "".join(c(color, BARS[int(a * (len(BARS) - 1))]) for a in bars)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def render_player(track, elapsed, duration=30):
    bars     = generate_bars(track["bpm"], elapsed)
    progress = min(elapsed / duration, 1.0)
    filled   = int(progress * 38)
    prog_bar = "█" * filled + "░" * (38 - filled)
    mins, secs = int(elapsed) // 60, int(elapsed) % 60

    clear()
    print()
    print(c("bold", "  ♪  ASCII MUSIC PLAYER"))
    print(c("dim",  "  ──────────────────────────────────────"))
    print()
    print(f"  {c('bold', track['title'])}")
    print(f"  {c('dim', track['artist'])}  {c('dim', str(track['bpm']) + ' BPM')}")
    print()
    print(f"  {render_visualizer(bars, track['color'])}")
    print(f"  {render_visualizer(bars[2:] + bars[:2], track['color'])}")
    print()
    print(f"  {c(track['color'], prog_bar)}")
    print(f"  {c('dim', f'{mins:02d}:{secs:02d}')}  {c('dim', '00:30')}")
    print()
    print(c("dim", "  Entrée = suivant   ctrl+c = quitter"))

def main():
    start_http_server(8000)
    r = get_redis()
    idx = int(r.get("current_track") or 0) if r else 0
    try:
        while True:
            track = PLAYLIST[idx]
            SONGS_PLAYED.inc()
            CURRENT_BPM.set(track["bpm"])
            start = time.time()
            while True:
                elapsed = time.time() - start
                if elapsed >= 30:
                    break
                render_player(track, elapsed)
                time.sleep(0.08)
            idx = (idx + 1) % len(PLAYLIST)
            if r:
                r.set("current_track", idx)
    except KeyboardInterrupt:
        clear()
        print(c("purple", "\n  À bientôt ♪\n"))

if __name__ == "__main__":
    main()