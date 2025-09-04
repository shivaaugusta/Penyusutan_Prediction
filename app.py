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
# Fungsi Load Data
# -------------------------------
@st.cache_data
def load_excel(file):
    return pd.read_excel(file)

# -------------------------------
# Upload File
# -------------------------------
uploaded_file = st.file_uploader("📂 Upload File Excel", type=["xlsx"])

if uploaded_file is not None:
    df = load_excel(uploaded_file)

    # Preview kolom
    st.write("Kolom ditemukan:", df.columns.tolist())

    # -------------------------------
    # Bersihkan Data
    # -------------------------------
    obj_cols = df.select_dtypes(include="object").columns
    if len(obj_cols) > 0:
        mask = df[obj_cols].apply(lambda x: x.str.contains("Subtotal|Total", case=False, na=False)).any(axis=1)
        df = df[~mask]  # hapus subtotal/total

    df = df.dropna(how="all")  # hapus baris kosong

    # Ubah tahun jadi integer
    if "Tahun_Perolehan" in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df["Tahun_Perolehan"]):
            df["Tahun_Perolehan"] = df["Tahun_Perolehan"].dt.year
        df["Tahun_Perolehan"] = df["Tahun_Perolehan"].fillna(0).astype(int)

    # Isi NaN
    if len(obj_cols) > 0:
        df[obj_cols] = df[obj_cols].fillna("-")
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[num_cols] = df[num_cols].fillna(0)

    st.subheader("📄 Preview Dataset")
    st.dataframe(df.head())

    # -------------------------------
    # Ringkasan Total
    # -------------------------------
    st.subheader("📌 Ringkasan Total")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Nilai Perolehan", f"Rp {df.get('Nilai_Perolehan', pd.Series([0])).sum():,.0f}")
    col2.metric("Total Biaya Penyusutan Bulan", f"Rp {df.get('Biaya_Penyusutan_Bulan', pd.Series([0])).sum():,.0f}")
    col3.metric("Total Akumulasi Penyusutan", f"Rp {df.get('Akumulasi_Penyusutan', pd.Series([0])).sum():,.0f}")
    col4.metric("Total Nilai Buku Bulan Ini", f"Rp {df.get('Nilai_Buku_Bulan_Ini', pd.Series([0])).sum():,.0f}")

    # -------------------------------
    # Analisis
    # -------------------------------
    if "Jenis_Aktiva_Tetap" in df.columns and "Biaya_Penyusutan_Bulan" in df.columns:
        st.subheader("📈 Top 10 Jenis Aktiva (Biaya Penyusutan Bulan)")

        biaya_per_jenis = (
            df.groupby("Jenis_Aktiva_Tetap")["Biaya_Penyusutan_Bulan"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        fig1, ax1 = plt.subplots()
        biaya_per_jenis.plot(kind="bar", ax=ax1, color="skyblue", edgecolor="black")
        ax1.set_ylabel("Biaya Penyusutan Bulan (Rp)")
        ax1.set_title("Top 10 Jenis Aktiva")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig1)

    # -------------------------------
    # Prediksi Linear Regression
    # -------------------------------
    st.subheader("🤖 Prediksi Penyusutan Tahun Depan")

    if "Tahun_Perolehan" in df.columns and "Biaya_Penyusutan_Bulan" in df.columns:
        biaya_tahunan = (
            df.groupby("Tahun_Perolehan")["Biaya_Penyusutan_Bulan"]
            .sum()
            .reset_index()
            .sort_values("Tahun_Perolehan")
        )

        if not biaya_tahunan.empty:
            X = biaya_tahunan[["Tahun_Perolehan"]]
            y = biaya_tahunan["Biaya_Penyusutan_Bulan"]

            model = LinearRegression()
            model.fit(X, y)

            tahun_terakhir = int(biaya_tahunan["Tahun_Perolehan"].max())
            tahun_prediksi = np.array([[tahun_terakhir + 1]])
            y_pred = model.predict(tahun_prediksi)[0]

            st.write("📅 Data Biaya Penyusutan Tahunan:")
            st.dataframe(biaya_tahunan)

            st.success(f"Prediksi Biaya Penyusutan Tahun {tahun_terakhir+1}: Rp {y_pred:,.0f}")

            # Plot
            fig2, ax2 = plt.subplots()
            ax2.plot(biaya_tahunan["Tahun_Perolehan"], y, marker="o", label="Aktual", color="blue")
            ax2.plot(tahun_terakhir + 1, y_pred, "rx", label="Prediksi", markersize=12)
            ax2.set_xlabel("Tahun")
            ax2.set_ylabel("Total Biaya Penyusutan (Rp)")
            ax2.set_title("Prediksi Linear Regression")
            ax2.legend()
            st.pyplot(fig2)

            # Tombol download hasil prediksi
            hasil_prediksi = pd.DataFrame({
                "Tahun": [tahun_terakhir + 1],
                "Prediksi_Biaya_Penyusutan": [y_pred]
            })
            st.download_button(
                "⬇️ Download Hasil Prediksi",
                data=hasil_prediksi.to_csv(index=False).encode("utf-8"),
                file_name="prediksi_penyusutan.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Data tahunan kosong, tidak bisa prediksi.")
    else:
        st.warning("⚠️ Kolom 'Tahun_Perolehan' atau 'Biaya_Penyusutan_Bulan' tidak ada di dataset.")

else:
    st.info("⬅️ Silakan upload file Excel untuk mulai analisis & prediksi.")
