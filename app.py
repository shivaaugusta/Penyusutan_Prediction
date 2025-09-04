import streamlit as st
import pandas as pd

st.title("Analisis & Prediksi Penyusutan")

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()  # bersihin spasi

    st.write("Kolom tersedia:", df.columns.tolist())
    st.dataframe(df.head())
else:
    st.warning("Silakan upload file Excel terlebih dahulu.")

