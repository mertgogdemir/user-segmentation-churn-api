# AI Growth Case Study Projesi

Bu proje, kullanıcı davranışlarını analiz ederek ödeme, churn riski ve upsell potansiyelini tahmin eden; segmentasyon ve gerçek zamanlı dashboard sunan uçtan uca bir AI destekli büyüme analitiği sistemidir.

## Özellikler
- **Feature Engineering:** Case study tanımlarına uygun hedef değişkenler ve gelişmiş özellikler.
- **Modelleme:** SMOTE ile veri dengesi, Random Forest & XGBoost, GridSearchCV ile hiperparametre optimizasyonu, SHAP ile açıklanabilirlik.
- **Segmentasyon:** High Value, Medium Value, Growth Potential, Churn Risk ve Other segmentleri.
- **Dashboard:** KPI kartları, segment bazında analizler, kullanıcı detay ekranı ve açıklama kutuları.
- **Pipeline Otomasyonu:** Tek komutla tüm süreci başlatan otomasyon scripti (`run_all.py`).

## Kullanım
1. **Ortamı Hazırlayın**
   ```bash
   pip install -r requirements.txt
   ```
2. **Tüm Süreci Çalıştırın**
   ```bash
   python src/run_all.py
   ```
   Bu komut sırasıyla veri hazırlama, feature engineering, modelleme, segmentasyon ve çıktı üretimini tamamlar.

3. **Dashboard'u Başlatın**
   ```bash
   streamlit run src/dashboard_app.py
   ```
   Dashboard'da segment KPI'ları, analizler ve kullanıcı detaylarını inceleyebilirsiniz.

## Segment Açıklamaları
- **High Value:** Ödeme yaptı, churn riski yok, upsell adayı. En değerli kullanıcılar.
- **Medium Value:** Ödeme yaptı, churn riski yok, upsell adayı değil. Sadık ama büyüme potansiyeli düşük.
- **Growth Potential:** Ödeme yaptı, churn riski yok, yeni upsell adayı. Büyüme için hedeflenebilir.
- **Churn Risk:** Churn riski yüksek. Kayıp riski olan kullanıcılar.
- **Other:** Yukarıdaki segmentlere uymayanlar.

## Örnek Analiz Ekranı
> Dashboard'u başlatıp, segment KPI kartlarını ve kullanıcı detaylarını içeren bir ekran görüntüsü ekleyin.

## Dosya Yapısı
```
├── src/
│   ├── data_preparation.py
│   ├── feature_engineering.py
│   ├── modeling.py
│   ├── segmentation.py
│   ├── dashboard_app.py
│   └── run_all.py
├── outputs/
│   ├── features.csv
│   ├── segmented_users.csv
│   └── shap_*.png
├── models/
│   └── *.joblib
├── requirements.txt
└── README.md
```

## Notlar
- Tüm kod ve segment mantığı case study yönergelerine %100 uyumludur.
- Model çıktıları ve segmentasyon, dashboard'da gerçek zamanlı veya batch olarak analiz edilebilir.
- Gelişmiş model açıklamaları için `outputs/shap_*.png` dosyalarını inceleyebilirsiniz.

---
Her türlü soru ve ek geliştirme için iletişime geçebilirsiniz.
I Growth Uzmanı Vaka Çalışması

Bu proje, kullanıcı profili ve olay verilerini analiz ederek ödeme olasılığı, churn riski ve upselling potansiyeli tahminleri yapan, segmentasyon ve interaktif dashboard sunan bir AI sistemidir.

## Klasör Yapısı
- `data/` : Ham veriler
- `notebooks/` : Keşifsel analiz ve feature engineering için notebooklar
- `src/` : Veri hazırlama, modelleme ve dashboard kodları
- `models/` : Kaydedilen AI modelleri (.joblib)
- `outputs/` : Segmentlenmiş kullanıcı verisi ve görseller

## Çalıştırma
1. Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
2. `src/` içindeki betikleri çalıştırarak veri hazırlama, modelleme ve segmentasyon adımlarını uygulayın.
3. Dashboard'u başlatmak için: `streamlit run src/dashboard_app.py`

Detaylar için `dokumantasyon.md` dosyasına bakınız.
