import os
import subprocess
import pandas as pd

# 1. Data Preparation
os.system('python src/data_preparation.py')

# 2. Feature Engineering
os.system('python src/feature_engineering.py')

# 3. Modeling
os.system('python src/modeling.py')

# 4. Segmentation
features = pd.read_csv('outputs/features.csv')
if os.path.exists('models/rf_churn.joblib'):
    import joblib
    rf_churn = joblib.load('models/rf_churn.joblib')
    model_features = rf_churn.feature_names_in_
    for col in model_features:
        if col not in features.columns:
            features[col] = 0
    features = features.reindex(columns=list(features.columns) + [col for col in model_features if col not in features.columns], fill_value=0)
    features['pred_churn'] = rf_churn.predict(features[model_features])
else:
    features['pred_churn'] = features['target_churn_risk']

from segmentation import segment_users
segmented = segment_users(features)
segmented.to_csv('outputs/segmented_users.csv', index=False)

print('Tüm pipeline başarıyla tamamlandı! Dashboard için: streamlit run src/dashboard_app.py')
