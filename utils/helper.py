import os
import joblib

RESULT_PATH = "model/c45_model.joblib"
MODEL_PATH = "model/classifier.joblib"

def is_model_available():
    return os.path.exists(MODEL_PATH)

def save_result(result_and_tree):
    joblib.dump(result_and_tree, RESULT_PATH)

def load_result():
    return joblib.load(RESULT_PATH)

def save_model(model):
    joblib.dump(model, MODEL_PATH)

def load_model():
    return joblib.load(MODEL_PATH)