import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# -------------------------------
# Konfigurasi App
# -------------------------------
st.set_page_config(page_title="Dashboard Penyusutan Aset", layout="wide")
st.title("📊 Dashboard Analisis & Prediksi Penyusutan Aset")

# -------------------------------
# Upload File
# -------------------------------
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Preview kolom
    st.write("Kolom ditemukan:", df.columns.tolist())

    # -------------------------------
    # Bersihkan Data
    # -------------------------------
    obj_cols = df.select_dtypes(include="object").columns
    mask = df[obj_cols].apply(lambda x: x.str.contains("Subtotal|Total", case=False, na=False)).any(axis=1)
    df = df[~mask]  # hapus subtotal/total
    df = df.dropna(how="all")  # hapus baris kosong

    # Ubah tahun
    if pd.api.types.is_datetime64_any_dtype(df["Tahun_Perolehan"]):
        df["Tahun_Perolehan"] = df["Tahun_Perolehan"].dt.year

    # Isi NaN
    df[obj_cols] = df[obj_cols].fillna("-")
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[num_cols] = df[num_cols].fillna(0)

    st.subheader("Preview Dataset")
    st.dataframe(df.head())

    # -------------------------------
    # Ringkasan Total
    # -------------------------------
    st.subheader("📌 Ringkasan Total")
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Nilai Perolehan", f"Rp {df['Nilai_Perolehan'].sum():,.0f}")
    col2.metric("Total Biaya Penyusutan Bulan", f"Rp {df['Biaya_Penyusutan_Bulan'].sum():,.0f}")
    col3.metric("Total Akumulasi Penyusutan", f"Rp {df['Akumulasi_Penyusutan'].sum():,.0f}")

    # -------------------------------
    # Analisis
    # -------------------------------
    st.subheader("📈 Analisis Data")

    # Top 10 Jenis Aktiva
    biaya_per_jenis = (
        df.groupby("Jenis_Aktiva_Tetap")["Biaya_Penyusutan_Bulan"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    fig1, ax1 = plt.subplots()
    biaya_per_jenis.plot(kind="bar", ax=ax1)
    ax1.set_ylabel("Biaya Penyusutan Bulan (Rp)")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig1)

    # -------------------------------
    # Prediksi Linear Regression
    # -------------------------------
    st.subheader("🤖 Prediksi Penyusutan Tahun Depan")

    if "Tahun_Perolehan" in df.columns:
        # Ambil data tahun & biaya penyusutan total per tahun
        biaya_tahunan = (
            df.groupby("Tahun_Perolehan")["Biaya_Penyusutan_Bulan"]
            .sum()
            .reset_index()
            .sort_values("Tahun_Perolehan")
        )

        X = biaya_tahunan[["Tahun_Perolehan"]]
        y = biaya_tahunan["Biaya_Penyusutan_Bulan"]

        model = LinearRegression()
        model.fit(X, y)

        tahun_terakhir = int(biaya_tahunan["Tahun_Perolehan"].max())
        tahun_prediksi = np.array([[tahun_terakhir + 1]])
        y_pred = model.predict(tahun_prediksi)[0]

        st.write("Data Biaya Penyusutan Tahunan:")
        st.dataframe(biaya_tahunan)

        st.success(f"📅 Prediksi Biaya Penyusutan Tahun {tahun_terakhir+1}: Rp {y_pred:,.0f}")

        # Plot
        fig2, ax2 = plt.subplots()
        ax2.plot(biaya_tahunan["Tahun_Perolehan"], y, marker="o", label="Aktual")
        ax2.plot(tahun_terakhir + 1, y_pred, "rx", label="Prediksi", markersize=12)
        ax2.set_xlabel("Tahun")
        ax2.set_ylabel("Total Biaya Penyusutan (Rp)")
        ax2.legend()
        st.pyplot(fig2)

    else:
        st.warning("⚠️ Kolom 'Tahun_Perolehan' tidak ada di dataset, jadi prediksi tidak bisa dijalankan.")

else:
    st.info("⬅️ Silakan upload file Excel untuk mulai analisis & prediksi.")
