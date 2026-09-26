"""

Data Science Project: Heart Disease Prediction

"""

import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.model_selection as model_selection
from keras.layers import Dense
from keras.models import Sequential
from sklearn import metrics, svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, label_binarize
from umap import UMAP

file_dir = os.path.dirname(os.path.abspath(__file__))
csv_folder = "rand_forest_feature_selection(25)"

########################################################################
# ------------------ PREPROCESSING & DATA VISUALIZATION -----------------
########################################################################

# Load the dataset
df_c = pd.read_csv("data/cleveland_76_header.csv", sep=",")

df_c.head
df_c.columns
df_c.dtypes

# Remove the missing values
cols = []
for i in df_c.columns:
    if df_c.loc[0, i] == -9:
        cols.append(i)
df_c[cols] = "NA"
df_c = df_c.drop(cols, axis=1)
df_c = df_c.drop("name", axis=1)

# Maximum heart rate VS age (+ target)
plt.figure(figsize=(14, 8))
plt.scatter(x=df_c.age[df_c.num == 1], y=df_c.thalach[(df_c.num == 1)], c="indianred", alpha=0.5, edgecolors="red")
plt.scatter(x=df_c.age[df_c.num == 2], y=df_c.thalach[(df_c.num == 2)], c="indianred", alpha=0.5, edgecolors="red")
plt.scatter(x=df_c.age[df_c.num == 3], y=df_c.thalach[(df_c.num == 3)], c="indianred", alpha=0.5, edgecolors="red")
plt.scatter(x=df_c.age[df_c.num == 4], y=df_c.thalach[(df_c.num == 4)], c="indianred", alpha=0.5, edgecolors="red")
plt.scatter(x=df_c.age[df_c.num == 0], y=df_c.thalach[(df_c.num == 0)], c="lightskyblue", alpha=0.5, edgecolors="blue")
# plt.legend(["Disease", "Not disease"], labelcolor = ["indianred", "lightskyblue"])
red_patch = mpatches.Patch(color="indianred", label="Disease")
blue_patch = mpatches.Patch(color="lightskyblue", label="Not disease")
plt.legend(handles=[red_patch, blue_patch])
plt.title("Maximum heart rate as a function of age", fontsize=20, fontstyle="italic")
plt.xlabel("Age", fontsize=14)
plt.ylabel("Maximum Heart Rate", fontsize=14)
plt.savefig("plots/cleveland_1_max_heart_rate_vs_age.png")
plt.show()


#  Cholesterol level vs age (+ target) (1 = male; 0 = female)
plt.figure(figsize=(15, 8))
sns.set(font_scale=1.2)
sns.scatterplot(data=df_c, x="age", y="chol", hue="sex", size="chol", sizes=(50, 300), palette="pastel", alpha=0.8)
plt.title("Cholesterol level as a function of age", fontsize=20, fontstyle="italic")
plt.xlabel("Age", fontsize=16)
plt.ylabel("Cholesterol level", fontsize=16)
plt.savefig("plots/cleveland_2_chol_level.png")
plt.show()

# Blood pressure vs pain chest (1 = male; 0 = female)
plt.figure(figsize=(15, 8))
df_c.loc[(df_c.cp == 1), "cp"] = "Typical angina"
df_c.loc[(df_c.cp == 2), "cp"] = "Atypical angina"
df_c.loc[(df_c.cp == 3), "cp"] = "Non-anginal pain"
df_c.loc[(df_c.cp == 4), "cp"] = "Asymptomatic"
sns.boxplot(data=df_c, x="cp", y="trestbps", hue="sex", palette="pastel")
plt.title("Blood pressure vs chest pain categories", fontsize=20, fontstyle="italic")
plt.xlabel("Chest pain", fontsize=14)
plt.ylabel("Blood pressure", fontsize=14)
plt.savefig("plots/cleveland_3_blood_pressure_vs_cp.png")
plt.show()


# Correlation between features
C = df_c.drop(["num"], axis=1)
C.corrwith(df_c["num"]).plot.bar(
    figsize=(15, 8), title="Correlation of the features with the target variable", fontsize=18, rot=90, grid=True
)
plt.savefig("plots/cleveland_4_correlation_of_features_and_target.png")

