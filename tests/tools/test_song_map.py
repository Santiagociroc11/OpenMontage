"""song_map must recover a known tempo, downbeat phase and drop.

The fixture is synthesized, so the ground truth is exact: 120 BPM, 4/4, a
kick on every downbeat (beat 1) and a quiet-loud-quiet energy shape whose
drop lands on a bar line.
"""

import wave

import numpy as np
import pytest

pytest.importorskip("librosa")

from tools.analysis.song_map import SongMap

SR = 22050
BPM = 120
BEAT = 60 / BPM
# (bars, gain): quiet intro, loud drop, quiet outro.
SHAPE = [(8, 0.15), (8, 1.0), (4, 0.15)]
DROP_AT = 8 * 4 * BEAT  # 16.0 s


def _hit(freq: float, dur: float, decay: float) -> np.ndarray:
    t = np.arange(int(SR * dur)) / SR
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * decay)


@pytest.fixture(scope="module")
def track(tmp_path_factory) -> str:
    total_beats = sum(b for b, _ in SHAPE) * 4
    y = np.zeros(int(SR * (total_beats * BEAT + 1)))
    kick = _hit(55, 0.25, 18)
    rng = np.random.default_rng(0)
    hat = rng.standard_normal(int(SR * 0.05)) * np.exp(-np.arange(int(SR * 0.05)) / SR * 80)
    pad_t = np.arange(len(y)) / SR
    beat_i = 0
    for bars, gain in SHAPE:
        for _ in range(bars * 4):
            i = int(beat_i * BEAT * SR)
            hit = kick if beat_i % 4 == 0 else hat * 0.4
            y[i : i + len(hit)] += hit * gain
            beat_i += 1
    # Sustained chord whose level follows the energy shape (the "drop" body).
    env = np.zeros(len(y))
    start = 0
    for bars, gain in SHAPE:
        n = int(bars * 4 * BEAT * SR)
        env[start : start + n] = gain
        start += n
    y += 0.2 * env * (np.sin(2 * np.pi * 220 * pad_t) + np.sin(2 * np.pi * 277 * pad_t))
    y = (y / np.abs(y).max() * 0.9 * 32767).astype(np.int16)

    path = tmp_path_factory.mktemp("song") / "click.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())
    return str(path)


@pytest.fixture(scope="module")
def song(track):
    result = SongMap().execute({"input_path": track, "min_section_seconds": 6, "fps": 30})
    assert result.success, result.error
    return result.data


def test_tempo(song):
    assert song["tempo_bpm"] == pytest.approx(BPM, rel=0.03)
    assert song["tempo_note"].startswith("steady")


def test_downbeats_land_on_the_kick(song):
    # Kicks sit on multiples of 4 beats (2.0 s at 120 BPM).
    for t in song["bars"][:8]:
        assert (t / (4 * BEAT)) == pytest.approx(round(t / (4 * BEAT)), abs=0.05)


def test_drop_is_found_on_the_bar_line(song):
    top = song["drops"][0]
    assert top["time_seconds"] == pytest.approx(DROP_AT, abs=BEAT)
    assert top["jump_db"] > 6
    loudest = next(s for s in song["sections"] if s["energy_rank"] == 1)
    assert loudest["start_seconds"] == pytest.approx(DROP_AT, abs=BEAT)


def test_frames_are_emitted_when_fps_is_given(song):
    assert song["beats"][0]["frame"] == round(song["beats"][0]["time_seconds"] * 30)
    assert "start_frame" in song["sections"][0]
