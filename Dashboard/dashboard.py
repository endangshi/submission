import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "main_data.csv")
    df = pd.read_csv(file_path)
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['workingday'] = df['workingday'].replace({0:'Weekend', 1:'Working Day'})
    return df

def filter_data(df, start_date, end_date):
    df_filtered = df[
        (df['dteday'] >= pd.to_datetime(start_date)) &
        (df['dteday'] <= pd.to_datetime(end_date))
    ].copy()
    return df_filtered.dropna(subset=['workingday', 'cnt'])

def create_avg_workingday(df):
    avg = df.groupby('workingday')['cnt'].mean()
    return avg.reindex(['Working Day', 'Weekend'])

def create_yearly_avg(df, year):
    df_year = df[df['dteday'].dt.year == year]
    return df_year.groupby('workingday')['cnt'].mean().reindex(['Working Day','Weekend'])

def create_correlation(df, year):
    df_year = df[df['dteday'].dt.year == year]
    return df_year[['temp','hum','cnt']].corr()

def create_monthly_trend(df):
    df = df.copy()
    df['month'] = df['dteday'].dt.to_period('M')
    return df.groupby('month')['cnt'].mean()

df = load_data()

st.title("Analisis Peminjaman Sepeda Tahun 2011-2012")

st.sidebar.header("Silakan Masukkan Rentang Tanggal")

start_date = st.sidebar.date_input("Tanggal Awal", value=df['dteday'].min())
end_date = st.sidebar.date_input("Tanggal Akhir", value=df['dteday'].max())

df_filtered = filter_data(df, start_date, end_date)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Peminjaman Sepeda",
    "Statistika Deskriptif",
    "Rata-rata",
    "Korelasi",
    "Tren"
])

with tab1:
    st.subheader("Peminjaman Sepeda Berdasarkan Working Day vs Weekend")

    if df_filtered.empty:
        st.info("Silakan pilih rentang tanggal yang sesuai untuk melihat data.")
    else:
        avg_filtered = create_avg_workingday(df_filtered)

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Rata-rata Working Day",
                f"{int(avg_filtered['Working Day']):,}" if pd.notna(avg_filtered['Working Day']) else "-"
            )

        with col2:
            st.metric(
                "Rata-rata Weekend",
                f"{int(avg_filtered['Weekend']):,}" if pd.notna(avg_filtered['Weekend']) else "-"
            )

        st.divider()

        fig, ax = plt.subplots()
        sns.barplot(
            x=avg_filtered.index,
            y=avg_filtered.values,
            palette=['#1f77b4', '#ff7f0e'],
            ax=ax
        )
        ax.set_title("Perbandingan Rata-rata Peminjaman Sepeda")
        st.pyplot(fig)
    
with tab2:
    st.subheader("Statistika Deskriptif")
    st.write(df.describe())
    st.write(
    """
    Berdasarkan hasil statistika deskriptif didapat:
    - Rata-rata nilai workingday adalah 0,683995 yang menunjukkan bahwa sekitar 68% digunakan pada workingday dan sisanya yaitu sekitar 32% digunakan pada weekend atau holiday.
    - Rata-rata peminjaman sepeda adalah sebesar 4504,348837 per hari, dengan nilai minimum 22 dan maksimum 8714.
    - Rentang nilai suhu yaitu diantara 0,059130 - 0,861667 dengan rata-rata 0,495385 dan rentang nilai keelembapan diantara 0 - 0,972500 dengan rata-rata 0,627894.
    """)

