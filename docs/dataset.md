# Dataset

## Source

[UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease), donated by David W. Aha in 1988, licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Citation:

> Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). *Heart Disease* [Dataset]. UCI Machine Learning
> Repository. https://doi.org/10.24432/C52P4X

[`data/raw/`](../data/raw/) holds the whole folder of the archive as downloaded in March 2021, including the
original description [`heart-disease.names`](../data/raw/heart-disease.names).

| Location | File | Institution | Instances |
|---|---|---|---|
| Cleveland | `cleveland.data` | Cleveland Clinic Foundation | 303 |
| Hungary | `hungarian.data` | Hungarian Institute of Cardiology, Budapest | 294 |
| Switzerland | `switzerland.data` | University Hospital Zurich | 123 |
| Long Beach VA | `long-beach-va.data` | V.A. Medical Center, Long Beach, CA | 200 |

The instance counts are those of `heart-disease.names`. `cleveland.data` is partly corrupted (see
[`WARNING`](../data/raw/WARNING)); the parser yields 282 of the 303 Cleveland patients. The other files
yield the full counts.

Each file has 76 attributes; missing values are `-9`. The target is attribute 58, `num`, from 0 (no disease) to 4.
The complete attribute list is in the [appendix of the report](report.md).

Class distribution (`num`) according to the report:

| Location | 0 | 1 | 2 | 3 | 4 | Total |
|---|---|---|---|---|---|---|
| Cleveland | 164 | 55 | 36 | 35 | 13 | 303 |
| Hungary | 188 | 37 | 26 | 28 | 15 | 294 |
| Switzerland | 8 | 48 | 32 | 30 | 5 | 123 |
| Long Beach VA | 51 | 56 | 41 | 42 | 10 | 200 |

## Unused files

The `processed.*` files (14 attributes), `reprocessed.hungarian.data`, `new.data`, `bak` and `cleve.mod` are not
used. They are included for completeness.

`new.data` contains the last names of patients (attribute 76, `name`); in the four used files this attribute is
replaced with the placeholder `name`. The analysis scripts drop the column.

## Parsing

In the raw files, one patient spans several lines and ends with the placeholder `name`.
[`parse_raw`](../src/heart_disease/data.py) splits the text at `name`, keeps records with exactly 76 values and turns
`-9` into missing values. The result is identical to the CSV files the 2021 version produced by hand (see
[`v1.1.0`](https://github.com/HuberNicolas/heart-disease-risk-factors-uzh/tree/v1.1.0): `formatter.py` plus a header
row); this was checked cell by cell for all four locations when the parser was written.

## Hashes

Each raw file has an `.md5` file next to it, and all of them match:

```bash
cd data/raw && for f in *.md5; do md5 -r "${f%.md5}"; done
```

On Linux, use `md5sum -c *.md5` instead. The intermediate CSV files of 2021 (only in `v1.x`) were hashed on Windows
with CRLF line endings.
