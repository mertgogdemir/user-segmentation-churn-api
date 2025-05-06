import gradio as gr
import pandas as pd
import joblib
import json
from src.feature_engineering import create_features
from src.segmentation import segment_users

# Modeli yükle
model = joblib.load("models/rf_churn.joblib")

def predict_segment(events_json):
    try:
        if isinstance(events_json, str):
            events = json.loads(events_json)
        else:
            events = events_json
        df_events = pd.DataFrame(events["events"])
        features = create_features(df_events)
        preds = model.predict_proba(features)[:, 1]  # Churn olasılığı örnek
        features["pred_churn_prob"] = preds
        segments = segment_users(features)
        features["segment"] = segments
        return features.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

iface = gr.Interface(
    fn=predict_segment,
    inputs=gr.Textbox(label="Kullanıcı Event JSON", lines=10, placeholder='{"events": [...]}'),
    outputs="json",
    title="Kullanıcı Segmentasyon Demo",
    description="Kullanıcı event verisini JSON olarak girin, modelin segmentasyon ve tahmin çıktısını anında görün."
)

if __name__ == "__main__":
    iface.launch()
