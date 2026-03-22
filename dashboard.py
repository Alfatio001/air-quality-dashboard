import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(layout="wide")

# ======================
# 🎨 STYLE
# ======================
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1C1F26, #2A2E38);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

# ======================
# 📥 LOAD DATA
# ======================
@st.cache_data
def load_data():
    folder_path = "PRSA_Data_20130301-20170228"
    files = os.listdir(folder_path)

    df_list = []
    for file in files:
        if file.endswith(".csv"):
            df_list.append(pd.read_csv(os.path.join(folder_path, file)))

    df = pd.concat(df_list, ignore_index=True)
    df['datetime'] = pd.to_datetime(df[['year','month','day','hour']])
    return df

df = load_data()

# ======================
# ⚙️ SIDEBAR
# ======================
st.sidebar.title("⚙️ Filter")

selected_station = st.sidebar.multiselect(
    "Stasiun Pemantauan Udara",
    sorted(df['station'].unique()),
    default=[df['station'].unique()[0]]
)

selected_year = st.sidebar.multiselect(
    "Tahun",
    sorted(df['year'].unique()),
    default=[df['year'].unique()[0]]
)

mode = st.sidebar.selectbox("Mode Grafik", ["Bulanan", "Harian"])

# ======================
# 🔎 FILTER DATA
# ======================
filtered_df = df[
    (df['station'].isin(selected_station)) &
    (df['year'].isin(selected_year))
].copy()

# ======================
# 🧾 HEADER
# ======================
st.title("🌍 Air Quality Dashboard")
st.caption("Analisis PM2.5 berdasarkan waktu, cuaca, dan lokasi")

# ======================
# 📊 KPI
# ======================
avg_pm25 = filtered_df['PM2.5'].mean()
max_pm25 = filtered_df['PM2.5'].max()

status = "🟢 Baik" if avg_pm25 <= 50 else "🟡 Sedang" if avg_pm25 <= 100 else "🔴 Buruk"

col1, col2, col3 = st.columns(3)

col1.markdown(f"<div class='metric-card'><h4>Rata-rata PM2.5</h4><h2>{avg_pm25:.2f}</h2><p>{status}</p></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><h4>PM2.5 Maksimum</h4><h2>{max_pm25:.2f}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><h4>Total Data</h4><h2>{len(filtered_df)}</h2></div>", unsafe_allow_html=True)

# ======================
# 📈 TREND
# ======================
st.subheader("📈 Tren PM2.5")

if mode == "Bulanan":
    trend = filtered_df.groupby(['month','station'])['PM2.5'].mean().reset_index()
    fig = px.line(trend, x='month', y='PM2.5', color='station', markers=True)
else:
    trend = filtered_df.resample('D', on='datetime')['PM2.5'].mean().reset_index()
    fig = px.line(trend, x='datetime', y='PM2.5')

st.plotly_chart(fig, use_container_width=True)

# ======================
# 📊 PERBANDINGAN STATION
# ======================
st.subheader("📊 Perbandingan Antar Stasiun")

compare = filtered_df.groupby('station')['PM2.5'].mean().reset_index()

fig2 = px.bar(compare, x='station', y='PM2.5', color='PM2.5')
st.plotly_chart(fig2, use_container_width=True)

# ======================
# 🌡️ SUHU VS PM2.5
# ======================
st.subheader("🌡️ Hubungan Suhu vs PM2.5")

fig3 = px.scatter(
    filtered_df,
    x='TEMP',
    y='PM2.5',
    color='station',
    opacity=0.4
)

st.plotly_chart(fig3, use_container_width=True)

# ======================
# 🔥 HEATMAP
# ======================
st.subheader("🔥 Korelasi Antar Variabel")

corr = filtered_df.corr(numeric_only=True)

fig4 = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale='RdBu_r'
)

st.plotly_chart(fig4, use_container_width=True)

# ======================
# 🧠 KATEGORI (CLUSTERING)
# ======================
st.subheader("🌫️ Kategori Kualitas Udara")

def kategori(x):
    if x <= 50:
        return "Baik"
    elif x <= 100:
        return "Sedang"
    else:
        return "Buruk"

filtered_df['kategori'] = filtered_df['PM2.5'].apply(kategori)

fig5 = px.histogram(filtered_df, x='kategori', color='kategori')
st.plotly_chart(fig5, use_container_width=True)

# ======================
# 🏆 RANKING
# ======================
st.subheader("🏆 Stasiun Terbaik & Terburuk")

best = compare.sort_values('PM2.5').head(3)
worst = compare.sort_values('PM2.5', ascending=False).head(3)

col1, col2 = st.columns(2)

with col1:
    st.write("🔥 Terburuk")
    st.dataframe(worst)

with col2:
    st.write("🌿 Terbaik")
    st.dataframe(best)

# ======================
# 💡 INSIGHT OTOMATIS
# ======================
st.subheader("💡 Insight Otomatis")

insight = f"""
Rata-rata PM2.5 sebesar {avg_pm25:.2f} ({status}).
Polusi tertinggi mencapai {max_pm25:.2f}.
Station paling tercemar: {worst.iloc[0]['station']}.
Station paling bersih: {best.iloc[0]['station']}.
"""

st.info(insight)

# ======================
# FOOTER
# ======================
st.markdown("---")
st.caption("🚀 Dashboard by Alfatio Sultansyah")