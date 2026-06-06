"""
app.py — Halaman Beranda (Landing Page)
Urban Heat Island Sumatera Barat | Visualisasi Data Spasio-Temporal
"""

import streamlit as st
from utils.data_loader import load_panel, load_forecast, load_eval, KOTA_LIST

st.set_page_config(
    page_title="UHI Sumatera Barat",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS kustom ──
st.markdown("""
<style>
    .metric-card {
        background: var(--secondary-background-color);
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #E85D24;
        margin-bottom: 8px;
    }
    .metric-title { font-size: 12px; color: var(--text-color); opacity: 0.7; text-transform: uppercase; letter-spacing: .06em; }
    .metric-value { font-size: 26px; font-weight: 700; color: var(--text-color); }
    .metric-sub   { font-size: 12px; color: var(--text-color); opacity: 0.7; margin-top: 2px; }
    .hero-title   { font-size: 2rem; font-weight: 700; color: var(--text-color); line-height: 1.3; }
    .hero-sub     { font-size: 1rem; color: var(--text-color); opacity: 0.8; margin-top: 8px; }
    .section-title{ font-size: 1.1rem; font-weight: 600; color: var(--text-color); margin: 1rem 0 .5rem; }
    .badge        { display:inline-block; padding:3px 10px; border-radius:20px;
                    font-size:11px; font-weight:600; margin:2px; }
    .badge-red    { background:#993C1D; color:#FAECE7; }
    .badge-green  { background:#0F6E56; color:#E1F5EE; }
    .badge-blue   { background:#185FA5; color:#E6F1FB; }
    .badge-amber  { background:#854F0B; color:#FAEEDA; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──
df       = load_panel()
df_fore  = load_forecast()
df_eval  = load_eval()

year_min = int(df["year"].min())
year_max = int(df["year"].max())

# ── Hero Section ──
st.markdown("""
<div class="hero-title">🌡️ Urban Heat Island — 7 Kota Sumatera Barat</div>
<div class="hero-sub">
Analisis spasio-temporal intensitas UHI dan perubahan tutupan lahan menggunakan
data Landsat 8/9 LST (2015–2025) dengan pendekatan Machine Learning
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Metric Cards ──
latest_year = df["year"].max()
df_latest   = df[df["year"] == latest_year]

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_lst = df_latest["lst_c_mean"].mean()
    st.metric("🌡️ Rata-rata LST (2025)", f"{avg_lst:.1f} °C",
              delta=f"+{df[df['year']==2015]['lst_c_mean'].mean() - avg_lst:.1f} °C vs 2015")

with col2:
    hottest = df_latest.loc[df_latest["lst_c_mean"].idxmax(), "kota"]
    hottest_val = df_latest["lst_c_mean"].max()
    st.metric("🔥 Kota Terpanas (2025)", hottest, delta=f"{hottest_val:.1f} °C")

with col3:
    max_uhi = df_latest["uhi_intensity"].max()
    max_uhi_kota = df_latest.loc[df_latest["uhi_intensity"].idxmax(), "kota"]
    st.metric("☀️ UHI Intensity Tertinggi", max_uhi_kota, delta=f"+{max_uhi:.2f} °C")

with col4:
    fore_2030 = df_fore[df_fore["year"] == 2030]["lst_forecast"].mean()
    st.metric("🔮 Proyeksi LST 2030", f"{fore_2030:.1f} °C",
              delta=f"+{fore_2030 - avg_lst:.1f} °C dari 2025")

st.divider()

# ── Dua kolom: info + tabel kota ──
left, right = st.columns([1.2, 1])

with left:
    st.markdown('<div class="section-title">📍 Area Studi: 7 Kota Administratif Sumbar</div>',
                unsafe_allow_html=True)

    zone_data = df[["kota", "zona_uhi"]].drop_duplicates().set_index("kota")

    for kota in KOTA_LIST:
        zona = zone_data.loc[kota, "zona_uhi"] if kota in zone_data.index else "-"
        lst_kota = df_latest[df_latest["kota"] == kota]["lst_c_mean"].values
        lst_str  = f"{lst_kota[0]:.1f} °C" if len(lst_kota) > 0 else "N/A"

        badge_class = "badge-red"
        if "Sedang"  in zona: badge_class = "badge-amber"
        if "Rendah"  in zona: badge_class = "badge-green"
        if "Sangat"  in zona: badge_class = "badge-blue"

        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:7px 12px;border-radius:8px;margin-bottom:5px;
                    background:var(--secondary-background-color);border:1px solid var(--border-color);">
            <span style="font-weight:500;font-size:14px;color:var(--text-color);">{kota}</span>
            <span>
                <span style="font-size:13px;color:var(--text-color);opacity:0.8;">{lst_str}</span>
                &nbsp;
                <span class="badge {badge_class}">{zona}</span>
            </span>
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">🤖 Performa Model Machine Learning</div>',
                unsafe_allow_html=True)

    st.markdown("**K-Means Clustering**")
    st.markdown("""
    <div style="background:var(--secondary-background-color);padding:10px 14px;border-radius:8px;font-size:13px;color:var(--text-color);">
        k = 3 zona UHI | Silhouette Score = <b>0.416</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Random Forest Classifier**")
    st.markdown("""
    <div style="background:var(--secondary-background-color);padding:10px 14px;border-radius:8px;font-size:13px;color:var(--text-color);">
        F1 Macro (CV-5) = <b>0.5376</b> | Accuracy training = 0.98
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**XGBoost Forecasting — RMSE per Kota**")
    if not df_eval.empty:
        st.dataframe(
            df_eval.style.format({"RMSE": "{:.3f} °C", "MAE": "{:.3f} °C"})
                   .background_gradient(subset=["RMSE"], cmap="YlOrRd"),
            use_container_width=True, hide_index=True
        )

st.divider()

# ── Navigasi ──
st.markdown('<div class="section-title">🗺️ Navigasi Dashboard</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.info("**📊 Tren LST**\nGrafik tren historis LST per kota 2015–2025 dengan perbandingan multi-kota")
with c2:
    st.info("**🗺️ Peta UHI**\nPeta choropleth interaktif dengan slider tahun dan tooltip informatif")
with c3:
    st.info("**🤖 Clustering**\nHasil K-Means: peta zona UHI + analisis silhouette")
with c4:
    st.info("**🔮 Forecasting**\nProyeksi LST 2026–2030 per kota dengan confidence interval")

st.caption(
    "Data: Landsat 8/9 Collection 2 Level-2 (NASA/USGS) via Google Earth Engine | "
    "Batas admin: GADM Level 2 | Analisis: Python + scikit-learn + XGBoost | "
    f"Periode: {year_min}–{year_max}"
)
