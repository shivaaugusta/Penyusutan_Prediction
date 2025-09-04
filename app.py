import streamlit as st
import pandas as pd

# Load data
df = pd.read_excel("data/sample.xlsx")

# Bersihin spasi di nama kolom (kadang ada trailing space)
df.columns = df.columns.str.strip()

st.write("Kolom tersedia di dataset:", df.columns.tolist())

# --- Cek apakah kolom yang dibutuhkan ada ---
required_cols = ["Perolehan", "Penyusutan"]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Kolom berikut tidak ditemukan di dataset: {missing_cols}")
    st.stop()  # hentikan app biar gak error di bawah

# --- Kalau kolom aman, tampilkan metrik ---
col1, col2 = st.columns(2)

col1.metric("Total Perolehan", f"Rp {df['Perolehan'].sum():,.0f}")
col2.metric("Total Penyusutan", f"Rp {df['Penyusutan'].sum():,.0f}")

st.success("Data berhasil dimuat ✅")
st.dataframe(df.head())

