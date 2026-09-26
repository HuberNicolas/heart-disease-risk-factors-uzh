"""Run the whole analysis for one location and write the results to disk."""

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import analysis, plots
from .data import FeatureSet, Location, load_location, select_features


@dataclass(frozen=True)
class Settings:
    seed: int = 0
    top_k: int = 25
    feature_set: FeatureSet = FeatureSet()
    embeddings: bool = True


def run(location: Location | str, output: Path, settings: Settings = Settings()) -> pd.DataFrame:
    """Analyse one location. Writes figures, metrics and selected features to `output/<location>/`."""
    location = Location(location)
    out = output / location.value
    figures = out / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    title = location.label

    df = load_location(location)
    X, y = select_features(df, settings.feature_set)
    plots.exploratory(df, title, figures)
    plots.correlations(X, y, title, figures)

    X_train, X_test, y_train, y_test = analysis.split(X, y, settings.seed)
    importances = analysis.feature_importance(X_train, y_train, settings.seed)
    selected = list(importances.index[: settings.top_k])
    importances.to_frame().assign(selected=importances.index.isin(selected)).to_csv(out / "feature_importance.csv")
    plots.importance(importances, len(selected), title, figures)

    if settings.embeddings:
        plots.embeddings(analysis.embeddings(X[selected], settings.seed), y, title, figures)

    results = analysis.evaluate(X_train[selected], X_test[selected], y_train, y_test, settings.seed)
    plots.confusion_matrices(results, title, figures)
    plots.roc_curves(results, y_test, title, figures)

    metrics = pd.DataFrame(
        [
            {
                "model": r.name,
                "accuracy": r.accuracy,
                "balanced_accuracy": r.balanced_accuracy,
                "roc_auc": r.roc_auc,
                "cv_accuracy_mean": r.cv_accuracy_mean,
                "cv_accuracy_std": r.cv_accuracy_std,
            }
            for r in results
        ]
    )
    metrics.to_csv(out / "metrics.csv", index=False)
    summary = {
        "location": location.value,
        "patients": len(df),
        "class_distribution": {int(k): int(v) for k, v in y.value_counts().sort_index().items()},
        "features_available": X.shape[1],
        "features_selected": selected,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "settings": {"seed": settings.seed, "top_k": settings.top_k, "feature_set": vars(settings.feature_set)},
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return metrics.assign(location=location.label)


def write_overview(metrics: pd.DataFrame, output: Path) -> Path:
    """Write a Markdown table with the test accuracy of every model per location."""
    table = metrics.pivot(index="model", columns="location", values="accuracy")
    order = [loc.label for loc in Location if loc.label in table.columns]
    table = table.reindex(index=metrics["model"].drop_duplicates(), columns=order)
    lines = [
        "| Model | " + " | ".join(order) + " |",
        "|---|" + "---|" * len(order),
        *(f"| {model} | " + " | ".join(f"{v:.2f}" for v in row) + " |" for model, row in table.iterrows()),
    ]
    path = output / "accuracy.md"
    path.write_text("\n".join(lines) + "\n")
    return path
