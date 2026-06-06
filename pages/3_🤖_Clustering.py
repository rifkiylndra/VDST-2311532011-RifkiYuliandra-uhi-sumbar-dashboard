"""
pages/3_🤖_Clustering.py
Hasil K-Means: peta zona UHI + analisis cluster
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
sys.path.append(".")
from utils.data_loader import load_panel, load_geodata, KOTA_LIST
from utils.map_utils import base_map, choropleth_cluster

st.set_page_config(page_title="Clustering | UHI Sumbar", page_icon="🤖", layout="wide")
st.title("🤖 Clustering Spasial — Zona Urban Heat Island")
st.caption("Hasil K-Means Clustering (k=3) berdasarkan pola LST multi-tahun 2015–2025")

df  = load_panel()
gdf = load_geodata()

# Ambil zona dari data (tiap kota punya 1 zona)
zona_df = df[["kota","zona_uhi","cluster"]].drop_duplicates(subset=["kota"])
gdf_cluster = gdf.merge(zona_df, on="kota", how="left")
# Tambah rata-rata LST untuk tooltip
lst_mean = df.groupby("kota")["lst_c_mean"].mean().reset_index().rename(
    columns={"lst_c_mean": "lst_c_mean"})
gdf_cluster = gdf_cluster.merge(lst_mean, on="kota", how="left")

# ── Ringkasan hasil ──
col_info, col_metric = st.columns([2, 1])

with col_info:
    st.markdown("### Hasil K-Means (k = 3)")
    st.markdown("""
    | Zona | Kota | Karakteristik |
    |------|------|---------------|
    | 🔴 UHI Intensif | Bukittinggi, Padang, Pariaman, Payakumbuh | LST tinggi konsisten, padat urban |
    | 🟡 UHI Sedang   | Sawahlunto, Solok | Campuran urban-vegetasi |
    | 🟢 UHI Rendah   | Padang Panjang | Elevasi tinggi, vegetasi relatif lebih rapat |
    """)

with col_metric:
    st.metric("k Optimal", "3")
    st.metric("Silhouette Score", "0.4157", delta="Kategori: Baik")
    st.metric("Total Kota", "7")

st.divider()

# ── Layout: peta + box plot ──
map_col, chart_col = st.columns([1.3, 1])

with map_col:
    st.subheader("🗺️ Peta Zona UHI")
    m = base_map()
    m = choropleth_cluster(m, gdf_cluster)
    st_folium(m, width=600, height=480)

with chart_col:
    st.subheader("📊 Distribusi LST per Zona")

    ZONA_ORDER = ["UHI Intensif 🔴", "UHI Sedang 🟡", "UHI Rendah 🟢"]
    ZONA_COLOR = {
        "UHI Intensif 🔴": "#E85D24",
        "UHI Sedang 🟡":   "#EF9F27",
        "UHI Rendah 🟢":   "#1D9E75",
    }

    df_plot = df[df["zona_uhi"].notna()].copy()

    fig_box = px.box(
        df_plot, x="zona_uhi", y="lst_c_mean",
        color="zona_uhi",
        color_discrete_map=ZONA_COLOR,
        category_orders={"zona_uhi": ZONA_ORDER},
        points="all",
        labels={"zona_uhi": "Zona UHI", "lst_c_mean": "LST (°C)"},
        title="Distribusi LST per Zona UHI"
    )
    fig_box.update_layout(
        showlegend=False, plot_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0")
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # LST rata-rata per zona per tahun
    st.subheader("📈 Tren LST per Zona")
    df_zona_yr = df_plot.groupby(["year","zona_uhi"])["lst_c_mean"].mean().reset_index()
    fig_line = px.line(
        df_zona_yr, x="year", y="lst_c_mean", color="zona_uhi",
        markers=True, color_discrete_map=ZONA_COLOR,
        labels={"year": "Tahun", "lst_c_mean": "LST Rata-rata (°C)", "zona_uhi": "Zona"},
    )
    fig_line.update_layout(
        hovermode="x unified", plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.3),
        xaxis=dict(tickmode="linear", dtick=1, gridcolor="#f0f0f0"),
        yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# ── Radar chart profil tiap kota ──
st.subheader("🕸️ Profil Multi-dimensi per Kota")

feats = ["lst_c_mean", "uhi_intensity", "ndvi_mean", "lst_std"]
feat_labels = ["LST Mean", "UHI Intensity", "NDVI", "LST Std"]
df_radar = df.groupby("kota")[feats].mean().reset_index()

# Normalisasi 0-1
for f in feats:
    mn, mx = df_radar[f].min(), df_radar[f].max()
    df_radar[f] = (df_radar[f] - mn) / (mx - mn + 1e-9)

fig_radar = go.Figure()
colors = ["#E85D24","#EF9F27","#1D9E75","#378ADD","#534AB7","#993C1D","#185FA5"]
for i, kota in enumerate(df_radar["kota"]):
    row = df_radar[df_radar["kota"] == kota].iloc[0]
    vals = [row[f] for f in feats] + [row[feats[0]]]
    fig_radar.add_trace(go.Scatterpolar(
        r=vals, theta=feat_labels + [feat_labels[0]],
        fill="toself", name=kota,
        line_color=colors[i % len(colors)],
        opacity=0.7
    ))

fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    showlegend=True,
    title="Profil Karakteristik Multi-dimensi (Ternormalisasi)",
    height=450
)
st.plotly_chart(fig_radar, use_container_width=True)