with tab3:
    avg_2011 = create_yearly_avg(df, 2011)
    avg_2012 = create_yearly_avg(df, 2012)

    col1, col2 = st.columns(2)

    with col1:
        st.write("Tahun 2011")
        st.dataframe(avg_2011.rename("Rata-rata"))

    with col2:
        st.write("Tahun 2012")
        st.dataframe(avg_2012.rename("Rata-rata"))

    avg_compare = pd.DataFrame({
        '2011': avg_2011,
        '2012': avg_2012
    })

    fig, ax = plt.subplots()
    avg_compare.plot(kind='bar', ax=ax)
    st.pyplot(fig)

    st.write(
    """
    Berdasarkan hasil analisis:
    - Pada tahun 2011 rata-rata jumlah peminjaman sepeda pada akhir pekan adalah 3363,82 sedangkan pada hari kerja sebesar 3425,06. Perbedaan ini relatif kecil, menunjukkan bahwa pada tahun tersebut pola penggunaan sepeda antara hari kerja dan akhir pekan masih cenderung seimbang.
    - Pada tahun 2012 terjadi peningkatan yang cukup signifikan pada kedua kategori, di mana rata-rata peminjaman pada akhir pekan meningkat menjadi 5288,19 dan pada hari kerja meningkat menjadi 5744,58. Selain mengalami kenaikan jumlah peminjaman secara keseluruhan, selisih antara hari kerja dan akhir pekan juga menjadi lebih besar dibanding tahun 2011. Hal ini menunjukkan bahwa pada tahun 2012 terjadi peningkatan penggunaan sepeda secara umum, dengan kecenderungan yang lebih kuat pada hari kerja, yang mengindikasikan bahwa sepeda semakin banyak digunakan sebagai sarana transportasi rutin seperti aktivitas bekerja atau bersekolah
    """)
    
with tab4:
    st.subheader("Korelasi")

    corr_2011 = create_correlation(df, 2011)
    corr_2012 = create_correlation(df, 2012)

    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots()
        sns.heatmap(corr_2011, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax1)
        ax1.set_title("2011")
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        sns.heatmap(corr_2012, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax2)
        ax2.set_title("2012")
        st.pyplot(fig2)
    
    st.write(
    """
    Berdasarkan hasil analisis:
    - Pada tahun 2011 suhu memiliki hubungan positif yang cukup kuat dengan jumlah peminjaman sepeda dengan nilai korelasi sebesar 0,771214. Hal ini menunjukkan bahwa semakin tinggi suhu, maka jumlah peminjaman sepeda cenderung meningkat. Sementara itu, kelembapan memiliki hubungan yang sangat lemah dengan jumlah peminjaman sepeda, dengan nilai korelasi mendekati nol yaitu 0,001898, yang berarti kelembapan hampir tidak berpengaruh pada tahun tersebut.
    - Pada tahun 2012, pola yang serupa masih terlihat, di mana suhu tetap memiliki hubungan positif yang cukup kuat dengan jumlah peminjaman sepeda yaitu sebesar 0,713793, meskipun sedikit menurun dibandingkan tahun 2011. Sebaliknya, kelembapan menunjukkan korelasi negatif yang sangat lemah yaitu sebesar -0,088861), yang mengindikasikan bahwa peningkatan kelembapan sedikit cenderung diikuti oleh penurunan jumlah peminjaman, meskipun pengaruhnya tidak signifikan.
    """)

with tab5:
    st.subheader("Tren Peminjaman Sepeda per-Bulan")

    monthly = create_monthly_trend(df)

    fig, ax = plt.subplots()
    ax.plot(monthly.index.astype(str), monthly.values, marker='o')
    plt.xticks(rotation=90)
    st.pyplot(fig)
    
    st.write(
    """
    Jumlah peminjaman sepeda menunjukkan tren yang meningkat dari tahun 2011 ke 2012 dengan pola yang cukup jelas dipengaruhi oleh musim. Pada tahun 2011, jumlah peminjaman masih relatif rendah di awal tahun, kemudian meningkat secara bertahap hingga mencapai puncak sekitar pertengahan tahun, sebelum kembali menurun menjelang akhir tahun. Sementara itu, pada tahun 2012 terlihat peningkatan yang lebih signifikan dibandingkan 2011, dengan lonjakan peminjaman mulai awal hingga pertengahan tahun dan mencapai puncak tertinggi pada sekitar bulan September, sebelum kembali menurun di akhir tahun. Pola ini menunjukkan adanya pengaruh musim terhadap penggunaan sepeda, di mana peminjaman cenderung lebih tinggi pada bulan-bulan dengan kondisi cuaca yang lebih mendukung pada suhu hanggat ke panas, dan menurun pada bulan yang lebih dingin.
    """)
    
st.caption('Copyright (c) CDCC229D6Y2242')
