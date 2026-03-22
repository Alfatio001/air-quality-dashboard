import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(layout="wide")

# ======================
# 🎨 ULTRA UI CSS
# ======================
st.markdown("""
<style>

/* BACKGROUND */
.main {
    background-color: #0E1117;
}

/* HEADER */
h1 {
    font-size: 36px !important;
    font-weight: 700;
    color: white;
}
h2, h3 {
    color: white;
}

/* CARD STYLE */
.metric-card {
    background: linear-gradient(135deg, #1C1F26, #2A2E38);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
    transition: 0.3s;
}

/* HOVER EFFECT */
.metric-card:hover {
    transform: translateY(-5px);
}

/* SUBTEXT */
.caption {
    color: #aaa;
}

</style>
""", unsafe_allow_html=True)

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    folder_path = "data_air/PRSA_Data_20130301-20170228"
    files = os.listdir(folder_path)

    df_list = []
    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            df_list.append(pd.read_csv(file_path))

    df = pd.concat(df_list, ignore_index=True)

    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df = df.sort_values(by='datetime')

    return df

df = load_data()

# ======================
# SIDEBAR
# ======================
st.sidebar.title("⚙️ Filter")

selected_station = st.sidebar.selectbox(
    "Stasiun Pemantauan Udara",
    sorted(df['station'].unique())
)

station_df = df[df['station'] == selected_station].copy()

# ======================
# HEADER
# ======================
st.markdown("🌍 Air Quality Dashboard")
st.caption("Analisis PM2.5 berbasis waktu dan faktor lingkungan")

# ======================
# METRICS (ULTRA CARD)
# ======================
avg_pm25 = station_df['PM2.5'].mean()
max_pm25 = station_df['PM2.5'].max()

if avg_pm25 <= 50:
    status = "🟢 Baik"
elif avg_pm25 <= 100:
    status = "🟡 Sedang"
else:
    status = "🔴 Buruk"

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="metric-card">
<h4>Rata-rata PM2.5</h4>
<h2>{avg_pm25:.2f}</h2>
<p>{status}</p>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="metric-card">
<h4>PM2.5 Maksimum</h4>
<h2>{max_pm25:.2f}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="metric-card">
<h4>Total Data</h4>
<h2>{len(station_df)}</h2>
</div>
""", unsafe_allow_html=True)

# ======================
# 📈 TREND BULANAN
# ======================
st.markdown("### 📈 Tren PM2.5 (Bulanan)")

monthly_pm25 = station_df.groupby('month')['PM2.5'].mean().reset_index()

fig1 = px.line(
    monthly_pm25,
    x='month',
    y='PM2.5',
    markers=True,
    title="Rata-rata PM2.5 per Bulan"
)

fig1.update_layout(
    template="plotly_dark",
    xaxis_title="Bulan",
    yaxis_title="PM2.5"
)

st.plotly_chart(fig1, use_container_width=True)

# ======================
# 📊 TREND HARIAN
# ======================
st.markdown("### 📊 Tren Harian")

daily_pm25 = station_df.resample('D', on='datetime')['PM2.5'].mean().reset_index()

fig2 = px.line(
    daily_pm25,
    x='datetime',
    y='PM2.5',
    title="PM2.5 Harian"
)

fig2.update_layout(template="plotly_dark")

st.plotly_chart(fig2, use_container_width=True)

# ======================
# 🔥 SCATTER + HEATMAP
# ======================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🌡️ Suhu vs PM2.5")

    fig3 = px.scatter(
        station_df,
        x='TEMP',
        y='PM2.5',
        opacity=0.3
    )

    fig3.update_layout(template="plotly_dark")

    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("### 🔥 Korelasi")

    corr = station_df.corr(numeric_only=True)

    fig4 = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale='RdBu_r'
    )

    fig4.update_layout(template="plotly_dark")

    st.plotly_chart(fig4, use_container_width=True)

# ======================
# 🌫️ KATEGORI
# ======================
st.markdown("### 🌫️ Kualitas Udara")

def kategori_pm25(x):
    if x <= 50:
        return "Baik"
    elif x <= 100:
        return "Sedang"
    else:
        return "Buruk"

station_df['kategori_udara'] = station_df['PM2.5'].apply(kategori_pm25)

fig5 = px.histogram(
    station_df,
    x='kategori_udara',
    color='kategori_udara'
)

fig5.update_layout(template="plotly_dark")

st.plotly_chart(fig5, use_container_width=True)

# ======================
# FOOTER
# ======================
st.markdown("---")
st.caption("🤓 Alfatio Sultansyah | Dashboard Air Quality")