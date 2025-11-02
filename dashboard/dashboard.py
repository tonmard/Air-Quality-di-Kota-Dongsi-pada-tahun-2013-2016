# dashboard.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

sns.set(style='darkgrid')
st.set_page_config(page_title="Air Quality Dongsi 2013-2016", layout="wide")

# Fungsi rata-rata polutan
def create_pollutant_mean_df(df, time_level="year", pollutant_cols=None):
    if "datetime" not in df.columns:
        if all(c in df.columns for c in ["year","month","day","hour"]):
            df = df.copy()
            df["datetime"] = pd.to_datetime(df[["year","month","day","hour"]], errors="coerce")
        elif all(c in df.columns for c in ["year","month","day"]):
            df = df.copy()
            df["datetime"] = pd.to_datetime(df[["year","month","day"]], errors="coerce")
        else:
            raise ValueError("Tidak menemukan kolom datetime atau komponen waktu year/month/day[(hour)].")

    df2 = df.copy()
    df2["datetime"] = pd.to_datetime(df2["datetime"], errors="coerce")
    df2 = df2.dropna(subset=["datetime"])

    rule_map = {"hour":"H", "day":"D", "month":"M", "year":"Y"}
    if time_level not in rule_map:
        raise ValueError("time_level harus salah satu dari: 'hour','day','month','year'")

    possible = ["PM2.5","PM10","SO2","NO2","CO","O3"]
    if pollutant_cols is None:
        pollutant_cols = [c for c in possible if c in df2.columns]
    else:
        pollutant_cols = [c for c in pollutant_cols if c in df2.columns]

    if not pollutant_cols:
        raise ValueError("Tidak ada kolom polutan ditemukan di dataset.")

    df2 = df2.set_index("datetime")
    res = df2[pollutant_cols].resample(rule_map[time_level]).mean().reset_index()
    res.rename(columns={c:f"{c}_mean" for c in pollutant_cols}, inplace=True)
    return res

# Load dataset
all_df = pd.read_csv("Airflow_Dongsi.csv")

# sort dan reset index
all_df = all_df.sort_values("datetime").reset_index(drop=True)
all_df["datetime"] = pd.to_datetime(all_df["datetime"], errors="coerce")

# Sidebar controls
st.sidebar.header("Filters")
min_date = all_df["datetime"].min().date()
max_date = all_df["datetime"].max().date()
start_date, end_date = st.sidebar.date_input(
    "Rentang Waktu",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)
time_level = st.sidebar.selectbox("Level waktu agregasi", options=["day","month","year"], index=1)

# otomatis list polutan yang ada
available_pollutants = [c for c in ["PM2.5","PM10","SO2","NO2","CO","O3"] if c in all_df.columns]
pollutant_sel = st.sidebar.multiselect("Pilih polutan (kosong = semua)", options=available_pollutants, default=available_pollutants[:2])

# Filter dataframe by date range
mask = (all_df["datetime"].dt.date >= start_date) & (all_df["datetime"].dt.date <= end_date)
main_df = all_df.loc[mask].copy()

# Aggregation
agg_df = create_pollutant_mean_df(main_df, time_level=time_level, pollutant_cols=pollutant_sel if pollutant_sel else None)

#Visualisasi Dashboard
st.title("Proyek Data Analisis — Air Quality Kota Dongsi (2013-2016) 🌤️")
st.markdown(f"Periode dipilih: **{start_date}** sampai **{end_date}** — Rekaman: **{len(main_df):,}**")

# Plot: garis rata-rata polutan (time series)
st.subheader("Trend Rata-rata Polutan 📊")
fig, ax = plt.subplots(figsize=(12,5))
mean_cols = [c for c in agg_df.columns if c.endswith("_mean")]
for col in mean_cols:
    sns.lineplot(data=agg_df, x="datetime", y=col, marker="o", label=col.replace("_mean",""), ax=ax)
ax.set_xlabel("Waktu")
ax.set_ylabel("Konsentrasi Polutan")
ax.legend(title="")
ax.grid(True, linestyle="--", alpha=0.5)
plt.xticks(rotation=25)
st.pyplot(fig)

