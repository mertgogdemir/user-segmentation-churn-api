import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from segmentation import segment_users
from feature_engineering import create_features

app = FastAPI(title="User Churn & Upsell Prediction API")

MODEL_PATH = "models/rf_churn.joblib"

class UserEvent(BaseModel):
    user_id: str
    event_type: str
    timestamp: str  # ISO format datetime
    plan_type: str
    country: str
    device_type: str
    industry: str

class UserEventsRequest(BaseModel):
    events: list[UserEvent]

@app.post("/predict_segment/")
def predict_segment(request: UserEventsRequest):
    # 1. Eventleri DataFrame'e çevir
    df = pd.DataFrame([e.dict() for e in request.events])
    if df.empty:
        raise HTTPException(status_code=400, detail="Empty event list.")
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 2. Feature engineering
    features = create_features(df)

    # 3. Model yükle ve tahmin
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        model_features = model.feature_names_in_
        for col in model_features:
            if col not in features.columns:
                features[col] = 0
        features = features.reindex(columns=list(features.columns) + [col for col in model_features if col not in features.columns], fill_value=0)
        features['pred_churn'] = model.predict(features[model_features])
    else:
        features['pred_churn'] = features['target_churn_risk']

    # 4. Segmentasyon
    segmented = segment_users(features)

    # 5. Sonuçları JSON olarak döndür
    result = segmented.to_dict(orient="records")
    return {"segments": result}

@app.get("/")
def root():
    return {"message": "User Churn & Upsell Prediction API is running."}
