import json

import pandas as pd

from heart_disease.cli import main
from heart_disease.pipeline import Settings, run, write_overview


def test_run_writes_results(tmp_path):
    metrics = run("switzerland", tmp_path, Settings(top_k=10, embeddings=False))
    out = tmp_path / "switzerland"
    assert (out / "metrics.csv").exists()
    assert (out / "figures" / "10_confusion_matrices.png").exists()
    summary = json.loads((out / "summary.json").read_text())
    assert summary["patients"] == 123
    assert len(summary["features_selected"]) == 10
    assert metrics["accuracy"].between(0, 1).all()
    assert "Majority class (baseline)" in set(metrics["model"])

    table = write_overview(metrics, tmp_path).read_text()
    assert "| Model | Switzerland |" in table


def test_cli_info(capsys):
    main(["info", "-l", "hungary"])
    assert "294" in capsys.readouterr().out


def test_metrics_are_reproducible(tmp_path):
    settings = Settings(top_k=10, embeddings=False)
    first = run("switzerland", tmp_path / "a", settings)
    second = run("switzerland", tmp_path / "b", settings)
    pd.testing.assert_frame_equal(first, second)
