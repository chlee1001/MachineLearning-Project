from sklearn.preprocessing import LabelEncoder
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import cm
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

df = pd.read_csv('bank.csv')

print("\n--------------------------- < Initial data > ----------------------------")
print(df)
print("-------------------------------------------------------------------------\n")
# Dirty data count output
print("In Initial data, total dirty data count = ", sum(df.isna().sum()))

# ──────────────────────────────────────────
#          Drop Columns
# ──────────────────────────────────────────
print("\n--------------------------- < Initial Columns > ----------------------------")
count = 0
for c in df.columns:
    if (count != 0) & ((count % 7) == 0):
        print(c)
    elif count == len(df.columns):
        print(c)
    else:
        print(c, end=', ')
    count += 1

df2 = df.copy()

# Drop unnecessary columns
df2.drop(['Unnamed: 0', 'marital', 'marital', 'education', 'contact', 'month', 'day_of_week',
          'duration', 'campaign', 'pdays', 'previous', 'poutcome'], axis=1, inplace=True)

print("\n--------------------------- < After Drop Columns > ----------------------------")
count = 0
for c in df2.columns:
    if (count != 0) & ((count % 7) == 0):
        print(c)
    elif count == len(df2.columns):
        print(c, end='\n\n')
    else:
        print(c, end=', ')
    count += 1

# ──────────────────────────────────────────
#          LABEL ENCODING
# ──────────────────────────────────────────
df2 = df2.apply(LabelEncoder().fit_transform)

# ──────────────────────────────────────────
#      Show Correlation with Heatmap
# ──────────────────────────────────────────
corrmat = df2.corr()
top_corr = corrmat.index
plt.figure(figsize=(9, 9))
g = sns.heatmap(df2[top_corr].corr(), annot=True, cmap="RdYlGn")
# plt.show()


# ──────────────────────────────────────────
#               Normalization
# ──────────────────────────────────────────
y = df2['y']
X = df2.drop(['y'], axis=1)
scaler = MinMaxScaler()
scaled_x = scaler.fit_transform(X)
scaled_x = pd.DataFrame(scaled_x, columns=['age', 'job', 'default', 'housing', 'loan', 'emp.var.rate', 'cons.price.idx',
                                           'cons.conf.idx', 'euribor3m', 'nr.employed'])
target_names = ['No', 'Yes']

# Visualize Data Normalization with MinMax Scaling
ig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(9, 7))
ax1.set_title('Before Scaling', size=15)
sns.kdeplot(df2['age'], ax=ax1)
sns.kdeplot(df2['job'], ax=ax1)
sns.kdeplot(df2['default'], ax=ax1)
sns.kdeplot(df2['housing'], ax=ax1)
sns.kdeplot(df2['loan'], ax=ax1)
sns.kdeplot(df2['emp.var.rate'], ax=ax1)
sns.kdeplot(df2['cons.conf.idx'], ax=ax1)
sns.kdeplot(df2['cons.price.idx'], ax=ax1)
sns.kdeplot(df2['euribor3m'], ax=ax1)
sns.kdeplot(df2['nr.employed'], ax=ax1)

ax2.set_title('After MinMax Scaler', size=15)
sns.kdeplot(scaled_x['age'], ax=ax2)
sns.kdeplot(scaled_x['job'], ax=ax2)
sns.kdeplot(scaled_x['default'], ax=ax2)
sns.kdeplot(scaled_x['housing'], ax=ax2)
sns.kdeplot(scaled_x['loan'], ax=ax2)
sns.kdeplot(scaled_x['emp.var.rate'], ax=ax2)
sns.kdeplot(scaled_x['cons.conf.idx'], ax=ax2)
sns.kdeplot(scaled_x['cons.price.idx'], ax=ax2)
sns.kdeplot(scaled_x['euribor3m'], ax=ax2)
sns.kdeplot(scaled_x['nr.employed'], ax=ax2)

plt.show()

# ──────────────────────────────────────────
#               Split data
# ──────────────────────────────────────────
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(scaled_x, y, test_size=0.2, shuffle=True, random_state=0)

kf = KFold(n_splits=5)

# ──────────────────────────────────────────
#               Decision Tree
# ──────────────────────────────────────────
from sklearn.tree import DecisionTreeClassifier

dt_clf = DecisionTreeClassifier(max_depth=5, criterion='entropy', random_state=0)
dt_clf.fit(X_train, y_train)

y_pred = dt_clf.predict(X_test)