corrMatrix = C.corr()
mask = np.zeros_like(corrMatrix, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True
f, ax = plt.subplots(figsize=(15, 8))
cmap = sns.diverging_palette(220, 10, as_cmap=True)
sns.heatmap(corrMatrix, mask=mask, cmap=cmap, vmax=0.5, center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.5})
plt.savefig("plots/cleveland_5_correlation_matrix.png")


# Blood pressure vs age (+ target)
sns.lmplot(x="age", y="trestbps", hue="num", col="num", ci=95, data=df_c, order=1, height=2.5).set(
    ylabel="Blood pressure", xlabel="Age"
).fig.suptitle("Effects of age on blood pressure", fontsize=20, x=0.53, y=1.05, fontstyle="oblique")
plt.savefig("plots/cleveland_6_blood_pressure_vs_age_target.png")


# Maximum heart rate vs age (+ target)
sns.lmplot(x="age", y="thalach", data=df_c, hue="num", col="num", ci=95, order=1, height=2.5).set(
    ylabel="Maximum heart rate", xlabel="Age"
).fig.suptitle("Effects of age on heart rate", fontsize=20, x=0.53, y=1.05, fontstyle="oblique")
plt.savefig("plots/cleveland_7_max_heart_rate_vs_age_target.png")

# 'thalach' refers to the maximum heart rate achieved during thalium stress test.
# At first sight, we might suppose that the maximum heart rate is lower for those diagnosed with heart diseases.
# Indeed, it seems logical to assume that a higher rate indicates a satisfactory heart condition since it managed to increase its rate to such a level during the stress test.

# Distribution of age vs disease
plt.figure(figsize=(15, 8))
sns.kdeplot(x=df_c.loc[df_c["num"] == 4, "age"], shade=True, label="4")
sns.kdeplot(x=df_c.loc[df_c["num"] == 3, "age"], shade=True, label="3")
sns.kdeplot(x=df_c.loc[df_c["num"] == 2, "age"], shade=True, label="2")
sns.kdeplot(x=df_c.loc[df_c["num"] == 1, "age"], shade=True, label="1")
sns.kdeplot(x=df_c.loc[df_c["num"] == 0, "age"], shade=True, label="0")
plt.title("Distributions of age according to the presence of heart disease", y=1.05, fontsize=16, fontstyle="oblique")
plt.legend()
plt.savefig("plots/cleveland_8_distribution_disease_vs_age.png")
plt.show()

# Comprare the distribution of the disease according to age and sex
df_c.groupby("sex")["age"].hist()
df_c.groupby("sex").age.plot(kind="kde")
plt.savefig("plots/cleveland_9_distribution_disease_vs_age_and_sex.png")


#######################################################################
# ------------------------ SPLITTING THE DATASET -----------------------
#######################################################################

# Renaming cols
df_c.loc[(df_c.cp == "Typical angina"), "cp"] = 1
df_c.loc[(df_c.cp == "Atypical angina"), "cp"] = 2
df_c.loc[(df_c.cp == "Non-anginal pain"), "cp"] = 3
df_c.loc[(df_c.cp == "Asymptomatic"), "cp"] = 4

# Split the dataset
X = df_c.loc[:, df_c.columns != "num"]
y = df_c.loc[:, "num"]
X_train, X_test, y_train, y_test = model_selection.train_test_split(
    X, y, train_size=0.75, test_size=0.25, shuffle=True, random_state=101
)


#######################################################################
# -------------------------- FEATURE SELECTION -------------------------
#######################################################################

# Feature selection using Random Forests for measuring the relative importance of each feature on the prediction.
# Pros: scale invariant, robust to irrelevant features, interpretable
# Cons: tendency to overfit (not good for generalization)
random_forest = RandomForestClassifier(n_estimators=100)
random_forest.fit(X_train, y_train)

Y_prediction = random_forest.predict(X_test)

random_forest.score(X_train, y_train)
acc_random_forest = round(random_forest.score(X_train, y_train) * 100, 2)
print(
    round(
        acc_random_forest,
        2,
    ),
    "%",
)

importances = pd.DataFrame({"feature": X_train.columns, "importance": np.round(random_forest.feature_importances_, 3)})
importances = importances.sort_values("importance", ascending=False).set_index("feature")

importances.head(25)
importances.head(25).sum()  # with 25 features, we can "explain" for 80 %

