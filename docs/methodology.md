# Methodology

What `heart-disease run` does for each location, and how it differs from the analysis of 2021.

## Features

The 76 attributes fall into groups ([`data.py`](../src/heart_disease/data.py)):

| Group | Attributes | Default |
|---|---|---|
| Target | `num` (0 = no disease, 1–4 = increasing severity) | target |
| Angiography | `lmt`, `ladprox`, `laddist`, `diag`, `cxmain`, `ramus`, `om1`, `om2`, `rcaprox`, `rcadist` | dropped |
| Identifiers | `id`, `ccf`, `name` | dropped |
| Dates | `ekgmo`, `ekgday`, `ekgyr`, `cmo`, `cday`, `cyr` | dropped |
| Unused | attributes documented as "not used", "irrelevant" or "dummy" | dropped |
| Everything else | patient data, symptoms, ECG and exercise test results | kept |

Of the kept attributes, columns with more than 50 % missing values and constant columns are dropped. Cleveland keeps
31 features, Hungary 28, Switzerland 27 and Long Beach VA 33 (`heart-disease info`).

**Why drop the angiography results?** The diagnosis `num` is the angiographic disease status: it counts the major
vessels with more than 50 % narrowing, and attributes 59–68 are those vessels. A model that sees them predicts the
diagnosis from the diagnosis. In 2021 these attributes were the most important features for Cleveland and Long Beach
VA and explain most of the high accuracies there.

**Why drop identifiers and dates?** They carry no medical information. In 2021 the random forest ranked the patient
`id` among the top features for Switzerland and Long Beach VA, probably because the IDs were assigned in an order that
correlates with the diagnosis.

`--original-features` restores the feature set of 2021: every attribute except `name` whose value is present for the
first patient of the file.

## Preprocessing

Missing values are replaced with the median of the training data and all features are standardised. Both steps are
part of each model's pipeline, so they are fitted on the training data only.

## Split and feature selection

- 75 % of the patients for training, 25 % for testing, stratified by `num` (seed 0 by default).
- A random forest (500 trees) ranks the features on the training data; the top 25 (`--top-k`) are used for the
  embeddings and the classifiers.

## Embeddings

t-SNE (perplexity 30, or less for small locations), UMAP (15 neighbours, minimum distance 0.15) and an autoencoder
with the layers features → 8 → 2 → 8 → features (tanh, min-max scaled input). The autoencoder replaces the Keras model
in R of 2021 and uses scikit-learn's `MLPRegressor`.

## Classifiers

| Model | Settings |
|---|---|
| Majority class (baseline) | always predicts the most frequent class |
| Logistic regression | default regularisation |
| Naive Bayes | Gaussian |
| SVM | linear, polynomial (degree 3) and RBF kernel, probabilities calibrated for the ROC curves |
| KNN | 5 neighbours |
| Neural network | one hidden layer with 16 units (replaces the Keras network of 2021) |

## Metrics

| Metric | Why |
|---|---|
| Accuracy | as in 2021; compare it with the baseline |
| Balanced accuracy | mean recall over the classes; 0.2 is chance level for five classes |
| ROC AUC | one-vs-rest, macro average; only if the test set contains every class |
| 5-fold cross-validation accuracy | mean and standard deviation over all patients, less dependent on one split |

## Differences to 2021

| | 2021 (`v1.x`) | Now |
|---|---|---|
| Code | four copies of one script | one package, location as a parameter |
| Data | converted by hand (`formatter.py`, header added manually) | raw files parsed directly |
| Features | all attributes present for the first patient | leakage, identifiers, dates and unused attributes dropped |
| Missing values | columns dropped if the first patient had none | median imputation, columns with > 50 % missing dropped |
| Split | random, fitted scaler on all data | stratified, preprocessing fitted on training data |
| Seeds | partly fixed | fixed everywhere |
| Neural networks | Keras (Python), autoencoder in R | scikit-learn |
| Output | plots and console logs | figures, CSV and JSON per location |