# Plot: rata-rata per tahun (jika ada)
if "PM2.5" in all_df.columns or "PM10" in all_df.columns:
    st.subheader("Rata-rata Tahunan PM2.5 & PM10")
    yearly = create_pollutant_mean_df(main_df, time_level="year", pollutant_cols=[c for c in ["PM2.5","PM10"] if c in main_df.columns])
    st.dataframe(yearly.head())
    fig2, ax2 = plt.subplots(figsize=(10,4))
    if "PM2.5_mean" in yearly.columns:
        sns.lineplot(data=yearly, x="datetime", y="PM2.5_mean", marker="o", label="PM2.5", ax=ax2)
    if "PM10_mean" in yearly.columns:
        sns.lineplot(data=yearly, x="datetime", y="PM10_mean", marker="o", label="PM10", ax=ax2)
    ax2.set_xlabel("Waktu"); ax2.set_ylabel("Konsentrasi (µg/m³)")
    ax2.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig2)

# Korelasi
st.subheader("Korelasi Singkat Antar Variabel Secara Keseluruhan 🔗")
corr_cols = [c for c in ["PM2.5","PM10","SO2","NO2","CO","O3","TEMP","WSPM"] if c in main_df.columns]
if len(corr_cols) >= 2:
    corr = main_df[corr_cols].corr()
    figc, axc = plt.subplots(figsize=(8,6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=axc)
    axc.set_title("Korelasi")
    st.pyplot(figc)
else:
    st.info("Tidak cukup kolom numerik untuk menghitung korelasi.")

# Analisis Airflow (selalu tampil, fixed bins & labels)
st.subheader("Analisis Polutan berdasarkan Kategori Kecepatan Angin (WSPM) 💨")

# Parameter label untuk kategori
WSPM_BINS = [0, 1, 3, 5, 10]
WSPM_LABELS = ["Tenang", "Lemah", "Sedang", "Kuat"]

if "WSPM" not in main_df.columns:
    st.info("Kolom 'WSPM' tidak ditemukan di dataset — tidak dapat membuat kategori airflow.")
else:
    default_pol = [c for c in ["PM2.5", "NO2"] if c in main_df.columns]
    polutan_for_airflow = st.multiselect("Pilih polutan untuk analisis airflow:", options=available_pollutants, default=default_pol)
    
    if not polutan_for_airflow:
        st.warning("Pilih minimal satu polutan untuk analisis.")
    else:
        tmp = main_df[["WSPM"] + polutan_for_airflow].copy()
        tmp = tmp.dropna(subset=["WSPM"])

        # gunakan bins & labels yang tetap
        tmp["wind_category"] = pd.cut(tmp["WSPM"], bins=WSPM_BINS, labels=WSPM_LABELS, include_lowest=True)

        airflow_cluster = tmp.groupby("wind_category", observed=True)[polutan_for_airflow].mean().reset_index()

        st.markdown("**Rata-rata polutan per kategori kecepatan angin**")
        st.dataframe(airflow_cluster.style.format(precision=2))

        # Plot: bar chart per polutan (horizontal)
        fig_a, axes = plt.subplots(nrows=1, ncols=len(polutan_for_airflow), figsize=(6*len(polutan_for_airflow), 4), constrained_layout=True)
        if len(polutan_for_airflow) == 1:
            axes = [axes]
        palette = sns.color_palette("muted")
        for ax, pol, pal in zip(axes, polutan_for_airflow, palette):
            sns.barplot(data=airflow_cluster.sort_values(by=pol), x=pol, y="wind_category", ax=ax, palette=[pal])
            ax.set_xlabel(f"Rata-rata {pol}")
            ax.set_ylabel("")
            ax.set_title(pol)
        st.pyplot(fig_a)

        # Ringkasan: kategori tertinggi per polutan
        summary = []
        for pol in polutan_for_airflow:
            if airflow_cluster[pol].dropna().empty:
                continue
            max_idx = airflow_cluster[pol].idxmax()
            max_row = airflow_cluster.loc[max_idx]
            summary.append(f"- **{pol}** terbesar pada kategori **{max_row['wind_category']}**: {max_row[pol]:.2f}")
        if summary:
            st.markdown("**Ringkasan:**")
            for s in summary:
                st.markdown(s)

# Footer
st.caption("Dashboard sederhana — Air Quality Dataset di Kota Dongsi pada tahun 2013-2016 © Tony Mardyansyah")