# Plot the dataframe of importances
importances.plot.bar()
plt.savefig("plots/cleveland_10_feature_importance_RFC.png")
# the distal left anterior descending artery seems to be one of the most important features.
# Indeed, it is part of the left main coronary artery (LAD), considered the most important because it supplies more than half of the blood to the heart.

# Select the 25 most "important" features
ind = importances.head(25).index.tolist()
X = df_c.loc[:, df_c.columns != "num"]
X = X.loc[:, ind]
y = df_c.loc[:, "num"]

# Eventually save the reduced dataset
file_path = os.path.join(file_dir, csv_folder, "cleveland_X_25_header.csv.csv")
X.to_csv(file_path, index=False, header=True)
# X.to_csv(r'C:\Users\Nicolas\Desktop\cleveland_X_25_header.csv', index = False, header=True) # absolute path
file_path = os.path.join(file_dir, csv_folder, "cleveland_y_25_header.csv.csv")
# y.to_csv(r'C:\Users\Nicolas\Desktop\cleveland_y_25_header.csv', index = False, header=True) # absolute path
y.to_csv(file_path, index=False, header=True)


##########################################################################
# ---------------- DIMENSIONALITY REDUCTION & VISUALIZATION ---------------
##########################################################################

# Dimensionality reduction using t-SNE
plt.figure(figsize=(14, 8))
for index, perp in enumerate([5, 25, 45, 65]):
    tsne = TSNE(n_components=2, perplexity=perp, random_state=0)
    embedded_sne = pd.DataFrame(tsne.fit_transform(X), columns=["tsne1", "tsne2"])
    plt.subplot(2, 2, index + 1)
    sns.scatterplot(x="tsne1", y="tsne2", data=embedded_sne, hue=y.tolist(), alpha=0.9, linewidth=0.5, s=30)
    plt.title("Perplexity = {}".format(str(perp)))
    plt.xlabel("")
    plt.ylabel("")
# plt.legend(['0', '1', '2', '3', '4'], bbox_to_anchor=(3,5), loc=2, borderaxespad=0.0)
plt.suptitle("Dimension reduction using t-SNE")
plt.savefig("plots/cleveland_11_t_SNE.png")
plt.show()

# Perplexity = 1 : local variations dominate
# Perplexity = 75 : global variations dominate

# Dimensionality reduction using UMAP
plt.figure(figsize=(14, 8))
umap_2d = UMAP(random_state=0, n_neighbors=15, min_dist=0.15)
embedded_umap = pd.DataFrame(umap_2d.fit_transform(X), columns=["UMAP1", "UMAP2"])
sns.scatterplot(x="UMAP1", y="UMAP2", data=embedded_umap, hue=y.tolist(), alpha=0.9, linewidth=0.5, s=30)
plt.savefig("plots/cleveland_12_UMAP.png")
plt.show()

# Dimensionality reduction using neural networks (Autoencoders)
# -> in R


##########################################################################
# ------------------ CLASSIFICATION - LOGISTIC REGRESSION -----------------
##########################################################################

# Classification using logistic regression
scaling = StandardScaler()
X_scaled = scaling.fit_transform(X)
X_train, X_test, y_train, y_test = model_selection.train_test_split(
    X_scaled, y, train_size=0.75, test_size=0.25, shuffle=True, random_state=101
)

# Multinomial Logistic Regression
log_regression = LogisticRegression(multi_class="multinomial", solver="lbfgs")

# Score
y_score = log_regression.fit(X_train, y_train).decision_function(X_test)

# Predictions
LR_pred = log_regression.predict(X_test)

# Confusion matrix
cnf_matrix_LR = metrics.confusion_matrix(y_test, LR_pred)
print("Accuracy:", metrics.accuracy_score(y_test, LR_pred))
plt.figure(figsize=(10, 6))
sns.heatmap(cnf_matrix_LR, annot=True)
plt.savefig("plots/cleveland_13_confusion_matrix_LR.png")

# Accuracy of the model
acc_LR = accuracy_score(y_test, LR_pred)

# AUC & ROC Curve
probs_LR = log_regression.predict_proba(X_test)

y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3, 4])
n_classes = y_test_bin.shape[1]

auc = metrics.roc_auc_score(y_test_bin, probs_LR)
print("AUC: %.2f" % auc)


