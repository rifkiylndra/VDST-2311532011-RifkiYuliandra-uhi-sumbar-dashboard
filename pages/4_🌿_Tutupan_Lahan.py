"""
pages/4_🌿_Tutupan_Lahan.py
Analisis korelasi tutupan lahan (NDVI/NBI) vs LST + hasil Random Forest
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
sys.path.append(".")
from utils.data_loader import load_panel, load_models, KOTA_LIST

st.set_page_config(page_title="Tutupan Lahan | UHI Sumbar", page_icon="🌿", layout="wide")
st.title("🌿 Analisis Tutupan Lahan & Klasifikasi UHI")
st.caption("Korelasi NDVI vs LST + Hasil Random Forest Classifier (F1 Macro CV = 0.54)")

df = load_panel()
_, rf, _ = load_models()

st.divider()

# ── 1. Korelasi NDVI vs LST ──
st.subheader("🔗 Korelasi NDVI vs LST per Tahun")

col1, col2 = st.columns([1.5, 1])

with col1:
    df_corr = df[["kota","year","lst_c_mean","ndvi_mean","zona_uhi"]].dropna()
    ZONA_COLOR = {
        "UHI Intensif 🔴": "#E85D24",
        "UHI Sedang 🟡":   "#EF9F27",
        "UHI Rendah 🟢":   "#1D9E75",
        "UHI Sangat Rendah 🔵": "#378ADD",
    }

    fig_scatter = px.scatter(
        df_corr, x="ndvi_mean", y="lst_c_mean",
        color="zona_uhi", symbol="kota",
        color_discrete_map=ZONA_COLOR,
        size_max=12,
        trendline="ols",
        hover_data=["kota","year"],
        labels={"ndvi_mean": "NDVI (Indeks Vegetasi)",
                "lst_c_mean": "LST Rata-rata (°C)",
                "zona_uhi": "Zona UHI"},
        title="Scatter Plot NDVI vs LST (dengan trendline OLS)"
    )
    fig_scatter.update_layout(plot_bgcolor="white",
                              xaxis=dict(gridcolor="#f0f0f0"),
                              yaxis=dict(gridcolor="#f0f0f0"))
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.markdown("**Korelasi Pearson per Kota**")
    corr_data = []
    for kota in KOTA_LIST:
        sub = df[df["kota"]==kota][["lst_c_mean","ndvi_mean","nbi_mean"]].dropna()
        if len(sub) > 3:
            r_ndvi = sub["lst_c_mean"].corr(sub["ndvi_mean"])
            r_nbi  = sub["lst_c_mean"].corr(sub["nbi_mean"]) if "nbi_mean" in sub else np.nan
            corr_data.append({"Kota": kota, "r(LST,NDVI)": round(r_ndvi,3),
                               "r(LST,NBI)": round(r_nbi,3)})

    df_corr_tbl = pd.DataFrame(corr_data)
    st.dataframe(
        df_corr_tbl.style
            .background_gradient(subset=["r(LST,NDVI)"], cmap="RdYlGn_r")
            .format({"r(LST,NDVI)": "{:.3f}", "r(LST,NBI)": "{:.3f}"}),
        use_container_width=True, hide_index=True
    )
    st.markdown("""
    <div style="font-size:12px;color:#666;padding:8px;background:#f8f9fa;
                border-radius:6px;margin-top:8px;">
    📌 <b>Interpretasi:</b> r negatif antara NDVI dan LST menunjukkan
    wilayah dengan vegetasi lebih rapat cenderung memiliki suhu permukaan
    lebih rendah (efek evapotranspirasi).
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── 2. Tren NDVI per kota ──
st.subheader("📉 Tren NDVI — Indikator Perubahan Tutupan Vegetasi")

kota_ndvi = st.multiselect("Pilih kota:", KOTA_LIST, default=KOTA_LIST)
df_ndvi = df[df["kota"].isin(kota_ndvi)].dropna(subset=["ndvi_mean"])

fig_ndvi = px.line(
    df_ndvi.sort_values("year"), x="year", y="ndvi_mean", color="kota",
    markers=True, line_shape="spline",
    color_discrete_sequence=px.colors.qualitative.Set2,
    labels={"year": "Tahun", "ndvi_mean": "NDVI Rata-rata", "kota": "Kota"},
    title="Tren NDVI per Kota (2015–2025)"
)
fig_ndvi.add_hline(y=0.3, line_dash="dot", line_color="green",
                   annotation_text="Threshold vegetasi moderat (0.3)")
fig_ndvi.update_layout(
    hovermode="x unified", plot_bgcolor="white",
    legend=dict(orientation="h", y=-0.2),
    xaxis=dict(tickmode="linear", dtick=1, gridcolor="#f0f0f0"),
    yaxis=dict(gridcolor="#f0f0f0"),
)
st.plotly_chart(fig_ndvi, use_container_width=True)

st.divider()

# ── 3. Feature Importance Random Forest ──
st.subheader("🤖 Feature Importance — Random Forest Classifier")

col3, col4 = st.columns([1.2, 1])

with col3:
    feat_names = rf.feature_names_in_ if hasattr(rf, "feature_names_in_") else \
                 ["ndvi_mean","nbi_mean","mndwi_mean","lst_std","year_num","is_urban","delta_lst"]
    importances = rf.feature_importances_

    fi_df = pd.DataFrame({
        "Fitur": feat_names,
        "Importance": importances
    }).sort_values("Importance", ascending=True)

    FEAT_LABEL = {
        "ndvi_mean":    "NDVI (vegetasi)",
        "nbi_mean":     "NBI (built-up index)",
        "mndwi_mean":   "MNDWI (badan air)",
        "lst_std":      "LST Std (variabilitas suhu)",
        "year_num":     "Tahun (tren temporal)",
        "is_urban":     "Status urban",
        "delta_lst":    "Δ LST vs baseline",
    }
    fi_df["Label"] = fi_df["Fitur"].map(FEAT_LABEL).fillna(fi_df["Fitur"])

    fig_fi = px.bar(
        fi_df, x="Importance", y="Label",
        orientation="h",
        color="Importance",
        color_continuous_scale=["#E6F1FB","#1D9E75"],
        labels={"Importance": "Feature Importance", "Label": "Fitur"},
        title="Feature Importance — Random Forest"
    )
    fig_fi.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0")
    )
    st.plotly_chart(fig_fi, use_container_width=True)

with col4:
    st.markdown("**Interpretasi Feature Importance**")
    st.markdown("""
    <div style="font-size:13px;line-height:1.8;color:#444">
    <b>delta_lst</b> dan <b>year_num</b> mendominasi — artinya perubahan
    LST terhadap baseline dan tren temporal adalah prediktor terkuat
    kategori UHI suatu kota.<br><br>
    <b>ndvi_mean</b> juga signifikan, mengkonfirmasi bahwa tutupan vegetasi
    berperan penting dalam menentukan intensitas UHI.<br><br>
    <b>F1 Macro CV-5 = 0.54</b> — performa moderate, wajar untuk dataset
    kecil (65 sampel). Accuracy training 0.98 mengindikasikan sedikit
    overfitting yang perlu disebutkan sebagai keterbatasan di artikel.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Metrik Evaluasi**")
    metrics_data = {
        "Metrik": ["F1 Macro (CV-5)", "Accuracy (Training)", "Precision (avg)", "Recall (avg)"],
        "Nilai":  ["0.5376 ± 0.054", "0.98", "0.97", "0.99"]
    }
    st.dataframe(pd.DataFrame(metrics_data), use_container_width=True, hide_index=True)
