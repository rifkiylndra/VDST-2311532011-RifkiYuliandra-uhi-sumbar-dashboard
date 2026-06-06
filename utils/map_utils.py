"""
utils/map_utils.py
Fungsi-fungsi pembuat peta Folium.
"""

import folium
import geopandas as gpd
import pandas as pd
import numpy as np
from folium.plugins import HeatMap, MarkerCluster


def base_map(lat=-0.9, lon=100.4, zoom=8) -> folium.Map:
    """Buat peta dasar dengan tile CartoDB."""
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles="CartoDB positron",
        attr="CartoDB"
    )
    return m


def choropleth_lst(m: folium.Map, gdf: gpd.GeoDataFrame,
                   col: str, label: str, year: int) -> folium.Map:
    """Tambahkan layer choropleth LST ke peta."""
    gdf_clean = gdf.dropna(subset=[col]).copy()
    if gdf_clean.empty:
        return m

    folium.Choropleth(
        geo_data=gdf_clean.to_json(),
        data=gdf_clean,
        columns=["kota", col],
        key_on="feature.properties.kota",
        fill_color="YlOrRd",
        fill_opacity=0.75,
        line_opacity=0.4,
        nan_fill_color="#cccccc",
        legend_name=f"{label} ({year})",
        name=f"Choropleth {label}",
    ).add_to(m)

    # Tooltip interaktif
    folium.GeoJson(
        gdf_clean,
        name="Info Kota",
        style_function=lambda x: {
            "fillOpacity": 0,
            "color": "#333",
            "weight": 1,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["kota", "lst_c_mean", "lst_max", "uhi_intensity",
                    "delta_lst", "zona_uhi"],
            aliases=["🏙️ Kota", "🌡️ LST Rata-rata (°C)", "🔥 LST Maks (°C)",
                     "☀️ UHI Intensity (°C)", "📈 Δ LST vs 2015 (°C)", "🗂️ Zona UHI"],
            localize=True,
            sticky=True,
            style="font-size:13px; font-family: sans-serif;",
        ),
        popup=folium.GeoJsonPopup(
            fields=["kota", "lst_c_mean", "uhi_intensity", "zona_uhi"],
            aliases=["Kota", "LST (°C)", "UHI Intensity", "Zona"],
        ),
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def choropleth_cluster(m: folium.Map, gdf: gpd.GeoDataFrame) -> folium.Map:
    """Layer choropleth berdasarkan zona UHI cluster."""
    COLOR_MAP = {
        "UHI Intensif 🔴":      "#E85D24",
        "UHI Sedang 🟡":        "#EF9F27",
        "UHI Rendah 🟢":        "#1D9E75",
        "UHI Sangat Rendah 🔵": "#378ADD",
    }

    def style_fn(feature):
        zona = feature["properties"].get("zona_uhi", "")
        color = COLOR_MAP.get(zona, "#aaaaaa")
        return {"fillColor": color, "color": "#333",
                "weight": 1.5, "fillOpacity": 0.75}

    folium.GeoJson(
        gdf,
        name="Zona UHI Cluster",
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["kota", "zona_uhi", "cluster", "lst_c_mean"],
            aliases=["🏙️ Kota", "🗂️ Zona UHI", "🔢 Cluster ID", "🌡️ LST Rata-rata (°C)"],
            sticky=True,
        ),
        popup=folium.GeoJsonPopup(
            fields=["kota", "zona_uhi"],
            aliases=["Kota", "Zona UHI"],
        ),
    ).add_to(m)

    # Legend manual
    legend_html = """
    <div style="position:fixed;bottom:40px;left:40px;z-index:1000;
                background:white;padding:12px 16px;border-radius:8px;
                box-shadow:2px 2px 8px rgba(0,0,0,0.2);font-size:13px;">
      <b>Zona UHI</b><br>
      <span style="color:#E85D24">■</span> UHI Intensif<br>
      <span style="color:#EF9F27">■</span> UHI Sedang<br>
      <span style="color:#1D9E75">■</span> UHI Rendah<br>
      <span style="color:#378ADD">■</span> UHI Sangat Rendah
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl().add_to(m)
    return m
