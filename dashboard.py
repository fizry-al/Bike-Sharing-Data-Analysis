import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ======================
# CONFIG & STYLE
# ======================
st.set_page_config(page_title="Analisis Penyewaan Sepeda", layout="wide")

# Custom CSS untuk tampilan lebih clean
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 28px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('hour.csv')
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    # Terjemahan pemetaan cuaca
    weather_map = {
        1: 'Cerah', 
        2: 'Berkabut', 
        3: 'Hujan/Salju Ringan', 
        4: 'Hujan/Salju Lebat'
    }
    df['weathersit'] = df['weathersit'].map(weather_map)
    df.rename(columns={'hr': 'hour', 'cnt': 'total_rentals'}, inplace=True)
    return df

df = load_data()

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.title("Filter")
    selected_weather = st.multiselect(
        "Kondisi Cuaca",
        options=df['weathersit'].unique(),
        default=df['weathersit'].unique()
    )
    
    selected_hour = st.select_slider(
        "Rentang Jam",
        options=list(range(24)),
        value=(0, 23)
    )
    
    day_type = st.radio(
        "Tipe Hari",
        options=["Semua Hari", "Hari Kerja", "Hari Libur"],
        index=0
    )

# Logic Filter
filtered_df = df[
    (df['weathersit'].isin(selected_weather)) &
    (df['hour'] >= selected_hour[0]) &
    (df['hour'] <= selected_hour[1])
]

if day_type == "Hari Kerja":
    filtered_df = filtered_df[filtered_df['workingday'] == 1]
elif day_type == "Hari Libur":
    filtered_df = filtered_df[filtered_df['workingday'] == 0]

# ======================
# MAIN CONTENT
# ======================
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis pola penyewaan per jam dan dampak kondisi cuaca terhadap permintaan.")

# KPI Metrics
total_rentals = filtered_df['total_rentals'].sum()
avg_rentals = filtered_df['total_rentals'].mean()
peak_hour = filtered_df.groupby('hour')['total_rentals'].mean().idxmax()

m1, m2, m3 = st.columns(3)
m1.metric("Total Penyewaan", f"{total_rentals:,}")
m2.metric("Rata-rata per Jam", f"{avg_rentals:.1f}")
m3.metric("Jam Puncak", f"{peak_hour}:00")

st.divider()

# Visualizations
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Tren Penyewaan per Jam")
    hourly_data = filtered_df.groupby('hour')['total_rentals'].mean()
    
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(x=hourly_data.index, y=hourly_data.values, color='#2c3e50', linewidth=2, ax=ax)
    ax.fill_between(hourly_data.index, hourly_data.values, color='#3498db', alpha=0.1)
    
    # Clean spines (menghilangkan garis tepi agar minimalis)
    sns.despine()
    ax.set_ylabel("Jumlah Sepeda Disewa")
    ax.set_xlabel("Jam")
    st.pyplot(fig)

with col_right:
    st.subheader("Dampak Cuaca")
    weather_data = filtered_df.groupby('weathersit')['total_rentals'].mean().sort_values(ascending=False)
    
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    # Menggunakan hue agar tidak memunculkan peringatan (warning) pada versi seaborn terbaru
    sns.barplot(x=weather_data.index, y=weather_data.values, hue=weather_data.index, palette="Blues_r", legend=False, ax=ax2)
    
    sns.despine()
    ax2.set_ylabel("")
    ax2.set_xlabel("")
    st.pyplot(fig2)

# ======================
# INSIGHTS
# ======================
with st.expander("Tampilkan Temuan Utama", expanded=True):
    st.write(f"""
    * **Lonjakan Permintaan:** Aktivitas tertinggi pada jam **{peak_hour}:00** dengan rata-rata sekitar **{int(hourly_data.max())} sepeda per jam**.
    * **Faktor Lingkungan:** Pengguna menunjukkan preferensi penyewaan yang kuat pada kondisi cuaca **{weather_data.idxmax()}**.
    * **Rekomendasi Operasional:** Pastikan ketersediaan unit sepeda di titik-titik penyewaan setidaknya 1-2 jam sebelum periode jam puncak tersebut.
    """)