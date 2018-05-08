from imblearn.under_sampling import RandomUnderSampler, ClusterCentroids
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from collections import defaultdict

import csv
import numpy as np


PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']
BUGS = [
    [str(x) for x in range(1, 134)],
    [str(x) for x in range(1, 66)],
    [str(x) for x in range(1, 27)],
    [str(x) for x in range(1, 107)],
    [str(x) for x in range(1, 39)],
    [str(x) for x in range(1, 28)]
]
FORMULAE = ['barinel', 'jaccard', 'opt2', 'tarantula', 'ochiai', 'dstar2', 'muse']


dataset = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
filename = '/Users/ashish/code/cs5704/software-engineering/fault-localization.cs.washington.edu/' \
           'susp/%s-%s-%s-line-suspiciousness'

for project, bugs in zip(PROJECTS, BUGS):
    for bug in bugs:
        for formula in FORMULAE:
            file = filename % (project, bug, formula)
            with open(file) as freader:
                csvreader = csv.DictReader(freader)
                for row in csvreader:
                    dataset[project][bug][row['Line']].append(row['Suspiciousness'])


buggy_lines = '/Users/ashish/code/cs5704/software-engineering/fault-localization-data/analysis/pipeline-scripts/' \
              'buggy-lines/%s-%s.buggy.lines'
faults = defaultdict(lambda: defaultdict(list))

for project, bugs in zip(PROJECTS, BUGS):
    for bug in bugs:
        buggy_lines_file = buggy_lines % (project, bug)
        with open(buggy_lines_file) as freader:
            try:
                for line in freader:
                    faulty_line = '#'.join(line.split('#')[:2])
                    faults[project][bug].append(faulty_line)
            except:
                pass

recency = '/Users/ashish/code/cs5704/recency/%s-%s-tarantula-sorted-susp-with-recency'
for project, bugs in zip(PROJECTS, BUGS):
    for bug in bugs:
        recency_file = recency % (project, bug)
        try:
            with open(recency_file) as freader:
                for line in freader:
                    split = line.split(',')
                    code_line = split[0].strip()
                    recency_value = split[-1].strip()
                    if code_line in dataset[project][bug]:
                        dataset[project][bug][code_line].append(recency_value)
        except:
            pass


for project, bugs in zip(PROJECTS, BUGS):
    for bug in bugs:
        for line in dataset[project][bug]:
            if line in faults[project][bug]:
                dataset[project][bug][line].append('1')
            else:
                dataset[project][bug][line].append('0')


delete_list = []
for project, bugs in zip(PROJECTS, BUGS):
    for bug in bugs:
        for line in dataset[project][bug]:
            if len(dataset[project][bug][line]) != 9:
                delete_list.append((project, bug, line))

for item in delete_list:
    del dataset[item[0]][item[1]][item[2]]

data = []
for project, bugs in zip(PROJECTS, BUGS):
    for bug in bugs:
        for line in dataset[project][bug]:
            data.append(dataset[project][bug][line])

data = np.array(data, dtype=np.float32)
X = data[:, :8]
y = data[:, 8]

rus = RandomUnderSampler(random_state=42)
X_res, y_res = rus.fit_sample(X, y)

skf = StratifiedKFold(n_splits=5, random_state=42)

score_rfc = []
score_svm = []
score_lr = []

precision_rfc = []
precision_svm = []
precision_lr = []

recall_rfc = []
recall_svm = []
recall_lr = []

f1_rfc = []
f1_svm = []
f1_lr = []

for train_index, val_index in skf.split(X_res, y_res):
    X_train, X_test = X_res[train_index], X_res[val_index]
    y_train, y_test = y_res[train_index], y_res[val_index]

    # Random Forest Classifier
    rfc = RandomForestClassifier(random_state=42)
    rfc.fit(X_train, y_train)
    y_pred = rfc.predict(X_test)
    score_rfc.append(accuracy_score(y_test, y_pred))
    precision_rfc.append(precision_score(y_test, y_pred))
    recall_rfc.append(recall_score(y_test, y_pred))
    f1_rfc.append(f1_score(y_test, y_pred))
    print("Random Forest Accuracy: %s" % accuracy_score(y_pred, y_test))

    # Random Forest Classifier
    lr = LogisticRegression(random_state=42)
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    score_lr.append(accuracy_score(y_pred, y_test))
    precision_lr.append(precision_score(y_test, y_pred))
    recall_lr.append(recall_score(y_test, y_pred))
    f1_lr.append(f1_score(y_test, y_pred))
    print("Logistic Regression Accuracy: %s" % accuracy_score(y_pred, y_test))

    # Random Forest Classifier
    svm = LinearSVC(random_state=42)
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    score_svm.append(accuracy_score(y_pred, y_test))
    precision_svm.append(precision_score(y_test, y_pred))
    recall_svm.append(recall_score(y_test, y_pred))
    f1_svm.append(f1_score(y_test, y_pred))
    print("SVM Accuracy: %s" % accuracy_score(y_pred, y_test))
    print()

print("******** Random Forest ********")
print("Accuracy  :  %s" % np.average(score_rfc))
print("Precision :  %s" % np.average(precision_rfc))
print("Recall    :  %s" % np.average(recall_rfc))
print("F1-Score  :  %s" % np.average(f1_rfc))
print("*******************************\n")

print("******** SVM ********")
print("Accuracy  :  %s" % np.average(score_svm))
print("Precision :  %s" % np.average(precision_svm))
print("Recall    :  %s" % np.average(recall_svm))
print("F1-Score  :  %s" % np.average(f1_svm))
print("*********************\n")

print("******** Logistic Regression ********")
print("Accuracy  :  %s" % np.average(score_lr))
print("Precision :  %s" % np.average(precision_lr))
print("Recall    :  %s" % np.average(recall_lr))
print("F1-Score  :  %s" % np.average(f1_lr))
print("*************************************\n")


