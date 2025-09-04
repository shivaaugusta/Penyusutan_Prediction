import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Dashboard Aktiva", layout="wide")

st.title("📊 Dashboard Analisis & Prediksi Biaya Penyusutan")

# Upload file
uploaded_file = st.sidebar.file_uploader("Upload File Excel", type=["xlsx"])

# Pilih menu
menu = st.sidebar.selectbox("Pilih Menu", ["Analisis", "Prediksi"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df = df.dropna(how="all").fillna(0)

    if menu == "Analisis":
        st.subheader("📌 Ringkasan Data")
        col1, col2 = st.columns(2)
        col1.metric("Total Perolehan", f"Rp {df['Perolehan'].sum():,.0f}")
        col2.metric("Total Penyusutan", f"Rp {df['Penyusutan'].sum():,.0f}")

        st.subheader("📈 Visualisasi")
        top10 = df.groupby("Jenis Aktiva")["Perolehan"].sum().nlargest(10)
        fig, ax = plt.subplots()
        top10.plot(kind="bar", ax=ax)
        st.pyplot(fig)

    elif menu == "Prediksi":
        st.subheader("🔮 Prediksi Biaya Penyusutan")
        # Ambil data per tahun
        if "Tahun" in df.columns:
            data_tahunan = df.groupby("Tahun")["Penyusutan"].sum().reset_index()

            # Linear Regression
            X = data_tahunan[["Tahun"]]
            y = data_tahunan["Penyusutan"]
            model = LinearRegression().fit(X, y)

            next_year = data_tahunan["Tahun"].max() + 1
            prediksi = model.predict([[next_year]])[0]

            st.write(f"📅 Prediksi biaya penyusutan tahun {next_year}: **Rp {prediksi:,.0f}**")

            # Visualisasi
            fig, ax = plt.subplots()
            ax.plot(data_tahunan["Tahun"], y, marker="o", label="Data Aktual")
            ax.plot([next_year], [prediksi], "ro", label="Prediksi")
            ax.legend()
            st.pyplot(fig)
        else:
            st.warning("Dataset tidak memiliki kolom 'Tahun'.")
else:
    st.info("⬅️ Silakan upload file Excel terlebih dahulu.")