dt_acc = float(accuracy_score(y_test, y_pred).round(3))
dt_mse = float(metrics.mean_squared_error(y_test, y_pred).round(3))
dt_f1 = float(metrics.f1_score(y_test, y_pred, average='weighted', zero_division=1).round(3))
print('\n\n----------------- < Decision Tree > -----------------')
print("Accuracy:", dt_acc)
print("MSE(Mean Square Error): ", dt_mse)
print("F1 Score: ", dt_f1)

cf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(cf_matrix, annot=True, cmap="YlGnBu")
plt.title("Decision Tree Confusion Matrix")
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()
print("\nDecision Tree Classification Report")
print(classification_report(y_test, y_pred, target_names=target_names, digits=3, zero_division=1))

# ──────────────────────────────────────────
#            Logistic Regression
# ──────────────────────────────────────────
logisticRegr = LogisticRegression()
parameters = {'C': [0.1, 1.0, 10.0],
              'solver': ['liblinear', 'lbfgs', 'sag'],
              'max_iter': [50, 100, 200]}

reg_clf = GridSearchCV(logisticRegr, parameters, cv=kf)
reg_clf.fit(X_train, y_train)
print('\n----------------- < Logistic Regression > -----------------')
print("Best parameters:", reg_clf.best_params_)
print("Best score:", reg_clf.best_score_.round(3))

best_reg_clf = LogisticRegression(**reg_clf.best_params_)
best_reg_clf.fit(X_train, y_train)
y_pred = best_reg_clf.predict(X_test)

reg_acc = float(accuracy_score(y_test, y_pred).round(3))
reg_mse = float(metrics.mean_squared_error(y_test, y_pred).round(3))
reg_f1 = float(metrics.f1_score(y_test, y_pred, average='weighted', zero_division=1).round(3))
print("Accuracy:", reg_acc)
print("MSE(Mean Square Error): ", reg_mse)
print("F1 Score: ", reg_f1)

cf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(cf_matrix, annot=True, cmap="YlGnBu")
plt.title("Logistic Regression Confusion Matrix")
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()
print("\nLogistic Regression Classification Report")
print(classification_report(y_test, y_pred, target_names=target_names, digits=3, zero_division=1))

# ──────────────────────────────────────────
#              Random forest
# ──────────────────────────────────────────
randomforest = RandomForestClassifier()
parameters = {'criterion': ['gini', 'entropy'],
              'n_estimators': [1, 10, 100],
              'max_depth': [1, 10, 100]}

ran_clf = GridSearchCV(randomforest, parameters, cv=kf)
ran_clf.fit(X_train, y_train)
print('\n----------------- < Random forest > -----------------')
print("Best parameters:", ran_clf.best_params_)
print("Best score:", ran_clf.best_score_)

best_ran_clf = RandomForestClassifier(**ran_clf.best_params_)
best_ran_clf.fit(X_train, y_train)
y_pred = best_ran_clf.predict(X_test)

ran_acc = float(accuracy_score(y_test, y_pred).round(3))
ran_mse = float(metrics.mean_squared_error(y_test, y_pred).round(3))
ran_f1 = float(metrics.f1_score(y_test, y_pred, average='weighted', zero_division=1).round(3))
print("Accuracy:", ran_acc)
print("MSE(Mean Square Error): ", ran_mse)
print("F1 Score: ", ran_f1)

cf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(cf_matrix, annot=True, cmap="YlGnBu")
plt.title("Random Forest Confusion Matrix")
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()
print("\nRandom Forest Classification Report")
print(classification_report(y_test, y_pred, target_names=target_names, digits=3, zero_division=1))

# ──────────────────────────────────────────
#                   KNN
# ──────────────────────────────────────────
# Neighbors
neighbors = np.arange(0, 30)
# Create empty list that will hold cv scores
cv_scores = []

from sklearn.neighbors import KNeighborsClassifier

knnClassfier = KNeighborsClassifier()
parameters = {'weights': ['uniform', 'distance'],
              'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute']}

knn_clf = GridSearchCV(knnClassfier, parameters, cv=kf)
knn_clf.fit(X_train, y_train)
print('\n----------------- < KNN > -----------------')
print("Best parameters:", knn_clf.best_params_)
print("Best score:", knn_clf.best_score_)

# Perform 10-fold cross validation on training set for odd values of k:
for k in neighbors:
    k_value = k + 1
    knn = KNeighborsClassifier(n_neighbors=k_value, algorithm='brute', weights='uniform', p=2, metric='euclidean')
    kfold = KFold(n_splits=10, random_state=123)
    scores = cross_val_score(knn, X_train, y_train, cv=kfold, scoring='accuracy')
    cv_scores.append(scores.mean() * 100)
    # print("k=%d %0.2f (+/- %0.2f)" % (k_value, scores.mean()*100, scores.std()*100))

