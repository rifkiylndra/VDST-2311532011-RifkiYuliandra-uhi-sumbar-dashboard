"""
pages/2_🗺️_Peta_UHI.py
Peta choropleth interaktif LST dengan slider tahun
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import json
sys.path.append(".")
from utils.data_loader import load_panel, load_geodata, merge_geo, KOTA_LIST

st.set_page_config(page_title="Peta UHI | UHI Sumbar", page_icon="🗺️", layout="wide")
st.title("🗺️ Peta Spasio-Temporal Urban Heat Island")
st.caption("Peta choropleth interaktif LST dengan kontrol temporal — klik wilayah untuk detail")

df  = load_panel()
gdf = load_geodata()

# ── Sidebar kontrol ──
st.sidebar.header("🎛️ Kontrol Peta")

is_timelapse = st.sidebar.checkbox("▶️ Mode Timelapse (Animasi)", value=False)

year_sel = st.sidebar.slider(
    "📅 Pilih Tahun",
    min_value=int(df["year"].min()),
    max_value=int(df["year"].max()),
    value=int(df["year"].max()),
    step=1
)

metric_opt = st.sidebar.selectbox(
    "📊 Metrik ditampilkan",
    ["lst_c_mean", "uhi_intensity", "delta_lst"],
    format_func=lambda x: {
        "lst_c_mean":    "🌡️ LST Rata-rata (°C)",
        "uhi_intensity": "☀️ UHI Intensity (°C)",
        "delta_lst":     "📈 Δ LST vs 2015 (°C)",
    }[x]
)

metric_label = {
    "lst_c_mean":    "LST Rata-rata (°C)",
    "uhi_intensity": "UHI Intensity (°C)",
    "delta_lst":     "Δ LST vs 2015 (°C)",
}[metric_opt]

# ── Gabung data ──
df_yr  = df[df["year"] == year_sel].copy()
gdf_yr = merge_geo(df_yr, gdf)

# ── Layout: peta kiri, info kanan ──
map_col, info_col = st.columns([2.2, 1])

with map_col:
    if is_timelapse:
        st.markdown(f"**Timelapse {metric_label} (2015 - {df['year'].max()})**")
        df_clean = df.dropna(subset=[metric_opt]).sort_values("year")
        fig = px.choropleth_mapbox(
            df_clean,
            geojson=gdf.__geo_interface__,
            locations="kota",
            featureidkey="properties.kota",
            color=metric_opt,
            animation_frame="year",
            color_continuous_scale="YlOrRd" if "lst" in metric_opt else "RdYlBu_r",
            range_color=(df_clean[metric_opt].min(), df_clean[metric_opt].max()),
            mapbox_style="carto-positron",
            zoom=7.5,
            center={"lat": -0.7, "lon": 100.5},
            opacity=0.7,
            labels={metric_opt: metric_label},
            hover_name="kota",
            hover_data={"kota": False, "year": False, "zona_uhi": True}
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(f"**{metric_label} — Tahun {year_sel}**")
        df_yr_clean = df_yr.dropna(subset=[metric_opt])
        fig = px.choropleth_mapbox(
            df_yr_clean,
            geojson=gdf.__geo_interface__,
            locations="kota",
            featureidkey="properties.kota",
            color=metric_opt,
            color_continuous_scale="YlOrRd" if "lst" in metric_opt else "RdYlBu_r",
            range_color=(df[metric_opt].min(), df[metric_opt].max()),
            mapbox_style="carto-positron",
            zoom=7.5,
            center={"lat": -0.7, "lon": 100.5},
            opacity=0.7,
            labels={metric_opt: metric_label},
            hover_name="kota",
            hover_data={"kota": False, "zona_uhi": True}
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

with info_col:
    st.markdown("**📋 Data Tahun Terpilih**")

    for kota in KOTA_LIST:
        row = df_yr[df_yr["kota"] == kota]
        if row.empty:
            continue
        row = row.iloc[0]
        zona = row.get("zona_uhi", "-")
        lst  = row.get("lst_c_mean", None)
        uhi  = row.get("uhi_intensity", None)
        dlt  = row.get("delta_lst", None)

        color = "#E85D24" if "Intensif" in str(zona) else \
                "#EF9F27" if "Sedang"   in str(zona) else \
                "#1D9E75" if "Rendah"   in str(zona) else "#378ADD"

        st.markdown(f"""
        <div style="border-left:3px solid {color};padding:6px 10px;
                    margin-bottom:7px;border-radius:0 6px 6px 0;background:var(--secondary-background-color);">
            <div style="font-weight:600;font-size:13px;color:var(--text-color);">{kota}</div>
            <div style="font-size:12px;color:var(--text-color);opacity:0.8;">
                LST: <b>{lst:.1f}°C</b> &nbsp;|&nbsp;
                UHI: <b>{uhi:+.2f}°C</b> &nbsp;|&nbsp;
                Δ: <b>{dlt:+.2f}°C</b>
            </div>
            <div style="font-size:11px;color:{color};margin-top:2px">{zona}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Grafik tren di bawah peta ──
st.divider()
st.subheader("📈 Tren Temporal — Pilih Kota untuk Perbandingan")

kota_cmp = st.multiselect(
    "Bandingkan kota:", KOTA_LIST, default=KOTA_LIST[:4]
)

if kota_cmp:
    df_cmp = df[df["kota"].isin(kota_cmp)].sort_values("year")
    fig = px.line(
        df_cmp, x="year", y=metric_opt, color="kota",
        markers=True, line_shape="spline",
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"year": "Tahun", metric_opt: metric_label, "kota": "Kota"},
    )
    fig.add_vline(x=year_sel, line_dash="dot", line_color="red",
                  annotation_text=f"Tahun {year_sel}", annotation_position="top right")
    fig.update_layout(
        hovermode="x unified", plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.2),
        xaxis=dict(tickmode="linear", dtick=1, gridcolor="#f0f0f0"),
        yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig, use_container_width=True)
