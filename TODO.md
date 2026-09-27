# TODO

Open tasks for the repository. See also [Known issues](README.md#known-issues).

## 1. Release of the submitted state (v1.x)

- [x] Tag the submission commit ("Submission via OLAT", 24 May 2021) as `v1.0.0`, release with report and slides
- [x] `v1.1.0`: dependencies of May 2021, Ruff, docs, MIT license, reproduce workflow (green on GitHub Actions)
- [x] Rename the GitHub repository to `heart-disease-risk-factors-uzh`

## 2. Modernisation (v2)

- [x] Python 3.12+, current libraries, uv lock
- [x] One package instead of four copies of the analysis script; location as a parameter, CLI
- [x] Parse the raw files directly instead of the manual CSV conversion
- [x] Drop target leakage (angiography), identifiers and dates; `--original-features` for the 2021 set
- [x] Fixed seeds, results as files, baseline and balanced accuracy
- [x] Autoencoder and neural network in scikit-learn instead of Keras and R
- [x] Tests and CI
- [x] Check the first CI run on GitHub
- [x] Release `v2.0.0`

## 3. Ideas

- [ ] Binary task (disease yes/no) next to the five levels
- [ ] Train on one location, test on the others
- [ ] Hyperparameter tuning with nested cross-validation
