# 🌡️ Urban Heat Island — 7 Kota Sumatera Barat

Aplikasi visualisasi data spasio-temporal intensitas Urban Heat Island (UHI) dan perubahan tutupan lahan di 7 kota administratif Sumatera Barat menggunakan data Landsat 8/9 LST (2015–2025) dengan pendekatan Machine Learning.

**Proyek Akhir — Mata Kuliah Visualisasi Data Spasio-Temporal**

---

## 📁 Struktur Folder

```
uhi_sumbar_app/
├── app.py                      ← Beranda (entry point)
├── pages/
│   ├── 1_📊_Tren_LST.py       ← Grafik tren LST historis
│   ├── 2_🗺️_Peta_UHI.py       ← Peta choropleth interaktif
│   ├── 3_🤖_Clustering.py     ← Hasil K-Means clustering
│   ├── 4_🌿_Tutupan_Lahan.py  ← Korelasi NDVI + Random Forest
│   └── 5_🔮_Forecasting.py    ← Proyeksi LST 2026–2030
├── data/
│   ├── uhi_panel_data.csv          ← Data panel 7 kota 2015–2025
│   ├── uhi_forecast_2026_2030.csv  ← Hasil proyeksi XGBoost
│   ├── model_evaluation.csv        ← RMSE & MAE per kota
│   ├── 7kota_sumbar.gpkg           ← Shapefile 7 kota
│   ├── kmeans_model.pkl            ← Model K-Means
│   ├── rf_model.pkl                ← Model Random Forest
│   └── xgb_models.pkl             ← Model XGBoost (dict per kota)
├── utils/
│   ├── data_loader.py              ← Fungsi loading data terpusat
│   └── map_utils.py                ← Fungsi builder peta Folium
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalasi & Menjalankan Aplikasi

### 1. Clone / Download project
Pastikan semua file sudah ada sesuai struktur di atas.

### 2. Buat virtual environment (opsional tapi direkomendasikan)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependensi
```bash
pip install -r requirements.txt
```

> ⚠️ **Catatan untuk Windows:** Jika instalasi `rasterio` gagal, install via wheel:
> ```bash
> pip install pipwin
> pipwin install rasterio
> ```
> Atau download wheel dari: https://github.com/cgohlke/geospatial-wheels

### 4. Pastikan file data sudah ada di folder `data/`
Download dari Google Drive → folder `UHI_Sumbar` → salin ke `data/`:
- `uhi_panel_data.csv`
- `uhi_forecast_2026_2030.csv`
- `model_evaluation.csv`
- `7kota_sumbar.gpkg`
- `kmeans_model.pkl`
- `rf_model.pkl`
- `xgb_models.pkl`

### 5. Jalankan aplikasi
```bash
streamlit run app.py
```
Aplikasi akan terbuka otomatis di browser: `http://localhost:8501`

---

## 🗺️ Fitur Dashboard

| Halaman | Deskripsi |
|---------|-----------|
| **🏠 Beranda** | Ringkasan metrik utama, tabel kota, performa model |
| **📊 Tren LST** | Grafik tren historis, heatmap, bar chart perbandingan per tahun |
| **🗺️ Peta UHI** | Choropleth interaktif dengan slider tahun (2015–2025), tooltip per kota |
| **🤖 Clustering** | Peta zona UHI (K-Means k=3), box plot distribusi, radar chart |
| **🌿 Tutupan Lahan** | Scatter NDVI vs LST, tren NDVI, feature importance RF |
| **🔮 Forecasting** | Proyeksi XGBoost 2026–2030 dengan confidence interval |

---

## 📊 Data & Metodologi

| Komponen | Detail |
|----------|--------|
| **Sumber data** | Landsat 8/9 Collection 2 Level-2 (NASA/USGS) via Google Earth Engine |
| **Variabel utama** | Land Surface Temperature (ST_B10), NDVI, MNDWI, NBI |
| **Periode** | 2015–2025 (musim kemarau Mei–Oktober) |
| **Resolusi** | 30 meter per piksel |
| **Batas admin** | GADM Level 2 Indonesia |
| **ML Clustering** | K-Means (k=3, Silhouette=0.416) |
| **ML Klasifikasi** | Random Forest (F1 Macro CV = 0.54) |
| **ML Forecasting** | XGBoost Regressor (RMSE 0.23–1.92°C) |

---

## 👤 Informasi Proyek

- **Mata Kuliah:** Visualisasi Data Spasio-Temporal
- **Topik:** Intensitas UHI dan Perubahan Tutupan Lahan di 7 Kota Sumatera Barat
- **Teknologi:** Python, Streamlit, Folium, GeoPandas, scikit-learn, XGBoost, Google Earth Engine
