"""Map a song's musical structure: tempo, beat grid, bars, sections and drops.

This is the timing backbone of the concert-visuals pipeline. A concert visual
lives or dies on landing cuts, flashes and scene changes on the music, so every
downstream stage reads this map instead of guessing timestamps by ear.

Output (also written to ``output_path`` as JSON):
  - tempo_bpm, tempo_stability (inter-beat-interval spread; high = live/rubato)
  - beats[]:    time, bar, beat_in_bar, strength, energy, low_energy (0-1)
  - bars[]:     downbeat times
  - sections[]: start/end snapped to downbeats, local tempo, energy in dB
                relative to the loudest section, most similar earlier
                section (repeated chorus -> high similarity)
  - drops[] / breakdowns[]: section boundaries ranked by energy jump (dB)

Per-frame frequency bands for audio-reactive motion are a separate concern —
use ``.agents/skills/hyperframes-creative/scripts/extract-audio-data.py``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

SAMPLE_RATE = 22050
HOP = 512


class SongMap(BaseTool):
    name = "song_map"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "analysis"
    provider = "librosa"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:librosa", "binary:ffmpeg"]
    install_instructions = "pip install librosa (ffmpeg on PATH decodes mp3/m4a)"

    capabilities = ["beat_grid", "tempo", "song_sections", "drop_detection"]
    best_for = [
        "syncing visual cuts and flashes to beats and downbeats",
        "splitting a song into intro/verse/chorus/drop sections for visual planning",
        "finding drops and breakdowns where the visual must change hardest",
        "choosing musically clean loop lengths (bars) for VJ loops",
    ]

    input_schema = {
        "type": "object",
        "required": ["input_path"],
        "properties": {
            "input_path": {"type": "string", "description": "Audio or video file"},
            "output_path": {
                "type": "string",
                "description": "Where to write song_map.json (optional)",
            },
            "beats_per_bar": {
                "type": "integer",
                "default": 4,
                "description": "Meter. 4 for almost all pop/electronic; 3 for waltz-time songs",
            },
            "min_section_seconds": {
                "type": "number",
                "default": 8.0,
                "description": "Sections shorter than this merge into a neighbour",
            },
            "fps": {
                "type": "number",
                "description": "If set, every beat/section also gets a frame index at this fps",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=1024, vram_mb=0, disk_mb=0, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=0, retryable_errors=[])
    idempotency_key_fields = ["input_path", "beats_per_bar", "min_section_seconds"]
    side_effects = ["writes output_path when given"]

    def get_status(self) -> ToolStatus:
        try:
            import librosa  # noqa: F401
        except ImportError:
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        input_path = Path(inputs["input_path"])
        if not input_path.exists():
            return ToolResult(success=False, error=f"File not found: {input_path}")

        beats_per_bar = int(inputs.get("beats_per_bar", 4))
        min_section = float(inputs.get("min_section_seconds", 8.0))
        fps = inputs.get("fps")
        if beats_per_bar < 2:
            return ToolResult(success=False, error="beats_per_bar must be >= 2")

        start = time.time()
        try:
            data = _analyze(input_path, beats_per_bar, min_section, fps)
        except Exception as e:  # librosa raises a wide variety on bad media
            return ToolResult(success=False, error=f"song_map failed: {e}")

        artifacts = []
        if inputs.get("output_path"):
            out = Path(inputs["output_path"])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(data, indent=2), encoding="utf-8")
            artifacts.append(str(out))

        return ToolResult(
            success=True,
            data=data,
            artifacts=artifacts,
            duration_seconds=round(time.time() - start, 2),
        )


def _norm(x):
    import numpy as np

    x = np.asarray(x, dtype=float)
    span = x.max() - x.min()
    return (x - x.min()) / span if span > 0 else np.zeros_like(x)


def _analyze(path: Path, beats_per_bar: int, min_section: float, fps) -> dict[str, Any]:
    import librosa
    import numpy as np

    y, sr = librosa.load(str(path), sr=SAMPLE_RATE, mono=True)
    duration = len(y) / sr

    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, hop_length=HOP
    )
    if len(beat_frames) < beats_per_bar * 4:
        raise ValueError(
            f"only {len(beat_frames)} beats found — not enough rhythmic content to map"
        )
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=HOP)
    # Tempo from the whole beat span, not librosa's estimate: per-beat
    # intervals are quantized to analysis hops (an exact 120 BPM click reads
    # ~117), while the span averages that error away.
    tempo = 60.0 * (len(beat_times) - 1) / float(beat_times[-1] - beat_times[0])

    # Per-beat signals: onset strength, overall RMS, and low band (kick + bass).
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    spec = np.abs(librosa.stft(y, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=sr)
    low = spec[freqs < 150].mean(axis=0)
    n = min(len(onset_env), len(rms), len(low))
    strength = librosa.util.sync(onset_env[None, :n], beat_frames, aggregate=np.max)[0]
    energy = librosa.util.sync(rms[None, :n], beat_frames, aggregate=np.mean)[0]
    low_e = librosa.util.sync(low[None, :n], beat_frames, aggregate=np.mean)[0]
    # sync() adds a leading segment before the first beat; align to beats.
    strength, energy, low_e = (a[1 : len(beat_frames) + 1] for a in (strength, energy, low_e))

    # ponytail: downbeat = the beat phase whose beats carry the most low-band
    # energy (kick on 1). Right for most 4/4 pop/electronic; wrong for
    # syncopated genres. Upgrade path: madmom's DBN downbeat tracker.
    phase_scores = [low_e[p::beats_per_bar].mean() for p in range(beats_per_bar)]
    phase = int(np.argmax(phase_scores))
    # Bar 1 = first full bar; bar 0 = pickup beats before it.
    bar_of = [(i - phase) // beats_per_bar + 1 for i in range(len(beat_times))]
    beat_in_bar = [(i - phase) % beats_per_bar + 1 for i in range(len(beat_times))]
    downbeat_idx = [i for i in range(len(beat_times)) if beat_in_bar[i] == 1]
    bars = [float(beat_times[i]) for i in downbeat_idx]

    # Sections: agglomerative clustering on beat-synchronous timbre + harmony,
    # boundaries snapped to downbeats so visual changes land on bar 1.
    chroma = librosa.feature.chroma_stft(S=spec**2, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=HOP, n_mfcc=13)
    m = min(chroma.shape[1], mfcc.shape[1])
    feats = np.vstack([librosa.util.normalize(chroma[:, :m], axis=1), _zscore(mfcc[:, :m])])
    sync_feats = librosa.util.sync(feats, beat_frames, aggregate=np.median)
    # Derive the section count from the song itself: one per min_section span,
    # then merge what still comes out shorter than min_section.
    k = int(np.clip(round(duration / (min_section * 2)), 2, 24))
    bounds_beats = librosa.segment.agglomerative(sync_feats, k)
    # sync_feats has a leading pre-first-beat column → shift to beat indices.
    bounds_beats = sorted({max(0, int(b) - 1) for b in bounds_beats} | {0})

    def snap(bi: int) -> int:
        if not downbeat_idx:
            return bi
        return min(downbeat_idx, key=lambda d: abs(d - bi))

    cut_beats = sorted({snap(b) for b in bounds_beats[1:]} - {0})
    edges = [0.0] + [float(beat_times[b]) for b in cut_beats] + [duration]
    edges = _merge_short(edges, min_section)

    track_energy = np.asarray(energy)
    beat_feat = sync_feats[:, 1:]
    sections: list[dict[str, Any]] = []
    for i in range(len(edges) - 1):
        s, e = edges[i], edges[i + 1]
        idx = np.where((beat_times >= s) & (beat_times < e))[0]
        if len(idx) == 0:
            idx = np.array([int(np.argmin(np.abs(beat_times - s)))])
        # Tempo over the whole section span: a per-beat median is quantized to
        # whole analysis hops (at 143 BPM one hop reads as 136 or 152 BPM).
        span = float(beat_times[idx[-1]] - beat_times[idx[0]]) if len(idx) > 1 else 0.0
        sections.append(
            {
                "id": f"s{i + 1:02d}",
                "start_seconds": round(s, 3),
                "end_seconds": round(e, 3),
                "bars": round(len(idx) / beats_per_bar, 1),
                "tempo_bpm": round(60.0 * (len(idx) - 1) / span, 1) if span > 0 else None,
                "_span": span,
                "energy": float(track_energy[idx].mean()),
                "_vec": beat_feat[:, idx].mean(axis=1),
            }
        )

    # Repetition: cosine similarity to every earlier section; the agent reads
    # high similarity as "same part again" (chorus 2 ≈ chorus 1).
    for i, sec in enumerate(sections):
        best = None
        for j in range(i):
            a, b = sec["_vec"], sections[j]["_vec"]
            sim = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
            if best is None or sim > best[1]:
                best = (sections[j]["id"], sim)
        sec["most_similar_to"] = {"id": best[0], "similarity": round(best[1], 3)} if best else None

    # Energy in dB relative to the loudest section (0 dB = loudest, so every
    # number is relative to this song — no absolute loudness threshold).
    peak = max(s["energy"] for s in sections) or 1e-9
    order = sorted(sections, key=lambda s: -s["energy"])
    for sec in sections:
        sec["energy_db"] = round(20 * float(np.log10(max(sec.pop("energy"), 1e-9) / peak)), 2)
        sec["energy_rank"] = order.index(sec) + 1
        sec.pop("_vec")

    changes = []
    for prev, nxt in zip(sections, sections[1:]):
        changes.append(
            {
                "time_seconds": nxt["start_seconds"],
                "into_section": nxt["id"],
                "jump_db": round(nxt["energy_db"] - prev["energy_db"], 2),
            }
        )
    drops = sorted([c for c in changes if c["jump_db"] > 0], key=lambda c: -c["jump_db"])
    breakdowns = sorted([c for c in changes if c["jump_db"] < 0], key=lambda c: c["jump_db"])

    s_n, e_n, l_n = _norm(strength), _norm(energy), _norm(low_e)
    beats = []
    for i, t in enumerate(beat_times):
        b = {
            "time_seconds": round(float(t), 3),
            "bar": int(bar_of[i]),
            "beat_in_bar": int(beat_in_bar[i]),
            "strength": round(float(s_n[i]), 3),
            "energy": round(float(e_n[i]), 3),
            "low_energy": round(float(l_n[i]), 3),
        }
        if fps:
            b["frame"] = int(round(t * fps))
        beats.append(b)
    if fps:
        for sec in sections:
            sec["start_frame"] = int(round(sec["start_seconds"] * fps))
            sec["end_frame"] = int(round(sec["end_seconds"] * fps))

    # Stability: robust spread of inter-beat intervals, judged against the
    # analysis resolution itself (one hop of timing jitter is unavoidable).
    ibi = np.diff(beat_times)
    med = float(np.median(ibi))
    stability = float(np.median(np.abs(ibi - med)) / med)
    jitter = HOP / sr / med
    # A section's tempo is uncertain by ~2 hops over its span (both ends are
    # quantized); only a deviation well beyond that is a real tempo change.
    global_bpm = tempo
    tempo_changes = any(
        abs(sec["tempo_bpm"] / global_bpm - 1) > 2 * (2 * HOP / sr) / sec["_span"]
        for sec in sections
        if sec["tempo_bpm"] and sec["_span"] >= 4 * bar_len_s
    ) if (bar_len_s := med * beats_per_bar) else False
    for sec in sections:
        sec.pop("_span")
    if stability > 2 * jitter:
        tempo_note = "tempo drifts (live take / rubato) - cut on the listed beat times, never on a computed grid"
    elif tempo_changes:
        tempo_note = "tempo changes between sections (see sections[].tempo_bpm) - cut on the listed beat times"
    else:
        tempo_note = "steady grid - safe to cut on computed beats"
    bar_seconds = 60.0 / tempo * beats_per_bar
    dyn_range = -min(s["energy_db"] for s in sections)

    return {
        "file": str(path),
        "duration_seconds": round(duration, 3),
        "tempo_bpm": round(tempo, 2),
        "tempo_stability": round(stability, 4),
        "tempo_note": tempo_note,
        "section_dynamic_range_db": round(dyn_range, 2),
        "beats_per_bar": beats_per_bar,
        "bar_seconds": round(bar_seconds, 3),
        "first_downbeat_seconds": bars[0] if bars else None,
        "loop_lengths_seconds": {f"{n}_bars": round(bar_seconds * n, 3) for n in (4, 8, 16)},
        "fps": fps,
        "beat_count": len(beats),
        "bar_count": len(bars),
        "sections": sections,
        "drops": drops,
        "breakdowns": breakdowns,
        "bars": [round(b, 3) for b in bars],
        "beats": beats,
    }


def _zscore(x):
    import numpy as np

    sd = x.std(axis=1, keepdims=True)
    return (x - x.mean(axis=1, keepdims=True)) / np.where(sd > 0, sd, 1)


def _merge_short(edges: list[float], min_len: float) -> list[float]:
    """Drop interior boundaries until every section is at least min_len long."""
    edges = list(edges)
    while len(edges) > 2:
        lens = [b - a for a, b in zip(edges, edges[1:])]
        i = min(range(len(lens)), key=lambda j: lens[j])
        if lens[i] >= min_len:
            break
        # Merge the shortest section into its shorter neighbour.
        if i == 0:
            edges.pop(1)
        elif i == len(lens) - 1:
            edges.pop(-2)
        else:
            edges.pop(i if lens[i - 1] < lens[i + 1] else i + 1)
    return edges
