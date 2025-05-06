import pandas as pd
from joblib import load
import numpy as np
import os

print("SEGMENTATION PIPELINE BAŞLADI")

def load_data():
    features = pd.read_csv('outputs/features.csv')
    return features

def predict_churn(features):
    model_path = 'models/rf_churn.joblib'
    if os.path.exists(model_path):
        model = load(model_path)
        # Modelin beklediği feature isimlerini al
        model_features = model.feature_names_in_
        # Eksik olanları sıfırla ekle
        for col in model_features:
            if col not in features.columns:
                features[col] = 0
        # Eksik/fazla sütunları ve tüm feature isimlerini dosyaya ve ekrana yaz
        os.makedirs("outputs", exist_ok=True)
        missing = [col for col in model_features if col not in features.columns]
        extra = [col for col in features.columns if col not in model_features]
        print('Eksik sütunlar:', missing)
        print('Fazla sütunlar:', extra)
        print('model_features:', list(model_features))
        print('features.columns:', list(features.columns))
        # Prediction öncesi sadece modelin beklediği feature'ları ayrı bir DataFrame olarak oluştur
        X_pred = features[list(model_features)]
        print("PREDICT FEATURES:", list(X_pred.columns))
        with open("outputs/model_features_pred.txt", "w", encoding="utf-8") as f:
            f.write(str(list(X_pred.columns)))
        try:
            churn_prob = model.predict_proba(X_pred)[:,1]
            churn_pred = model.predict(X_pred)
            features['pred_churn_prob'] = churn_prob
            features['pred_churn'] = churn_pred
        except Exception as e:
            print("Prediction hatası:", e)
            features['pred_churn_prob'] = np.nan
            features['pred_churn'] = np.nan
        print("SEGMENTATION PIPELINE BİTTİ")
        return features
    else:
        # Model yoksa veya bulunamazsa yine de bu sütunları ekle
        features['pred_churn_prob'] = np.nan
        features['pred_churn'] = features['target_churn_risk'] if 'target_churn_risk' in features.columns else np.nan
        print("SEGMENTATION PIPELINE BİTTİ")
        return features

def segment_users(features):
    seg = []
    for _, row in features.iterrows():
        churn_pred = row.get('pred_churn', row.get('target_churn_risk', 0))
        upsell_flag = row.get('target_upselling_potential', 0)
        payment_flag = row.get('target_made_payment', 0)
        # Öncelik sırası: High Value > Growth Potential > Churn Risk > Medium Value > Other
        if payment_flag == 1:
            seg.append('High Value')
        elif upsell_flag == 1:
            seg.append('Growth Potential')
        elif churn_pred == 1:
            seg.append('Churn Risk')
        elif payment_flag == 1 and churn_pred == 0 and upsell_flag == 0:
            seg.append('Medium Value')
        else:
            seg.append('Other')
    features['segment'] = seg
    return features


def save_segmented(features):
    out_cols = ['user_id','segment','pred_churn_prob','target_made_payment','target_churn_risk','target_upselling_potential'] + [col for col in features.columns if col not in ['user_id','segment','pred_churn_prob','target_made_payment','target_churn_risk','target_upselling_potential']]
    features[out_cols].to_csv('outputs/segmented_users.csv', index=False)
    features[out_cols].to_excel('outputs/segmented_users.xlsx', index=False)


def main():
    features = load_data()
    features = predict_churn(features)
    features = segment_users(features)
    save_segmented(features)
    # Segmentlerin dağılımını ve ilk 5 satırı yazdır
    print('Segment dağılımı:')
    print(features['segment'].value_counts())
    print('\nÖrnek veri:')
    print(features.head())
    print('Segmentasyon tamamlandı. Sonuç: outputs/segmented_users.csv')

if __name__ == "__main__":
    main()