def ROC_Plot(y_test_bin, probs, n_classes, index):
    lyst = [[], [], [], [], []]
    colors = ["tomato", "orange", "gold", "cornflowerblue", "chocolate"]

    for i in range(n_classes):
        fpr_, tpr_, thresholds_ = metrics.roc_curve(y_test_bin[:, i], probs[:, i])
        lyst[i].append([fpr_, tpr_])

    plt.figure(figsize=(8, 6))
    for i in range(n_classes):
        plt.plot(lyst[i][0][0], lyst[i][0][1], color=colors[i], label="ROC curve of class {}".format(i))
    plt.plot([0, 1], [0, 1], color="darkblue", linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver Operating Characteristic (ROC) Curve")
    plt.legend()
    plt.savefig("plots/cleveland_{}_ROC.png".format(index))
    plt.show()


ROC_Plot(y_test_bin, probs_LR, n_classes, 14)


######################################################################
# -------------------- CLASSIFICATION - NAIVE BAYES -------------------
######################################################################

# Classification using naive Bayes
# Pros - can also perform multiclass classification by comparing all the classes’ probability given a query point.
# Pros - efficient on large datasets since the time, and space complexity is less.
scaling = StandardScaler()
X_scaled = scaling.fit_transform(X)

X_train, X_test, y_train, y_test = model_selection.train_test_split(
    X_scaled, y, train_size=0.75, test_size=0.25, shuffle=True, random_state=101
)

# Naîve Bayes
naiveBayes = GaussianNB()  # the likelihood of the features is assumed to be Gaussian
naiveBayes.fit(X_train, y_train)

# Predictions
naiveBayes_pred = naiveBayes.predict(X_test)

# Confusion matrix
cnf_matrix_NB = metrics.confusion_matrix(y_test, naiveBayes_pred)
print("Accuracy:", metrics.accuracy_score(y_test, naiveBayes_pred))
plt.figure(figsize=(10, 6))
sns.heatmap(cnf_matrix_NB, annot=True)
plt.savefig("plots/cleveland_15_confusion_matrix_naiveBayes.png")
cnf_matrix_NB = confusion_matrix(y_test, naiveBayes_pred)

# Accuracy of the model
acc_NB = accuracy_score(y_test, naiveBayes_pred)

# AUC & ROC Curve
probs_NB = naiveBayes.predict_proba(X_test)

y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3, 4])
n_classes = y_test_bin.shape[1]

auc = metrics.roc_auc_score(y_test_bin, probs_NB)
print("AUC: %.2f" % auc)

ROC_Plot(y_test_bin, probs_NB, n_classes, 16)


######################################################################
# ------------------------ CLASSIFICATION - SVM -----------------------
######################################################################

# Classification using Support Vector Machine
scaling = StandardScaler()
X_scaled = scaling.fit_transform(X)
X_train, X_test, y_train, y_test = model_selection.train_test_split(
    X_scaled, y, train_size=0.75, test_size=0.25, shuffle=True, random_state=101
)

# SVM using a linear kernel
svc_linear = svm.SVC(kernel="linear")
svc_linear.probability = True
svc_linear.fit(X_train, y_train)
svc_linear_pred = svc_linear.predict(X_test)
svc_linear.score(X_test, y_test)
svc_linear_acc = metrics.accuracy_score(y_test, svc_linear_pred)
print(svc_linear_acc)

# AUC & ROC Curve
probs_svclinear = svc_linear.predict_proba(X_test)
y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3, 4])
n_classes = y_test_bin.shape[1]
ROC_Plot(y_test_bin, probs_svclinear, n_classes, 17)

# SVM using a polynomial kernel
svc_poly = svm.SVC(kernel="poly", degree=3)
svc_poly.probability = True
svc_poly.fit(X_train, y_train)
svc_poly_pred = svc_poly.predict(X_test)
svc_poly.score(X_test, y_test)
svc_poly_acc = metrics.accuracy_score(y_test, svc_poly_pred)
print(svc_poly_acc)

# AUC & ROC Curve
probs_svcpoly = svc_poly.predict_proba(X_test)
y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3, 4])
n_classes = y_test_bin.shape[1]
ROC_Plot(y_test_bin, probs_svcpoly, n_classes, 18)

# SVM using a RBF kernel
# C - a high C tries to minimize the misclassification of training data and a low value tries to maintain a smooth classification.
# Gamma - gamma determines the distance a single data sample exerts influence.
svc_rbf = svm.SVC(kernel="rbf", gamma=0.8, C=0.8)
svc_rbf.probability = True
svc_rbf.fit(X_train, y_train)
svc_rbf_pred = svc_rbf.predict(X_test)
svc_rbf.score(X_test, y_test)
svc_rbf_acc = metrics.accuracy_score(y_test, svc_rbf_pred)
print(svc_rbf_acc)

