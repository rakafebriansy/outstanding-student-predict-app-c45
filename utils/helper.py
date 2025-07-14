import os
import joblib

MODEL_PATH = "model/c45_model.joblib"
RESULT_PATH = "model/result.joblib"

def is_model_available():
    return os.path.exists(MODEL_PATH)
def save_model(result_and_tree):
    joblib.dump(result_and_tree, RESULT_PATH)

def load_model():
    return joblib.load(RESULT_PATH)