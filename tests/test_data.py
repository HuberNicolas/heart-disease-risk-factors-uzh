import pytest

from heart_disease.data import (
    ANGIOGRAPHY,
    ATTRIBUTES,
    DATES,
    IDENTIFIERS,
    TARGET,
    FeatureSet,
    Location,
    load_location,
    parse_raw,
    select_features,
)

# Patients per location; cleveland.data is partly corrupted, 282 of its 303 records are readable.
PATIENTS = {"cleveland": 282, "hungary": 294, "switzerland": 123, "long-beach-va": 200}


@pytest.mark.parametrize("location", list(Location))
def test_load_location(location):
    df = load_location(location)
    assert list(df.columns) == ATTRIBUTES
    assert len(df) == PATIENTS[location.value]
    assert set(df[TARGET]) <= {0, 1, 2, 3, 4}
    assert not (df.drop(columns="name") == -9).any().any()


def test_parse_raw_skips_incomplete_records():
    record = " ".join(["1"] * 75) + " name\n"
    broken = "1 2 3 name\n"
    assert len(parse_raw(record + broken + record)) == 2


@pytest.mark.parametrize("location", list(Location))
def test_default_features_exclude_leakage_and_identifiers(location):
    X, y = select_features(load_location(location))
    assert not set(X.columns) & set(ANGIOGRAPHY + IDENTIFIERS + DATES + [TARGET])
    assert len(X) == len(y)
    assert (X.nunique() > 1).all()


def test_original_features_keep_angiography():
    X, _ = select_features(load_location("cleveland"), FeatureSet.original())
    assert {"laddist", "om1", "id"} <= set(X.columns)
    assert "name" not in X.columns
