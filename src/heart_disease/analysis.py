"""Feature selection, dimensionality reduction and classification for one location."""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.svm import SVC

CLASSES = [0, 1, 2, 3, 4]


def preprocessing() -> list:
    return [SimpleImputer(strategy="median", keep_empty_features=True), StandardScaler()]


def classifiers(seed: int) -> dict[str, Pipeline]:
    """The classifiers of the 2021 analysis, each with median imputation and scaling."""
    models = {
        "Majority class (baseline)": DummyClassifier(strategy="most_frequent"),
        "Logistic regression": LogisticRegression(max_iter=5000),
        "Naive Bayes": GaussianNB(),
        "SVM, linear": _svm(kernel="linear"),
        "SVM, polynomial (degree 3)": _svm(kernel="poly", degree=3),
        "SVM, RBF": _svm(kernel="rbf"),
        "KNN (k = 5)": KNeighborsClassifier(n_neighbors=5),
        "Neural network": MLPClassifier(hidden_layer_sizes=(16,), max_iter=3000, random_state=seed),
    }
    return {name: make_pipeline(*preprocessing(), model) for name, model in models.items()}


def _svm(**params) -> CalibratedClassifierCV:
    """SVM with calibrated class probabilities for the ROC curves."""
    return CalibratedClassifierCV(SVC(**params), ensemble=False, cv=3)


def split(X: pd.DataFrame, y: pd.Series, seed: int, test_size: float = 0.25):
    """Stratified train/test split; falls back to a plain split if a class has fewer than two patients."""
    stratify = y if y.value_counts().min() >= 2 else None
    return train_test_split(X, y, test_size=test_size, stratify=stratify, random_state=seed)


def feature_importance(X_train: pd.DataFrame, y_train: pd.Series, seed: int) -> pd.Series:
    """Random forest importance of each feature, sorted in descending order."""
    model = make_pipeline(*preprocessing(), RandomForestClassifier(n_estimators=500, random_state=seed))
    model.fit(X_train, y_train)
    importances = model[-1].feature_importances_
    return pd.Series(importances, index=X_train.columns, name="importance").sort_values(ascending=False)


@dataclass
class ModelResult:
    name: str
    accuracy: float
    balanced_accuracy: float
    roc_auc: float | None
    cv_accuracy_mean: float
    cv_accuracy_std: float
    confusion: np.ndarray
    probabilities: np.ndarray | None = field(repr=False, default=None)


def evaluate(
    X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series, seed: int
) -> list[ModelResult]:
    """Fit every classifier on the training set and score it on the test set and with 5-fold cross-validation."""
    X_all, y_all = pd.concat([X_train, X_test]), pd.concat([y_train, y_test])
    folds = min(5, int(y_all.value_counts().min()))
    cv = StratifiedKFold(n_splits=max(folds, 2), shuffle=True, random_state=seed)

    results = []
    for name, model in classifiers(seed).items():
        cv_scores = cross_val_score(clone(model), X_all, y_all, cv=cv, scoring="accuracy")
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
        roc_auc = None
        # ROC AUC (one-vs-rest, macro) is only defined if the test set contains every class the model knows.
        if proba is not None and set(model.classes_) == set(y_test) and len(model.classes_) > 1:
            roc_auc = float(roc_auc_score(y_test, proba, multi_class="ovr", labels=model.classes_))
        results.append(
            ModelResult(
                name=name,
                accuracy=float(accuracy_score(y_test, pred)),
                balanced_accuracy=float(balanced_accuracy_score(y_test, pred)),
                roc_auc=roc_auc,
                cv_accuracy_mean=float(cv_scores.mean()),
                cv_accuracy_std=float(cv_scores.std()),
                confusion=confusion_matrix(y_test, pred, labels=CLASSES),
                probabilities=proba,
            )
        )
    return results


def embeddings(X: pd.DataFrame, seed: int) -> dict[str, np.ndarray]:
    """Two-dimensional embeddings with t-SNE, UMAP and an autoencoder."""
    from umap import UMAP  # slow to import, only needed here

    scaled = make_pipeline(*preprocessing()).fit_transform(X)
    perplexity = min(30.0, (len(X) - 1) / 3)
    return {
        "t-SNE": TSNE(n_components=2, perplexity=perplexity, random_state=seed).fit_transform(scaled),
        "UMAP": UMAP(n_neighbors=15, min_dist=0.15, random_state=seed, n_jobs=1).fit_transform(scaled),
        "Autoencoder": autoencoder_embedding(X, seed),
    }


def autoencoder_embedding(X: pd.DataFrame, seed: int, bottleneck: int = 2) -> np.ndarray:
    """Train a small autoencoder (features -> 8 -> 2 -> 8 -> features) and return the bottleneck activations.

    Replaces the Keras autoencoder in R from 2021, which used min-max scaled inputs and a tanh bottleneck.
    """
    scaled = make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True), MinMaxScaler()).fit_transform(X)
    model = MLPRegressor(
        hidden_layer_sizes=(8, bottleneck, 8), activation="tanh", max_iter=5000, random_state=seed
    ).fit(scaled, scaled)
    hidden = scaled
    for weights, bias in zip(model.coefs_[:2], model.intercepts_[:2], strict=True):
        hidden = np.tanh(hidden @ weights + bias)
    return hidden
