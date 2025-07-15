import pandas as pd
from sklearn.base import BaseEstimator

def predict_single_input(model: BaseEstimator, input_dict: dict) -> str:
    try:
        df_input = pd.DataFrame([input_dict])
        prediction = model.predict(df_input)[0]
        return prediction
    except Exception as e:
        raise ValueError(f"Kesalahan saat prediksi: {e}")
