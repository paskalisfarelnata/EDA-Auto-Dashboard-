# 📊 Auto EDA Insight

## Deskripsi Proyek

Auto EDA Insight adalah aplikasi berbasis Streamlit yang dirancang untuk membantu pengguna melakukan Exploratory Data Analysis (EDA) secara otomatis dan interaktif. Sistem ini memungkinkan pengguna mengunggah dataset, membersihkan data, melakukan analisis statistik, membuat visualisasi data, menghasilkan insight otomatis, serta mengekspor laporan hasil analisis.

## 🎯 Tujuan Proyek

- Mempermudah proses Exploratory Data Analysis (EDA).
- Mengotomatisasi proses analisis data.
- Menyediakan visualisasi data interaktif.
- Menghasilkan insight secara otomatis.
- Menyediakan fitur export laporan untuk dokumentasi hasil analisis.

## 🛠️ Teknologi yang Digunakan

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- OpenPyXL
- ReportLab
- Scikit-Learn

## 📁 Struktur Proyek

```text
Auto EDA Insight
│
├── app.py
├── requirements.txt
├── backend/
├── frontend/
├── assets/
├── data/
├── docs/
└── outputs/
```

# 🚀 Fitur Utama

## 1. Upload Dataset
- Mendukung file CSV, XLSX, dan TXT.
- Pembacaan dataset secara otomatis.

## 2. Data Management
- Preview dataset.
- Informasi jumlah baris dan kolom.
- Identifikasi tipe data.

## 3. Data Cleaning
- Deteksi missing values.
- Penghapusan missing values.
- Deteksi data duplikat.
- Ringkasan kualitas data.

## 4. Statistik Deskriptif
- Mean
- Median
- Modus
- Variance
- Standard Deviation
- Quartile

## 5. Analisis Kategorikal
- Frekuensi kategori.
- Persentase kategori.
- Distribusi data.

## 6. Visualisasi Data
- Histogram
- Boxplot
- Density Plot
- Violin Plot
- Bar Chart
- Pie Chart
- Count Plot
- Pareto Chart
- Scatter Plot
- Correlation Heatmap
- Bubble Chart
- Regression Plot

## 7. Time Series Analysis
- Trend Analysis
- Moving Average
- Visualisasi time series

## 8. Insight Generator
- Insight otomatis berdasarkan statistik dan visualisasi.
- Interpretasi tren dan hubungan antar variabel.

## 9. Reporting & Export
- Export ke CSV
- Export ke Excel
- Export ke PDF
- Export ke HTML

# 📝 Dokumentasi Modul Backend

### data_loader.py
Membaca dataset yang diunggah pengguna dan mendeteksi tipe data secara otomatis.

### preprocessing.py
Melakukan pembersihan data, penanganan missing value, dan penghapusan duplikasi.

### descriptive_stats.py
Menghasilkan statistik deskriptif untuk variabel numerik.

### visualization.py
Membuat berbagai visualisasi data untuk membantu proses eksplorasi.

### insight_generator.py
Menghasilkan insight otomatis berdasarkan hasil analisis data.

### export_report.py
Mengekspor hasil analisis ke berbagai format laporan.

# ▶️ Cara Menjalankan Aplikasi

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi

```bash
streamlit run app.py
```

### 3. Buka Browser

```text
http://localhost:8501
```

# 👨‍💻 Tim Pengembang

Kelompok 7

- Ulin Nikmah
- Paskalis Farel Nata Zamasi
- Nazwa Nur Ramadhani
- Veronica

# 📌 Catatan

Auto EDA Insight dikembangkan sebagai proyek Pemrograman Website untuk menyediakan platform analisis data yang cepat, interaktif, dan mudah digunakan.
