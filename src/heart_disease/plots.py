"""Figures for one location. Each function saves one PNG and returns its path."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from sklearn.metrics import roc_curve  # noqa: E402

from .analysis import CLASSES, ModelResult  # noqa: E402

sns.set_theme(style="whitegrid")
DISEASE_PALETTE = {"No disease": "#4C9BE8", "Disease": "#E05D5D"}
CLASS_PALETTE = sns.color_palette("rocket_r", n_colors=len(CLASSES))


def _save(fig: plt.Figure, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def _with_disease(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(disease=np.where(df["num"] > 0, "Disease", "No disease"))


def exploratory(df: pd.DataFrame, title: str, out: Path) -> list[Path]:
    """The exploratory plots of the 2021 analysis, one file each."""
    df = _with_disease(df)
    paths = []

    for column, label, name in [("thalach", "Maximum heart rate", "01_heart_rate_vs_age"),
                                ("chol", "Serum cholesterol (mg/dl)", "02_cholesterol_vs_age")]:  # fmt: skip
        values = df[column].replace(0, np.nan)
        if values.notna().sum() < 10:  # the Swiss data has no cholesterol values
            continue
        fig, ax = plt.subplots(figsize=(9, 6))
        sns.scatterplot(data=df.assign(**{column: values}), x="age", y=column, hue="disease",
                        palette=DISEASE_PALETTE, alpha=0.7, ax=ax)  # fmt: skip
        ax.set(xlabel="Age", ylabel=label, title=f"{label} by age – {title}")
        paths.append(_save(fig, out / f"{name}.png"))

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.boxplot(data=df, x="cp", y="trestbps", hue="disease", palette=DISEASE_PALETTE, ax=ax)
    ax.set(xlabel="Chest pain type (1 typical angina … 4 asymptomatic)", ylabel="Resting blood pressure (mm Hg)",
           title=f"Resting blood pressure by chest pain type – {title}")  # fmt: skip
    paths.append(_save(fig, out / "03_blood_pressure_vs_chest_pain.png"))

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.kdeplot(data=df, x="age", hue="disease", palette=DISEASE_PALETTE, fill=True, common_norm=False, ax=ax)
    ax.set(xlabel="Age", title=f"Age distribution – {title}")
    paths.append(_save(fig, out / "04_age_distribution.png"))

    fig, ax = plt.subplots(figsize=(9, 6))
    rates = df.assign(sex=df["sex"].map({0: "Female", 1: "Male"}), age_group=pd.cut(df["age"], range(25, 85, 10)))
    rates = rates.groupby(["age_group", "sex"], observed=True)["num"].apply(lambda s: (s > 0).mean()).reset_index()
    sns.barplot(data=rates, x="age_group", y="num", hue="sex", ax=ax)
    ax.set(xlabel="Age group", ylabel="Share with heart disease", title=f"Heart disease by age and sex – {title}")
    paths.append(_save(fig, out / "05_disease_by_age_and_sex.png"))
    return paths


def correlations(X: pd.DataFrame, y: pd.Series, title: str, out: Path) -> list[Path]:
    X = X.loc[:, X.nunique() > 1]  # correlation is undefined for constant columns
    corr = X.corrwith(y).dropna().sort_values()
    fig, ax = plt.subplots(figsize=(9, max(4, 0.25 * len(corr))))
    corr.plot.barh(ax=ax, color=np.where(corr > 0, "#E05D5D", "#4C9BE8"))
    ax.set(xlabel="Correlation with num", title=f"Correlation of each feature with the diagnosis – {title}")
    paths = [_save(fig, out / "06_correlation_with_target.png")]

    matrix = X.assign(num=y).corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(matrix, cmap="vlag", center=0, square=True, ax=ax, cbar_kws={"shrink": 0.7})
    ax.set_title(f"Correlation matrix – {title}")
    paths.append(_save(fig, out / "07_correlation_matrix.png"))
    return paths


def importance(importances: pd.Series, selected: int, title: str, out: Path) -> Path:
    top = importances.head(max(selected, 10))
    fig, ax = plt.subplots(figsize=(9, max(4, 0.3 * len(top))))
    colors = ["#E05D5D" if i < selected else "#BBBBBB" for i in range(len(top))]
    ax.barh(top.index[::-1], top.values[::-1], color=colors[::-1])
    ax.set(xlabel="Random forest importance", title=f"Feature importance (top {selected} selected) – {title}")
    return _save(fig, out / "08_feature_importance.png")


def embeddings(points: dict[str, np.ndarray], y: pd.Series, title: str, out: Path) -> Path:
    fig, axes = plt.subplots(1, len(points), figsize=(6 * len(points), 5.5))
    for ax, (name, xy) in zip(np.atleast_1d(axes), points.items(), strict=True):
        sns.scatterplot(x=xy[:, 0], y=xy[:, 1], hue=y.to_numpy(), palette=CLASS_PALETTE, hue_order=CLASSES,
                        ax=ax, s=30, alpha=0.8)  # fmt: skip
        ax.set(title=name, xticks=[], yticks=[])
        ax.legend(title="num", fontsize=8)
    fig.suptitle(f"Two-dimensional embeddings of the selected features – {title}")
    return _save(fig, out / "09_embeddings.png")


def confusion_matrices(results: list[ModelResult], title: str, out: Path) -> Path:
    cols = 4
    rows = -(-len(results) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3.8 * rows))
    for ax, result in zip(axes.flat, results, strict=False):
        sns.heatmap(result.confusion, annot=True, fmt="d", cbar=False, cmap="Blues", ax=ax,
                    xticklabels=CLASSES, yticklabels=CLASSES)  # fmt: skip
        ax.set(title=f"{result.name}\naccuracy {result.accuracy:.2f}", xlabel="Predicted", ylabel="True")
    for ax in axes.flat[len(results) :]:
        ax.axis("off")
    fig.suptitle(f"Confusion matrices on the test set – {title}")
    return _save(fig, out / "10_confusion_matrices.png")


def roc_curves(results: list[ModelResult], y_test: pd.Series, title: str, out: Path) -> Path | None:
    scored = [r for r in results if r.roc_auc is not None and r.probabilities is not None]
    if not scored:
        return None
    cols = 4
    rows = -(-len(scored) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3.8 * rows), squeeze=False)
    classes = sorted(y_test.unique())
    for ax, result in zip(axes.flat, scored, strict=False):
        for i, cls in enumerate(classes):
            fpr, tpr, _ = roc_curve(y_test == cls, result.probabilities[:, i])
            ax.plot(fpr, tpr, color=CLASS_PALETTE[cls], label=f"num = {cls}")
        ax.plot([0, 1], [0, 1], linestyle="--", color="grey")
        ax.set(title=f"{result.name}\nAUC {result.roc_auc:.2f}", xlabel="False positive rate",
               ylabel="True positive rate")  # fmt: skip
    for ax in axes.flat[len(scored) :]:
        ax.axis("off")
    axes.flat[0].legend(fontsize=8)
    fig.suptitle(f"ROC curves (one-vs-rest) on the test set – {title}")
    return _save(fig, out / "11_roc_curves.png")
