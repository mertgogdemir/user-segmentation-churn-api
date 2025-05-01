import pandas as pd
import os

def load_data(profiles_path, events_path):
    """
    Kullanıcı profil ve olay verilerini yükler.
    """
    profiles = pd.read_csv(profiles_path)
    events = pd.read_csv(events_path)
    return profiles, events

def preprocess_events(events):
    """
    Olay verilerindeki timestamp sütununu datetime formatına dönüştürür.
    """
    events['timestamp'] = pd.to_datetime(events['timestamp'])
    return events

def merge_data(profiles, events):
    """
    İki veri setini user_id üzerinden birleştirir.
    """
    merged = pd.merge(events, profiles, how='left', left_on='user_id', right_on='user_id')
    return merged

if __name__ == "__main__":
    profiles_path = os.path.join('data', 'advanced_user_profiles_with_uuid.csv')
    events_path = os.path.join('data', 'advanced_user_events_with_uuid.csv')
    profiles, events = load_data(profiles_path, events_path)
    events = preprocess_events(events)
    merged = merge_data(profiles, events)
    merged.to_csv(os.path.join('outputs', 'merged_data.csv'), index=False)
    print("Veriler yüklendi, işlendi ve birleştirildi. Çıktı: outputs/merged_data.csv")
