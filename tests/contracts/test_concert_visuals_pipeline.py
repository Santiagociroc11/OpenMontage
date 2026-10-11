"""Contracts for the concert-visuals pipeline.

The pipeline's promise is that every stage times its work on the song map, so
the manifest must make `song_map` a hard requirement where timing is decided,
and every skill it names must exist (the checkpoint loader would otherwise run
the stage with no instructions).
"""

from pathlib import Path

from lib.pipeline_loader import load_pipeline
from tools.tool_registry import registry

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = load_pipeline("concert-visuals")


def _stage(name: str) -> dict:
    return next(s for s in MANIFEST["stages"] if s["name"] == name)


def test_both_production_modes_need_the_song_map() -> None:
    modes = {m["name"]: m for m in MANIFEST["production_modes"]}
    assert set(modes) == {"song_sync", "vj_loops", "free_run"}
    for mode in modes.values():
        assert "song_map" in mode["required_tools"]


def test_timing_stages_require_song_map() -> None:
    for stage in ("idea", "script"):
        assert "song_map" in _stage(stage)["required_tools"]


def test_look_test_gates_before_asset_generation() -> None:
    sub = {s["name"]: s for s in _stage("scene_plan")["sub_stages"]}
    assert sub["look_test"]["human_approval_default"] is True


def test_every_named_skill_exists() -> None:
    skills = set(MANIFEST["required_skills"]) | {s["skill"] for s in MANIFEST["stages"]}
    skills.add(MANIFEST["orchestration"]["skill"])
    for skill in skills:
        assert (REPO_ROOT / "skills" / f"{skill}.md").exists(), skill


def test_every_named_tool_is_registered() -> None:
    registry.discover()
    named = set()
    for stage in MANIFEST["stages"]:
        for key in ("required_tools", "optional_tools", "tools_available"):
            named.update(stage.get(key, []))
        for sub in stage.get("sub_stages", []):
            named.update(sub.get("tools_available", []))
    for mode in MANIFEST["production_modes"]:
        named.update(mode.get("required_tools", []) + mode.get("optional_tools", []))
    missing = sorted(t for t in named if t not in registry._tools)
    assert not missing, missing
