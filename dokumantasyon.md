# AI Growth Uzmanı Vaka Çalışması: Proje Dokümantasyonu

## Proje Amacı
Kullanıcı profil ve olay verilerini analiz ederek; ödeme olasılığı, churn riski ve upselling potansiyeli tahmini yapan, segmentasyon ve interaktif dashboard sunan bir AI sistemi geliştirmek.

## Klasör ve Dosya Yapısı
- `data/` : Ham veriler (CSV)
- `outputs/` : Birleştirilmiş veri, özellik matrisi ve segmentlenmiş kullanıcılar (CSV)
- `models/` : Eğitilmiş modeller (.joblib)
- `src/` : Tüm Python betikleri
- `notebooks/eda_ve_feature_engineering.ipynb` : EDA ve feature engineering
- `requirements.txt` : Gerekli kütüphaneler
- `README.md` : Proje çalıştırma rehberi
- `dokumantasyon.md` : Bu doküman

## Adım Adım Süreç

### 1. Veri Yükleme ve Birleştirme
- `src/data_preparation.py` ile profil ve olay verileri yüklendi, timestamp dönüştürüldü ve birleştirildi.
- Çıktı: `outputs/merged_data.csv`

### 2. Keşifsel Veri Analizi (EDA)
- `notebooks/eda_ve_feature_engineering.ipynb` ile olay ve profil dağılımları, payment_success oranı ve churn/upsell öngörüleri analiz edildi.
- Önemli Bulgular:
  - Kullanıcıların büyük çoğunluğu ödeme yapmış.
  - Churn riski ve upselling için anlamlı segmentler mevcut.

### 3. Özellik Mühendisliği
- `src/feature_engineering.py` ile kullanıcı başına olay sayıları, zaman bazlı ve profil özellikleri türetildi.
- Hedef değişkenler:
  - `target_made_payment`: En az bir ödeme yapan kullanıcı.
  - `target_churn_risk`: 7+ gündür aktif olmayan ve ödeme yapmış kullanıcı.
  - `target_upselling_potential`: Ödeme yapmış ve yüksek aktiviteye sahip kullanıcı.
- Kategorik değişkenler one-hot encoding ile sayısallaştırıldı.
- Çıktı: `outputs/features.csv`

### 4. Modelleme
- `src/modeling.py` ile üç hedef için ayrı modeller kurulmaya çalışıldı.
- Sınıf dengesizliği nedeniyle sadece `target_churn_risk` için anlamlı model kurulabildi.
- Kullanılan algoritmalar: Lojistik Regresyon, Random Forest
- Model başarıları yüksek (AUC: 0.98+), modeller `models/` klasörüne kaydedildi.

### 5. Segmentasyon
- `src/segmentation.py` ile kullanıcılar dört segmente ayrıldı:
  - Yüksek Değerli
  - Churn Riski Yüksek
  - Upselling Adayı
  - Diğer/Stabil
- Çıktı: `outputs/segmented_users.csv`

### 6. Dashboard
- `src/dashboard_app.py` ile Streamlit tabanlı interaktif dashboard hazırlandı.
- Segment dağılımı, profil analizleri, churn olasılığı ve kullanıcı detayları görselleştirildi.
- Çalıştırmak için: `streamlit run src/dashboard_app.py`

## Varsayımlar ve Zorluklar
- Sınıf dengesizliği: Ödeme ve upselling hedeflerinde neredeyse tüm kullanıcılar pozitif sınıfta. Bu nedenle bu hedefler için model kurulamadı.
- Churn tanımı: 7 gün inaktiflik ve ödeme yapmış olma üzerinden yapıldı. Farklı eşikler denenebilir.
- Özellik mühendisliği: Kullanıcı davranış çeşitliliği arttıkça daha zengin özellikler eklenebilir.

## Model ve Segmentasyon Sonuçları
- Churn modeli yüksek doğruluk ve AUC ile çalıştı.
- Segmentasyon ile hedefli aksiyon alınabilecek kullanıcı grupları net olarak ayrıldı.

---

## Canlı Demo: HuggingFace Spaces

Proje, gerçek zamanlı olarak test edilebilen bir Gradio arayüzü ile HuggingFace Spaces üzerinde canlıya alınmıştır.

- **Demo Linki:** [Kullanıcı Segmentasyon Demo (HuggingFace Spaces)](https://huggingface.co/spaces/mertgogdemirr/user-segmentation-churn-demo)
- **Kullanım:**
    - Kullanıcı event verisini JSON formatında girin.
    - Model, otomatik olarak segmentasyon ve churn tahmini yaparak sonucu ekranda gösterir.
    - Örnek input:
      ```json
      {
        "events": [
          {
            "user_id": 1,
            "event_type": "login",
            "timestamp": "2024-04-01T09:00:00",
            "plan_type": "Basic",
            "country": "Turkey",
            "device_type": "Mobile",
            "industry": "Finance"
          },
          {
            "user_id": 1,
            "event_type": "purchase",
            "timestamp": "2024-04-01T09:05:00",
            "plan_type": "Basic",
            "country": "Turkey",
            "device_type": "Mobile",
            "industry": "Finance"
          }
        ]
      }
      ```
    - **Çıktı:** Kullanıcıya ait segment, churn olasılığı ve tüm öznitelikler JSON olarak gösterilir.

Bu canlı demo, projenin teknik yetkinliğini ve gerçek zamanlı analiz kabiliyetini jüriye ve paydaşlara göstermek için hazırlanmıştır.

---

## Kullanılan Betikler
- `src/data_preparation.py`: Veri yükleme ve birleştirme
- `src/feature_engineering.py`: Özellik mühendisliği ve hedefler
- `src/modeling.py`: Model eğitimi ve değerlendirme
- `src/segmentation.py`: Segmentasyon
- `src/dashboard_app.py`: Dashboard

## Sonuç
Proje, AI destekli kullanıcı segmentasyonu ve churn/upsell tahmini için uçtan uca bir çözüm sunmaktadır. Dashboard üzerinden segment ve kullanıcı analizleri kolayca yapılabilmektedir.

---

Her türlü iyileştirme, yeni segment veya farklı model denemeleri için kodlar kolayca tekrar çalıştırılabilir ve özelleştirilebilir.
