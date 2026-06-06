"""
pages/5_🔮_Forecasting.py
Proyeksi LST 2026–2030 menggunakan XGBoost
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys
sys.path.append(".")
from utils.data_loader import load_panel, load_forecast, load_eval, KOTA_LIST

st.set_page_config(page_title="Forecasting | UHI Sumbar", page_icon="🔮", layout="wide")
st.title("🔮 Proyeksi LST 2026–2030 — XGBoost Forecasting")
st.caption("Prediksi Land Surface Temperature menggunakan XGBoost Regressor berbasis lag features temporal")

df      = load_panel()
df_fore = load_forecast()
df_eval = load_eval()

# ── Sidebar ──
st.sidebar.header("⚙️ Pengaturan")
kota_sel = st.sidebar.selectbox("🏙️ Pilih Kota", KOTA_LIST)
show_ci  = st.sidebar.checkbox("Tampilkan Confidence Interval", value=True)
show_all = st.sidebar.checkbox("Tampilkan semua kota sekaligus", value=False)

# ── Evaluasi model ──
st.subheader("📊 Evaluasi Model XGBoost per Kota")
col_e1, col_e2 = st.columns([1, 1.5])

with col_e1:
    if not df_eval.empty:
        st.dataframe(
            df_eval.style
                .format({"RMSE": "{:.4f} °C", "MAE": "{:.4f} °C"})
                .background_gradient(subset=["RMSE"], cmap="YlOrRd")
                .highlight_min(subset=["RMSE"], color="#d4edda"),
            use_container_width=True, hide_index=True
        )

with col_e2:
    if not df_eval.empty:
        fig_eval = px.bar(
            df_eval.sort_values("RMSE"),
            x="RMSE", y="kota", orientation="h",
            color="RMSE", color_continuous_scale=["#1D9E75","#EF9F27","#E85D24"],
            labels={"RMSE": "RMSE (°C)", "kota": "Kota"},
            title="RMSE per Kota (lebih kecil = lebih baik)",
            text_auto=".3f"
        )
        fig_eval.update_layout(coloraxis_showscale=False, plot_bgcolor="white",
                               xaxis=dict(gridcolor="#f0f0f0"))
        fig_eval.update_traces(textposition="outside")
        st.plotly_chart(fig_eval, use_container_width=True)

st.divider()

# ── Chart forecast per kota ──
if not show_all:
    st.subheader(f"📈 Proyeksi LST — {kota_sel}")

    hist = df[df["kota"] == kota_sel].sort_values("year")
    fore = df_fore[df_fore["kota"] == kota_sel].sort_values("year")
    rmse = df_eval[df_eval["kota"] == kota_sel]["RMSE"].values
    rmse_val = rmse[0] if len(rmse) > 0 else 0

    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=hist["year"], y=hist["lst_c_mean"],
        mode="lines+markers",
        name="Historis (2015–2025)",
        line=dict(color="#1D9E75", width=2.5),
        marker=dict(size=8),
        hovertemplate="Tahun %{x}<br>LST: %{y:.2f}°C<extra></extra>"
    ))

    # Forecast
    if not fore.empty:
        fig.add_trace(go.Scatter(
            x=fore["year"], y=fore["lst_forecast"],
            mode="lines+markers",
            name="Proyeksi (2026–2030)",
            line=dict(color="#E85D24", width=2.5, dash="dash"),
            marker=dict(size=8, symbol="square"),
            hovertemplate="Tahun %{x}<br>Proyeksi: %{y:.2f}°C<extra></extra>"
        ))

        # Confidence interval
        if show_ci:
            fig.add_trace(go.Scatter(
                x=list(fore["year"]) + list(fore["year"][::-1]),
                y=list(fore["lst_upper"]) + list(fore["lst_lower"][::-1]),
                fill="toself",
                fillcolor="rgba(232,93,36,0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                name=f"CI ± RMSE ({rmse_val:.2f}°C)",
                hoverinfo="skip"
            ))

    # Garis pemisah historis-proyeksi
    fig.add_vline(x=2025.5, line_dash="dot", line_color="gray",
                  annotation_text="Batas historis/proyeksi",
                  annotation_position="top")

    fig.update_layout(
        title=f"Proyeksi LST {kota_sel} — 2015 hingga 2030",
        xaxis_title="Tahun",
        yaxis_title="LST Rata-rata (°C)",
        hovermode="x unified",
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.2),
        xaxis=dict(tickmode="linear", dtick=1, gridcolor="#f0f0f0"),
        yaxis=dict(gridcolor="#f0f0f0"),
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabel proyeksi
    if not fore.empty:
        st.markdown(f"**Tabel Proyeksi LST — {kota_sel}**")
        tbl = fore[["year","lst_forecast","lst_lower","lst_upper"]].copy()
        tbl.columns = ["Tahun","LST Proyeksi (°C)","Batas Bawah (°C)","Batas Atas (°C)"]
        st.dataframe(
            tbl.style.format({c: "{:.2f}" for c in tbl.columns if c != "Tahun"})
               .background_gradient(subset=["LST Proyeksi (°C)"], cmap="YlOrRd"),
            use_container_width=True, hide_index=True
        )

else:
    # ── Semua kota sekaligus ──
    st.subheader("📈 Proyeksi LST Semua Kota (2015–2030)")

    n = len(KOTA_LIST)
    cols_n = 3
    rows_n = (n + cols_n - 1) // cols_n

    for row_i in range(rows_n):
        cols = st.columns(cols_n)
        for col_i in range(cols_n):
            idx = row_i * cols_n + col_i
            if idx >= n:
                break
            kota = KOTA_LIST[idx]
            hist = df[df["kota"] == kota].sort_values("year")
            fore = df_fore[df_fore["kota"] == kota].sort_values("year")

            with cols[col_i]:
                fig_s = go.Figure()
                fig_s.add_trace(go.Scatter(
                    x=hist["year"], y=hist["lst_c_mean"],
                    mode="lines+markers", name="Historis",
                    line=dict(color="#1D9E75", width=2),
                    marker=dict(size=5)
                ))
                if not fore.empty:
                    fig_s.add_trace(go.Scatter(
                        x=fore["year"], y=fore["lst_forecast"],
                        mode="lines+markers", name="Proyeksi",
                        line=dict(color="#E85D24", width=2, dash="dash"),
                        marker=dict(size=5, symbol="square")
                    ))
                    if show_ci:
                        fig_s.add_trace(go.Scatter(
                            x=list(fore["year"]) + list(fore["year"][::-1]),
                            y=list(fore["lst_upper"]) + list(fore["lst_lower"][::-1]),
                            fill="toself", fillcolor="rgba(232,93,36,0.15)",
                            line=dict(color="rgba(0,0,0,0)"), showlegend=False,
                        ))
                fig_s.add_vline(x=2025.5, line_dash="dot", line_color="gray")
                fig_s.update_layout(
                    title=dict(text=kota, font=dict(size=13)),
                    height=280, showlegend=False,
                    plot_bgcolor="white", margin=dict(t=35,b=20,l=30,r=10),
                    xaxis=dict(tickmode="linear", dtick=2, gridcolor="#f0f0f0",
                               tickfont=dict(size=9)),
                    yaxis=dict(gridcolor="#f0f0f0", tickfont=dict(size=9)),
                )
                st.plotly_chart(fig_s, use_container_width=True)

st.divider()

# ── Ringkasan proyeksi 2030 ──
st.subheader("📋 Ringkasan Proyeksi LST Tahun 2030")
fore_2030 = df_fore[df_fore["year"] == 2030][["kota","lst_forecast","lst_lower","lst_upper"]]
fore_2030 = fore_2030.merge(
    df[df["year"] == df["year"].max()][["kota","lst_c_mean"]].rename(
        columns={"lst_c_mean":"lst_2025"}),
    on="kota", how="left"
)
fore_2030["delta_2025_2030"] = (fore_2030["lst_forecast"] - fore_2030["lst_2025"]).round(3)

fore_2030.columns = ["Kota","Proyeksi 2030 (°C)","Batas Bawah","Batas Atas","LST 2025 (°C)","Δ 2025→2030 (°C)"]
st.dataframe(
    fore_2030.style
        .format({c: "{:.2f}" for c in fore_2030.columns if c != "Kota"})
        .background_gradient(subset=["Proyeksi 2030 (°C)"], cmap="YlOrRd")
        .background_gradient(subset=["Δ 2025→2030 (°C)"], cmap="RdYlGn_r"),
    use_container_width=True, hide_index=True
)

st.caption("""
📌 **Metodologi:** XGBoost Regressor dengan lag features (lag1, lag2, lag3) dan trend temporal.
Confidence interval dihitung dari RMSE in-sample. Proyeksi bersifat ceteris paribus (asumsi pola
tutupan lahan dan iklim tidak berubah drastis). Interpretasikan sebagai skenario baseline.
""")
