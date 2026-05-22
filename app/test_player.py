from player import generate_bars, PLAYLIST

def test_playlist_not_empty():
    assert len(PLAYLIST) > 0

def test_generate_bars_length():
    bars = generate_bars(bpm=128, tick=0.0, width=40)
    assert len(bars) == 40

def test_generate_bars_values():
    bars = generate_bars(bpm=128, tick=0.0, width=40)
    assert all(0.0 <= b <= 1.0 for b in bars)
