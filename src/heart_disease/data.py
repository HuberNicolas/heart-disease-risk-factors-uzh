"""Load the four locations of the UCI Heart Disease dataset from the raw archive files."""

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

MISSING = -9

# The 76 attributes in file order, as documented in data/raw/heart-disease.names.
ATTRIBUTES = [
    "id", "ccf", "age", "sex", "painloc", "painexer", "relrest", "pncaden", "cp", "trestbps",
    "htn", "chol", "smoke", "cigs", "years", "fbs", "dm", "famhist", "restecg", "ekgmo",
    "ekgday", "ekgyr", "dig", "prop", "nitr", "pro", "diuretic", "proto", "thaldur", "thaltime",
    "met", "thalach", "thalrest", "tpeakbps", "tpeakbpd", "dummy", "trestbpd", "exang", "xhypo", "oldpeak",
    "slope", "rldv5", "rldv5e", "ca", "restckm", "exerckm", "restef", "restwm", "exeref", "exerwm",
    "thal", "thalsev", "thalpul", "earlobe", "cmo", "cday", "cyr", "num", "lmt", "ladprox",
    "laddist", "diag", "cxmain", "ramus", "om1", "om2", "rcaprox", "rcadist", "lvx1", "lvx2",
    "lvx3", "lvx4", "lvf", "cathef", "junk", "name",
]  # fmt: skip

TARGET = "num"

IDENTIFIERS = ["id", "ccf", "name"]
DATES = ["ekgmo", "ekgday", "ekgyr", "cmo", "cday", "cyr"]
# Marked as "not used", "irrelevant" or "dummy" in the attribute documentation.
UNUSED = [
    "dummy", "restckm", "exerckm", "thalsev", "thalpul", "earlobe",
    "lvx1", "lvx2", "lvx3", "lvx4", "lvf", "cathef", "junk",
]  # fmt: skip
# Results of the angiography the diagnosis `num` is derived from; using them as features leaks the target.
ANGIOGRAPHY = ["lmt", "ladprox", "laddist", "diag", "cxmain", "ramus", "om1", "om2", "rcaprox", "rcadist"]


class Location(StrEnum):
    CLEVELAND = "cleveland"
    HUNGARY = "hungary"
    SWITZERLAND = "switzerland"
    LONG_BEACH_VA = "long-beach-va"

    @property
    def file_name(self) -> str:
        return "hungarian.data" if self is Location.HUNGARY else f"{self.value}.data"

    @property
    def label(self) -> str:
        return {"long-beach-va": "Long Beach VA"}.get(self.value, self.value.title())


def parse_raw(text: str) -> pd.DataFrame:
    """Parse a raw `.data` file into one row per patient.

    Each patient spans several lines and ends with the placeholder `name`. Records without exactly 76 values
    (the corrupted part of cleveland.data) are skipped.
    """
    records = [chunk.split() + ["name"] for chunk in re.split(r"\bname\b", text)[:-1]]
    records = [r for r in records if len(r) == len(ATTRIBUTES)]
    df = pd.DataFrame(records, columns=ATTRIBUTES)
    numeric = [c for c in ATTRIBUTES if c != "name"]
    df[numeric] = df[numeric].apply(pd.to_numeric)
    df[TARGET] = df[TARGET].astype(int)
    return df


def load_location(location: Location | str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Return all 76 attributes of one location, with missing values (-9) as NaN."""
    location = Location(location)
    text = (raw_dir / location.file_name).read_text(encoding="latin-1")
    return parse_raw(text).replace(MISSING, np.nan)


@dataclass(frozen=True)
class FeatureSet:
    """Which attribute groups to drop before modelling."""

    drop_angiography: bool = True
    drop_identifiers_and_dates: bool = True
    drop_unused: bool = True
    drop_constant: bool = True
    max_missing: float = 0.5

    @classmethod
    def original(cls) -> "FeatureSet":
        """The feature set of the 2021 analysis: every attribute without missing values in the first row."""
        return cls(
            drop_angiography=False,
            drop_identifiers_and_dates=False,
            drop_unused=False,
            drop_constant=False,
            max_missing=0.0,
        )


def select_features(df: pd.DataFrame, feature_set: FeatureSet = FeatureSet()) -> tuple[pd.DataFrame, pd.Series]:
    """Split a location into features X and target y according to the feature set."""
    drop = {"name", TARGET}
    if feature_set.drop_unused:
        drop.update(UNUSED)
    if feature_set.drop_identifiers_and_dates:
        drop.update(IDENTIFIERS + DATES)
    if feature_set.drop_angiography:
        drop.update(ANGIOGRAPHY)
    X = df.drop(columns=[c for c in df.columns if c in drop])
    if feature_set.max_missing == 0.0:
        # 2021: drop a column if the first patient has no value for it.
        X = X.loc[:, X.iloc[0].notna()]
    else:
        X = X.loc[:, X.isna().mean() <= feature_set.max_missing]
    # Constant columns (for example chol, which is always 0 in the Swiss data) carry no information.
    if feature_set.drop_constant:
        X = X.loc[:, X.nunique(dropna=True) > 1]
    return X, df[TARGET]
