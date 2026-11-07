from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from astrid.core._shared.result_manifest import harvest_staged_outputs

PACK = Path(__file__).resolve().parents[3] / "editorial"


def test_script_pipeline_writes_the_receipt_the_host_harvests(tmp_path, monkeypatch):
    monkeypatch.setenv("ASTRID_INTERNAL_INVOCATION", "1")
    spec = importlib.util.spec_from_file_location("script_pipeline_run", PACK / "actions/script_pipeline/run.py")
    run = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, run)
    spec.loader.exec_module(run)
    action = yaml.safe_load((PACK / "pack.yaml").read_text())["actions"]["script_pipeline"]
    out = tmp_path / "outputs"
    argv = [str(arg).replace("{out}", str(out)) for arg in action["invocation"]["command"]["argv"][3:]]

    assert run.main([*argv, "--fake", "--prompt", "A short brief.", "--env-file", str(tmp_path / "none.env")]) == 0

    definition = SimpleNamespace(outputs=(), metadata=action["metadata"])
    harvested = harvest_staged_outputs(out, definition=definition, require=True)
    ports = {item["name"]: Path(item["path"]).resolve() for item in harvested}
    assert ports["selected_scene"] == (out / "produces" / "selected_scene.md").resolve()
    assert ports["manifest"] == (out / "produces" / "manifest.json").resolve()