optimal_k = neighbors[cv_scores.index(max(cv_scores))]

print("The optimal number of neighbors is %d with %0.1f%%" % (optimal_k, cv_scores[optimal_k]))
# plt.plot(neighbors, cv_scores)
# plt.xlabel('Number of Neighbors K')
# plt.ylabel('Train Accuracy')
# plt.show()


knnClassfier = KNeighborsClassifier(n_neighbors=optimal_k)
knnClassfier.fit(X_train, y_train)
y_pred = knnClassfier.predict(X_test)
knn_acc = float(accuracy_score(y_test, y_pred).round(3))
knn_mse = float(metrics.mean_squared_error(y_test, y_pred).round(3))
knn_f1 = float(metrics.f1_score(y_test, y_pred, average='weighted', zero_division=1).round(3))
print("Accuracy:", knn_acc)
print("MSE(Mean Square Error): ", knn_mse)
print("F1 Score: ", knn_f1)

cf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(cf_matrix, annot=True, cmap="YlGnBu")
plt.title("KNN Confusion Matrix")
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()
print("\nKNN Classification Report")
print(classification_report(y_test, y_pred, target_names=target_names, digits=3, zero_division=1))

# ──────────────────────────────────────────
#                   GradientBoosting
# ──────────────────────────────────────────
from sklearn.ensemble import GradientBoostingClassifier

gbkClassifier = GradientBoostingClassifier()
gbkClassifier.fit(X_train, y_train)
y_pred = gbkClassifier.predict(X_test)

print('\n----------------- < GradientBoosting > -----------------')

gbk_acc = float(accuracy_score(y_test, y_pred).round(3))
gbk_mse = float(metrics.mean_squared_error(y_test, y_pred).round(3))
gbk_f1 = float(metrics.f1_score(y_test, y_pred, average='weighted', zero_division=1).round(3))
print("Accuracy:", gbk_acc)
print("MSE(Mean Square Error): ", gbk_mse)
print("F1 Score: ", gbk_f1)

cf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(cf_matrix, annot=True, cmap="YlGnBu")
plt.title("GradientBoosting Confusion Matrix")
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()
print("\nGradientBoosting Classification Report")
print(classification_report(y_test, y_pred, target_names=target_names, digits=3, zero_division=1))

# ──────────────────────────────────────────
#                   SVM
# ──────────────────────────────────────────
svclassifier = SVC()
parameters = {'C': [0.1, 1.0, 10.0],
              'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
              'gamma': [0.01, 0.1, 1.0, 10.0]}

svm_clf = GridSearchCV(svclassifier, parameters, cv=kf)
svm_clf.fit(X_train, y_train)
print('\n----------------- < SVM > -----------------')
print("Best parameters:", svm_clf.best_params_)
print("Best score:", svm_clf.best_score_)

best_svm_clf = SVC(**svm_clf.best_params_)
best_svm_clf.fit(X_train, y_train)
y_pred = best_svm_clf.predict(X_test)

svm_acc = float(accuracy_score(y_test, y_pred).round(3))
svm_mse = float(metrics.mean_squared_error(y_test, y_pred).round(3))
svm_f1 = float(metrics.f1_score(y_test, y_pred, average='weighted', zero_division=1).round(3))
print("Accuracy:", svm_acc)
print("MSE(Mean Square Error): ", svm_mse)
print("F1 Score: ", svm_f1)

cf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(cf_matrix, annot=True, cmap="YlGnBu")
plt.title("SVM Confusion Matrix")
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()
print("\nSVM Classification Report")
print(classification_report(y_test, y_pred, target_names=target_names, digits=3, zero_division=1))

# ──────────────────────────────────────────
#                   Result
# ──────────────────────────────────────────
print('\n----------------- < Result > -----------------')
data = [
    ['Decision Tree', dt_acc, dt_mse, dt_f1],
    ['Logistic Regression', reg_acc, reg_mse, reg_f1],
    ['Random Forest', ran_acc, ran_mse, ran_f1],
    ['SVM', svm_acc, svm_mse, svm_f1],
    ['KNN', knn_acc, knn_mse, knn_f1],
    ['GradientBoosting', gbk_acc, gbk_mse, gbk_f1]]
result = pd.DataFrame(data, columns=['Algorithm', 'Accuracy', 'MSE', 'F1-score'])
print(result)
