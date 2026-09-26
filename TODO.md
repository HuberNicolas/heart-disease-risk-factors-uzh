# TODO

Open tasks for the repository. See also [Known issues](README.md#known-issues).

## 1. Release of the submitted state (v1.x)

- [x] Tag the submission commit ("Submission via OLAT", 24 May 2021) as `v1.0.0`
- [x] Declare the dependencies with the versions of May 2021 (`pyproject.toml`, `uv.lock`, TensorFlow 2.4.1)
- [x] Lint and format the scripts with Ruff (only unused imports removed)
- [x] Remove the duplicate `heart-disease.zip` and editor files; move report and slides to `submission/`
- [x] README, dataset documentation, MIT license, reproduce workflow
- [x] Check the first run of the Reproduce workflow: all four locations run; accuracies within a few points of 2021
- [x] Rename the GitHub repository to `heart-disease-risk-factors-uzh`
- [ ] Create GitHub releases `v1.0.0` (submission, with report and slides as assets) and `v1.1.0`
- [ ] Test `Autoencoders.R` again (R 4.0, keras for R)
- [ ] Add the lecturer of the course to the README

## 2. Modernisation (v2)

- [ ] Current Python and libraries (uv, Python 3.12+)
- [ ] One package instead of four copies of the analysis script; location as a parameter, CLI
- [ ] Rename `Vancouver` to Long Beach VA; folder names without spaces or parentheses
- [ ] Preprocessing as code (formatter for all locations, header from the attribute list)
- [ ] Fixed seeds, results as files instead of console output
- [ ] Autoencoder in Python instead of R
- [ ] Tests and CI on every push

## 3. Before publishing

- [x] Choose and add a license (MIT; UCI data stays CC BY 4.0)
- [x] Add the project context (course, institution, semester) to the README
- [x] Credit third parties (UCI Heart Disease, principal investigators)
- [x] Check for secrets in the files and the git history (none found; only GitHub noreply addresses in commits)
- [x] Co-authors agree to the publication (confirmed by Nicolas)
