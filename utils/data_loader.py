"""
utils/data_loader.py
Fungsi loading data terpusat dengan caching Streamlit.
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import joblib
from pathlib import Path

# ── Path data (relatif dari root app) ──
DATA_DIR    = Path("data")
PANEL_CSV   = DATA_DIR / "uhi_panel_data.csv"
FORECAST_CSV= DATA_DIR / "uhi_forecast_2026_2030.csv"
EVAL_CSV    = DATA_DIR / "model_evaluation.csv"
GPKG_PATH   = DATA_DIR / "7kota_sumbar.gpkg"
KM_MODEL    = DATA_DIR / "kmeans_model.pkl"
RF_MODEL    = DATA_DIR / "rf_model.pkl"
XGB_MODEL   = DATA_DIR / "xgb_models.pkl"

KOTA_LIST = [
    "Bukittinggi", "Padang", "Padang Panjang",
    "Pariaman", "Payakumbuh", "Sawahlunto", "Solok"
]

ZONA_COLOR = {
    "UHI Intensif 🔴": "#E85D24",
    "UHI Sedang 🟡":   "#EF9F27",
    "UHI Rendah 🟢":   "#1D9E75",
    "UHI Sangat Rendah 🔵": "#378ADD",
}


@st.cache_data
def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_CSV)
    # Clip nilai LST yang tidak realistis (artefak awan)
    df["lst_c_mean"] = df["lst_c_mean"].clip(lower=10, upper=55)
    df["lst_max"]    = df["lst_max"].clip(lower=10, upper=65)
    df["lst_min"]    = df["lst_min"].clip(lower=10, upper=55)
    return df


@st.cache_data
def load_forecast() -> pd.DataFrame:
    return pd.read_csv(FORECAST_CSV)


@st.cache_data
def load_eval() -> pd.DataFrame:
    return pd.read_csv(EVAL_CSV)


@st.cache_data
def load_geodata() -> gpd.GeoDataFrame:
    return gpd.read_file(str(GPKG_PATH)).to_crs(epsg=4326)


@st.cache_resource
def load_models():
    km  = joblib.load(KM_MODEL)
    rf  = joblib.load(RF_MODEL)
    xgb = joblib.load(XGB_MODEL)
    return km, rf, xgb


def merge_geo(df_year: pd.DataFrame, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Gabungkan data panel (1 tahun) ke GeoDataFrame."""
    merged = gdf.merge(df_year, left_on="kota", right_on="kota", how="left")
    return merged
