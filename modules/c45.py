import joblib
import os
from sklearn.tree import DecisionTreeClassifier, export_text
from utils.helper import MODEL_PATH
from utils import helper

def c45_process(data):
    fitur = [col for col in data.columns if col not in ['Nama', 'Terpilih']]
    X = data[fitur]
    y = data['Terpilih']

    clf = DecisionTreeClassifier(criterion='entropy')
    clf.fit(X, y)

    result = data[['Nama']].copy()
    result['Hasil'] = clf.predict(X)

    tree_rules = export_text(clf, feature_names=list(fitur))
    return result, tree_rules, clf