# AUC & ROC Curve
probs_svcrbf = svc_rbf.predict_proba(X_test)
y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3, 4])
n_classes = y_test_bin.shape[1]
ROC_Plot(y_test_bin, probs_svcrbf, n_classes, 19)

# Confusion matrices
plt.figure(figsize=(10, 5))
plt.subplot(1, 3, 1)
sns.heatmap(confusion_matrix(y_test, svc_linear_pred), annot=True)
plt.subplot(1, 3, 2)
sns.heatmap(confusion_matrix(y_test, svc_poly_pred), annot=True)
plt.subplot(1, 3, 3)
sns.heatmap(confusion_matrix(y_test, svc_rbf_pred), annot=True)
plt.savefig("plots/cleveland_20_confusion_matrices_SVC_lin_poly_rbf).png")


######################################################################
# ------------------------ CLASSIFICATION - KNN -----------------------
######################################################################

# Classification using K-nearest Neighbors
scaling = StandardScaler()
X_scaled = scaling.fit_transform(X)
X_train, X_test, y_train, y_test = model_selection.train_test_split(
    X_scaled, y, train_size=0.75, test_size=0.25, shuffle=True, random_state=101
)

# KNN
knn = KNeighborsClassifier(n_neighbors=5, algorithm="ball_tree")
knn.fit(X_train, y_train)
knn_pred = knn.predict(X_test)
knn_acc = accuracy_score(y_test, knn_pred)
print(knn_acc)

# Cross-validation and model selection
knn_scores = cross_val_score(knn, X, y, cv=5, scoring="accuracy")
print(knn_scores)
print(knn_scores.mean())

k_range = range(1, 40)
k_scores = []
for k in k_range:
    knn = KNeighborsClassifier(n_neighbors=k, algorithm="ball_tree")
    knn.fit(X_train, y_train)
    knn_pred = knn.predict(X_test)
    knn_acc = accuracy_score(y_test, knn_pred)
    k_scores.append(knn_acc)
    # knn_scores = cross_val_score(knn, X, y, cv = 5, scoring = 'accuracy')
    # k_scores.append(knn_scores.mean())
plt.figure(figsize=(8, 5))
plt.plot(k_range, k_scores)
plt.xlabel("Value of K for KNN")
plt.ylabel("Accuracy")
# plt.ylabel('Cross-Validated Accuracy')
plt.savefig("plots/cleveland_21_KNN.png")
plt.show()

# AUC & ROC Curve
probs_knn = knn.predict_proba(X_test)
y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3, 4])
n_classes = y_test_bin.shape[1]
ROC_Plot(y_test_bin, probs_knn, n_classes, 22)


######################################################################
# ------------------ CLASSIFICATION - NEURAL NETWORKS -----------------
######################################################################

# Classification using a simple Neural Networks
scaling = StandardScaler()
X_scaled = scaling.fit_transform(X)
X_train, X_test, y_train, y_test = model_selection.train_test_split(
    X_scaled, y, train_size=0.75, test_size=0.25, shuffle=True, random_state=101
)
X_train.shape
y_train.shape

X_train = X_train.astype(float)
X_test = X_test.astype(float)
y_train_bin = label_binarize(y_train, classes=[0, 1, 2, 3, 4])
y_test_bin = label_binarize(y_test, classes=[0, 1, 2, 3, 4])

print(X_train.shape, X_test.shape, y_train_bin.shape, y_test_bin.shape)

# Build the network
model = Sequential()

# First hidden layer
model.add(Dense(5, activation="relu", input_shape=(X_train.shape[1],)))

# Out hidden
model.add(Dense(y_train_bin.shape[1], activation="softmax"))

# Summary of the model
model.summary()

# Compile the model
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

history = model.fit(X_train, y_train_bin, epochs=50, batch_size=16, verbose=1, validation_data=(X_test, y_test_bin))

# Predict the test set
p = model.predict(X_test)
p = p > 0.5
print("Accuracy of the model: %.3f%%" % (accuracy_score(y_test_bin, p) * 100))
# print(classification_report(y_test_bin, p))
