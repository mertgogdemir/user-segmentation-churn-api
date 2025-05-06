import streamlit as st
import pandas as pd
import plotly.express as px

SEGMENT_DESCRIPTIONS = {
    'High Value': 'Ödeme yaptı, churn riski yok, upsell adayı. En değerli kullanıcılar.',
    'Medium Value': 'Ödeme yaptı, churn riski yok, upsell adayı değil. Sadık ama büyüme potansiyeli düşük.',
    'Growth Potential': 'Ödeme yaptı, churn riski yok, yeni upsell adayı. Büyüme için hedeflenebilir.',
    'Churn Risk': 'Churn riski yüksek. Kayıp riski olan kullanıcılar.',
    'Other': 'Yukarıdaki segmentlere uymayanlar.'
}

import json

def load_segmented_data(payload_path='test_payload.json'):
    with open(payload_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
    # "segments" anahtarındaki listeyi DataFrame'e çevir
    df = pd.DataFrame(payload["segments"])
    return df

def main():
    st.set_page_config(page_title="Kullanıcı Segmentasyonu Dashboard", layout="wide")
    st.title("Kullanıcı Segmentasyonu ve Davranış Dashboard'u")
    df = load_segmented_data()
    if df.empty:
        st.warning("API'den veri alınamadı veya sonuçlar boş.")
        return

    # KPI kartları
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Toplam Kullanıcı", len(df))
    with col2:
        st.metric("High Value", (df['segment'] == 'High Value').sum())
    with col3:
        st.metric("Medium Value", (df['segment'] == 'Medium Value').sum())
    with col4:
        st.metric("Growth Potential", (df['segment'] == 'Growth Potential').sum())
    with col5:
        st.metric("Churn Risk", (df['segment'] == 'Churn Risk').sum())

    # Segment açıklamaları
    st.write("### Segment Açıklamaları")
    for seg, desc in SEGMENT_DESCRIPTIONS.items():
        st.info(f"**{seg}:** {desc}")

    # Segment bazında event dağılımı
    st.write("## Segment Bazında Ortalama Event Dağılımı")
    event_cols = [col for col in df.columns if col.startswith('count_')]
    segment_event_means = df.groupby('segment')[event_cols].mean().reset_index()
    fig = px.bar(segment_event_means.melt(id_vars='segment'), x='segment', y='value', color='variable', barmode='group',
                 labels={'value':'Ortalama Event', 'variable':'Event Tipi', 'segment':'Segment'})
    st.plotly_chart(fig, use_container_width=True)

    # Korelasyon grafiği
    st.write("## Event Korelasyonu (Tüm Kullanıcılar)")
    corr = df[event_cols].corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto", title="Event Korelasyon Matrisi")
    st.plotly_chart(fig_corr, use_container_width=True)

    # Kullanıcı detay ekranı
    st.write("## Kullanıcı Detayları")
    user_id = st.selectbox("Kullanıcı Seç", df['user_id'])
    user_row = df[df['user_id'] == user_id].T
    st.dataframe(user_row)
    st.write("#### Segment Açıklaması:")
    seg = user_row.loc['segment'].values[0]
    st.success(SEGMENT_DESCRIPTIONS.get(seg, 'Tanımsız'))

    # Segment seçimi
    selected_segment = st.selectbox("Segment Seç (Profil Analizi için)", df['segment'].unique())
    seg_df = df[df['segment'] == selected_segment]

    # Profil özellikleri için bar grafikler
    profile_cols = [col for col in df.columns if col.startswith(('plan_type_', 'country_', 'device_type_', 'industry_'))]
    orig_cols = ['plan_type', 'country', 'device_type', 'industry']
    for orig in orig_cols:
        cols = [c for c in df.columns if c.startswith(f'{orig}_')]
        if cols:
            st.write(f"**{orig.replace('_',' ').title()} Dağılımı ({selected_segment})**")
            val_counts = seg_df[cols].sum().sort_values(ascending=False)
            fig = px.bar(val_counts, x=val_counts.index.str.replace(f'{orig}_',''), y=val_counts.values, labels={'x':orig, 'y':'Kullanıcı Sayısı'})
            st.plotly_chart(fig, use_container_width=True)

    # Tahmin olasılıklarının dağılımı
    if 'pred_churn_prob' in seg_df.columns:
        st.write(f"**Churn Riski Olasılığı Dağılımı ({selected_segment})**")
        fig_hist = px.histogram(seg_df, x='pred_churn_prob', nbins=20, title='Churn Riski Olasılığı')
        st.plotly_chart(fig_hist, use_container_width=True)

    # Kullanıcı detay tablosu
    st.write(f"**{selected_segment} Segmentindeki Kullanıcılar**")
    st.dataframe(seg_df.head(100))

if __name__ == "__main__":
    main()
