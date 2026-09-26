# Dataset

## Source

[UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease), donated by David W. Aha in 1988, licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Citation:

> Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). *Heart Disease* [Dataset]. UCI Machine Learning
> Repository. https://doi.org/10.24432/C52P4X

[`0 raw .data/`](../0%20raw%20.data/) holds the whole folder of the archive as downloaded in March 2021, including the
original description [`heart-disease.names`](../0%20raw%20.data/heart-disease.names).

| Location | File | Institution | Instances |
|---|---|---|---|
| Cleveland | `cleveland.data` | Cleveland Clinic Foundation | 303 |
| Hungary | `hungarian.data` | Hungarian Institute of Cardiology, Budapest | 294 |
| Switzerland | `switzerland.data` | University Hospital Zurich | 123 |
| Long Beach VA | `long-beach-va.data` | V.A. Medical Center, Long Beach, CA | 200 |

The instance counts are those of `heart-disease.names`. `cleveland.data` is partly corrupted (see
[`WARNING`](../0%20raw%20.data/WARNING)); the preprocessing yields 282 of the 303 Cleveland patients. The other files
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

## Preprocessing

1. Copy the four used `.data` files to [`1 raw .csv/`](../1%20raw%20.csv/) and rename them to `.csv`.
2. Run [`formatter.py`](../1%20raw%20.csv/formatter.py) in that folder. In the raw files, one patient spans ten lines
   (twelve in the unused `new.data`); the script joins them into one row per patient and writes `<location>_76.csv`.
   Only one section of the script is active at a time; uncomment the section for the location you want.
3. Add a header row with the 76 attribute names and save the result to [`data/`](../data/) as
   `<location>_76_header.csv`. The header was added by hand.

No values are changed in these steps. The analysis scripts then drop columns whose first value is `-9` and the
`name` column.

## Hashes

Each file has an `.md5` file next to it. The hashes of the CSV files in `1 raw .csv/` (except `cleveland.csv`),
`2 formatted .csv/` and `data/` were computed on Windows with CRLF line endings. The files in the repository have LF
line endings, so `md5` only matches after converting them, for example:

```bash
perl -pe 's/\r?\n/\r\n/' data/cleveland_76_header.csv | md5
```

The raw `.data` files match their hashes directly.
