# 🌤️ Air Quality Dashboard — Kota Dongsi (2013–2016)

Dashboard interaktif ini dibuat menggunakan **Streamlit** untuk menganalisis dataset kualitas udara di Kota **Dongsi** selama periode **2013–2016**.  
Dashboard ini menampilkan tren polutan utama seperti **PM2.5**, **PM10**, **SO₂**, **NO₂**, **CO**, dan **O₃**, serta analisis korelasi antar variabel dan pengaruh kecepatan angin (**WSPM**) terhadap konsentrasi polutan.

---

## 🧭 Fitur Utama

✨ **Fitur yang tersedia dalam dashboard ini:**

- 📊 **Visualisasi Rata-rata Polutan** — tren konsentrasi polutan berdasarkan waktu (harian, bulanan, tahunan).
- 🔗 **Korelasi Antar Variabel** — melihat hubungan antar polutan dan faktor cuaca (misalnya suhu & kecepatan angin).
- 💨 **Analisis Airflow (WSPM)** — kategori kecepatan angin otomatis (`Tenang`, `Lemah`, `Sedang`, `Kuat`) dan dampaknya terhadap konsentrasi polutan.
- 🌡️ **Filter Rentang Waktu & Polutan** — pengguna dapat menentukan periode analisis serta memilih polutan yang ingin ditampilkan.

---

## ⚙️ Setup Environment Menggunakan Anaconda

conda create --name airquality-dongsi python=3.9
conda activate airquality-dongsi
pip install -r requirements.txt

---

## ⚙️ Setup Environment Menggunakan Terminal

mkdir air_quality_dashboard
cd air_quality_dashboard
cd dashboard
pip install pipenv
pipenv install
pipenv shell
pip install -r requirements.txt

---

## ⚙️ Jalankan Dashboard Streamlit

streamlit run streamlit run dashboard.py
