from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from src.feature_engineering import create_features
from src.segmentation import segment_users

app = FastAPI(title="User Segmentation & Churn Prediction API")
model = joblib.load("models/rf_churn.joblib")

class Event(BaseModel):
    user_id: int
    event_type: str
    timestamp: str
    plan_type: str
    country: str
    device_type: str
    industry: str

class EventsRequest(BaseModel):
    events: list[Event]

@app.post("/predict/")
def predict_segment(request: EventsRequest):
    try:
        df = pd.DataFrame([e.dict() for e in request.events])
        features = create_features(df)
        model_features = model.feature_names_in_
        for col in model_features:
            if col not in features.columns:
                features[col] = 0
        features_for_pred = features[model_features]
        pred_probs = model.predict_proba(features_for_pred)[:, 1]
        features["pred_churn_prob"] = pred_probs
        features = segment_users(features)
        return features.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"message": "User Segmentation & Churn Prediction API is running."}
