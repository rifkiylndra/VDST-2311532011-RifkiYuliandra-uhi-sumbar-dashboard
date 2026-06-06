"""
pages/1_📊_Tren_LST.py
Halaman tren historis LST 2015–2025
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
sys.path.append(".")
from utils.data_loader import load_panel, load_forecast, KOTA_LIST

st.set_page_config(page_title="Tren LST | UHI Sumbar", page_icon="📊", layout="wide")
st.title("📊 Tren Land Surface Temperature (LST) — 2015–2025")
st.caption("Perbandingan tren suhu permukaan historis antar 7 kota administratif Sumatera Barat")

df      = load_panel()
df_fore = load_forecast()

# ── Sidebar filter ──
st.sidebar.header("⚙️ Filter")
kota_sel = st.sidebar.multiselect(
    "Pilih kota", KOTA_LIST, default=KOTA_LIST
)
metric = st.sidebar.selectbox(
    "Metrik",
    ["lst_c_mean", "uhi_intensity", "delta_lst"],
    format_func=lambda x: {
        "lst_c_mean":    "LST Rata-rata (°C)",
        "uhi_intensity": "UHI Intensity (°C)",
        "delta_lst":     "Δ LST vs Baseline 2015 (°C)",
    }[x]
)

metric_label = {
    "lst_c_mean":    "LST Rata-rata (°C)",
    "uhi_intensity": "UHI Intensity (°C)",
    "delta_lst":     "Δ LST vs Baseline 2015 (°C)",
}[metric]

df_fil = df[df["kota"].isin(kota_sel)].sort_values("year")

# ── Plot 1: Tren multi-kota ──
st.subheader("Tren LST Per Kota (2015–2025)")

fig = px.line(
    df_fil, x="year", y=metric, color="kota",
    markers=True, line_shape="spline",
    color_discrete_sequence=px.colors.qualitative.Set2,
    labels={"year": "Tahun", metric: metric_label, "kota": "Kota"},
    title=f"{metric_label} — 7 Kota Sumatera Barat"
)
fig.update_traces(line_width=2.5, marker_size=7)
fig.update_layout(
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.2),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(tickmode="linear", dtick=1, gridcolor="#f0f0f0"),
    yaxis=dict(gridcolor="#f0f0f0"),
)
st.plotly_chart(fig, use_container_width=True)

# ── Plot 2: Heatmap LST per kota per tahun ──
st.subheader("Heatmap LST — Kota vs Tahun")

pivot_heat = df[df["kota"].isin(kota_sel)].pivot_table(
    index="kota", columns="year", values="lst_c_mean", aggfunc="mean"
).round(2)

fig2 = px.imshow(
    pivot_heat,
    color_continuous_scale="YlOrRd",
    labels=dict(x="Tahun", y="Kota", color="LST (°C)"),
    title="Heatmap LST Rata-rata (°C) per Kota per Tahun",
    text_auto=True,
    aspect="auto"
)
fig2.update_layout(coloraxis_colorbar_title="LST (°C)")
st.plotly_chart(fig2, use_container_width=True)

# ── Plot 3: Bar chart perbandingan tahun tertentu ──
st.subheader("Perbandingan LST Antar Kota per Tahun")

col1, col2 = st.columns([1, 3])
with col1:
    year_sel = st.selectbox("Pilih tahun:", sorted(df["year"].unique(), reverse=True))

df_yr = df[(df["kota"].isin(kota_sel)) & (df["year"] == year_sel)].sort_values("lst_c_mean", ascending=False)

with col2:
    fig3 = px.bar(
        df_yr, x="kota", y="lst_c_mean",
        color="lst_c_mean",
        color_continuous_scale="YlOrRd",
        labels={"kota": "Kota", "lst_c_mean": "LST (°C)"},
        title=f"LST Rata-rata per Kota — Tahun {year_sel}",
        text_auto=".1f"
    )
    fig3.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

# ── Tabel ringkasan statistik ──
st.subheader("📋 Tabel Statistik Ringkasan")
summary = (
    df[df["kota"].isin(kota_sel)]
    .groupby("kota")[["lst_c_mean", "uhi_intensity", "delta_lst"]]
    .agg(["mean", "min", "max"])
    .round(3)
)
summary.columns = [" ".join(c) for c in summary.columns]
st.dataframe(summary.style.background_gradient(
    subset=[c for c in summary.columns if "mean" in c], cmap="YlOrRd"
), use_container_width=True)
