import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

st.title("📊 Analisis & Prediksi Biaya Penyusutan")

# Upload file Excel
uploaded_file = st.file_uploader("Upload dataset Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("📑 Data Asli")
    st.dataframe(df.head())

    # Pastikan ada kolom Tahun_Perolehan dan Biaya Penyusutan
    if "Tahun_Perolehan" in df.columns and "Biaya_Penyusutan_Sampai_Bulan" in df.columns:
        data = df.groupby("Tahun_Perolehan")["Biaya_Penyusutan_Sampai_Bulan"].sum().reset_index()
        
        st.subheader("📈 Total Biaya Penyusutan per Tahun")
        st.line_chart(data.set_index("Tahun_Perolehan"))

        # Pilih metode prediksi
        model_choice = st.selectbox("Pilih metode prediksi:", 
                                    ["Regresi Linier", "Random Forest", "ARIMA"])

        X = data[["Tahun_Perolehan"]]
        y = data["Biaya_Penyusutan_Sampai_Bulan"]

        next_year = data["Tahun_Perolehan"].max() + 1

        if model_choice == "Regresi Linier":
            model = LinearRegression()
            model.fit(X, y)
            pred = model.predict([[next_year]])

        elif model_choice == "Random Forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            pred = model.predict([[next_year]])

        elif model_choice == "ARIMA":
            # Gunakan ARIMA (1,1,1) contoh sederhana
            model = ARIMA(y, order=(1,1,1))
            model_fit = model.fit()
            pred = model_fit.forecast(steps=1)

        st.subheader("🔮 Hasil Prediksi")
        st.write(f"Prediksi biaya penyusutan tahun {next_year}: **Rp {pred[0]:,.0f}**")

        # Plot hasil prediksi
        plt.figure(figsize=(8,5))
        plt.plot(data["Tahun_Perolehan"], y, marker="o", label="Data Historis")
        plt.axvline(next_year, color="gray", linestyle="--")
        plt.scatter(next_year, pred, color="red", label="Prediksi")
        plt.legend()
        st.pyplot(plt)

    else:
        st.error("Dataset harus punya kolom 'Tahun_Perolehan' dan 'Biaya_Penyusutan_Sampai_Bulan'")
