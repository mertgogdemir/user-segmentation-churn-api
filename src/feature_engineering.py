import pandas as pd
import numpy as np
import joblib
import sklearn
from datetime import timedelta
import os

def load_merged_data(path='outputs/merged_data.csv'):
    df = pd.read_csv(path, parse_dates=['timestamp'])
    return df

def create_features(df):
    # Kullanıcı başına olay sayıları
    event_counts = df.pivot_table(index='user_id', columns='event_type', values='timestamp', aggfunc='count').fillna(0)
    event_counts.columns = [f'count_{col}' for col in event_counts.columns]

    # Son ve ilk event zamanı
    last_event = df.groupby('user_id')['timestamp'].max().rename('last_event')
    first_event = df.groupby('user_id')['timestamp'].min().rename('first_event')
    account_age_days = (df['timestamp'].max() - first_event).dt.days.rename('account_age_days')
    days_since_last_event = (df['timestamp'].max() - last_event).dt.days.rename('days_since_last_event')

    # Olay frekansı
    total_events = df.groupby('user_id').size().rename('total_events')
    event_frequency = (account_age_days / total_events).replace([np.inf, -np.inf], np.nan).fillna(0).rename('event_frequency')

    # Profil bilgileri
    profile_cols = ['plan_type', 'country', 'device_type', 'industry']
    profiles = df.drop_duplicates('user_id').set_index('user_id')[profile_cols]

    # Cihaz çeşitliliği
    n_device_types = df.groupby('user_id')['device_type'].nunique().rename('n_device_types')

    # İlk ödeme tarihi
    payment_events = df[df['event_type'] == 'payment_success'].groupby('user_id')['timestamp'].min().rename('first_payment_date')
    payment_events = payment_events.reindex(df['user_id'].unique())

    # Birleştir
    features = pd.concat([
        event_counts,
        account_age_days,
        days_since_last_event,
        event_frequency,
        total_events,
        n_device_types,
        profiles,
        first_event,
        payment_events
    ], axis=1)

    # Hedef değişkenler (esnetilmiş koşullar)
    # 1. İlk 14 gün içinde ödeme yaptı mı?
    features['target_made_payment'] = ((features['first_payment_date'] - features['first_event']).dt.days <= 14).astype(int)
    features['target_made_payment'] = features['target_made_payment'].fillna(0).astype(int)

    # 2. Upselling: Ödeme yaptı ve toplam event sayısı ortalamanın üstünde (cihaz şartı yok)
    total_event_mean = features['total_events'].mean()
    features['target_upselling_potential'] = (
        (features['target_made_payment'] == 1) &
        (features['total_events'] > total_event_mean)
    ).astype(int)

    # 3. Churn riski: Son 14 gün hiç aktif olmayan VEYA son 30 gün içinde ödeme yapmamış kullanıcı
    max_time = df['timestamp'].max()
    features['recent_payment'] = ((max_time - features['first_payment_date']).dt.days <= 30).astype(int)
    features['target_churn_risk'] = (
        (features['days_since_last_event'] >= 14) | (features['recent_payment'] == 0)
    ).astype(int)

    # Profil sütunlarını eksiksiz join ettikten sonra, kategorik değişkenlerin tüm olası değerlerini zorunlu olarak tanımla
    all_countries = ['Germany', 'Turkey', 'UK', 'USA']
    all_device_types = ['Mobile', 'Desktop']
    all_plan_types = ['Basic', 'Premium']
    all_industries = ['Finance', 'E-commerce', 'Education', 'Other']
    features['country'] = pd.Categorical(features['country'], categories=all_countries)
    features['device_type'] = pd.Categorical(features['device_type'], categories=all_device_types)
    features['plan_type'] = pd.Categorical(features['plan_type'], categories=all_plan_types)
    features['industry'] = pd.Categorical(features['industry'], categories=all_industries)

    # --- Kategorik değişkenlerin tüm olası değerlerini zorunlu tanımla ---
    all_countries = ['Germany', 'Turkey', 'UK', 'USA']
    all_device_types = ['Mobile', 'Desktop']
    all_plan_types = ['Basic', 'Premium']
    all_industries = ['Finance', 'E-commerce', 'Education', 'Other']
    features['country'] = pd.Categorical(features['country'], categories=all_countries)
    features['device_type'] = pd.Categorical(features['device_type'], categories=all_device_types)
    features['plan_type'] = pd.Categorical(features['plan_type'], categories=all_plan_types)
    features['industry'] = pd.Categorical(features['industry'], categories=all_industries)
    profile_cols = ['country', 'device_type', 'plan_type', 'industry']
    # --- Kategorik değişkenleri one-hot encoding (drop_first=False, dummy_na=False) ---
    features = pd.get_dummies(features, columns=profile_cols, drop_first=False, dummy_na=False)

    # Sürüm bilgisi yazdır
    import os
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/version_debug.txt', 'w', encoding='utf-8') as f:
        f.write('pandas version: ' + pd.__version__ + '\n')
        f.write('sklearn version: ' + sklearn.__version__ + '\n')

    # Modelin beklediği feature isimlerini yükle ve eksikleri ekle
    import joblib
    model_path = 'models/rf_churn.joblib'
    import os
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        model_features = model.feature_names_in_
        for col in model_features:
            if col not in features.columns:
                features[col] = 0
    # Sıralamayı değiştirme! Sadece prediction sırasında features[model_features] kullanılacak.

    return features.reset_index()


if __name__ == "__main__":
    df = load_merged_data()
    features = create_features(df)
    features.to_csv('outputs/features.csv', index=False)
    print("Özellik matrisi oluşturuldu ve outputs/features.csv olarak kaydedildi.")
