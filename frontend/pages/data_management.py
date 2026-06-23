import os
import streamlit as st
import pandas as pd

from backend.preprocessing import dataset_information
from backend.table_utils import show_table


# =====================================================
# DATA MANAGEMENT CSS — DARK PERMANENT
# =====================================================
def inject_data_management_css():
    st.markdown(
        """
        <style>
            .dm-hero {
                background:
                    radial-gradient(circle at 8% 0%, rgba(56,189,248,.18), transparent 32%),
                    radial-gradient(circle at 96% 12%, rgba(168,85,247,.18), transparent 34%),
                    linear-gradient(135deg, #020617 0%, #0f172a 52%, #111827 100%) !important;
                border: 1px solid rgba(96,165,250,.28) !important;
                border-radius: 24px !important;
                padding: 18px 22px !important;
                margin-bottom: 18px !important;
                box-shadow:
                    0 18px 48px rgba(0,0,0,.36),
                    0 0 32px rgba(56,189,248,.09) !important;
                color: #f8fafc !important;
            }

            .dm-title {
                font-size: 25px !important;
                font-weight: 1000 !important;
                color: #ffffff !important;
                margin-bottom: 5px !important;
                line-height: 1.15 !important;
            }

            .dm-subtitle {
                font-size: 13px !important;
                color: #cbd5e1 !important;
                font-weight: 650 !important;
                line-height: 1.55 !important;
            }

            .dm-card {
                background: rgba(15, 23, 42, 0.92) !important;
                border: 1px solid rgba(96, 165, 250, 0.28) !important;
                border-radius: 20px !important;
                padding: 16px 18px !important;
                box-shadow:
                    0 14px 34px rgba(0,0,0,.34),
                    0 0 24px rgba(56,189,248,.06) !important;
                margin-bottom: 16px !important;
                color: #e2e8f0 !important;
            }

            .dm-card-title {
                font-size: 16px !important;
                font-weight: 1000 !important;
                color: #f8fafc !important;
                margin-bottom: 8px !important;
            }

            .dm-desc {
                font-size: 13px !important;
                color: #cbd5e1 !important;
                line-height: 1.6 !important;
                font-weight: 650 !important;
            }

            .dm-kpi {
                background: linear-gradient(135deg, rgba(15,23,42,.94), rgba(30,41,59,.86)) !important;
                border: 1px solid rgba(96,165,250,.28) !important;
                border-radius: 18px !important;
                padding: 14px 15px !important;
                min-height: 106px !important;
                box-shadow: 0 12px 30px rgba(0,0,0,.30) !important;
                margin-bottom: 14px !important;
            }

            .dm-kpi-icon {
                font-size: 22px !important;
                margin-bottom: 5px !important;
            }

            .dm-kpi-label {
                color: #cbd5e1 !important;
                font-size: 12px !important;
                font-weight: 850 !important;
            }

            .dm-kpi-value {
                color: #f8fafc !important;
                font-size: 28px !important;
                font-weight: 1000 !important;
                line-height: 1.1 !important;
                margin-top: 4px !important;
                word-break: break-word !important;
            }

            .dm-path {
                background: rgba(2, 6, 23, .72) !important;
                border: 1px dashed rgba(96,165,250,.35) !important;
                border-radius: 13px !important;
                padding: 10px 12px !important;
                color: #dbeafe !important;
                font-size: 12px !important;
                font-weight: 700 !important;
                word-break: break-all !important;
                margin: 10px 0 14px 0 !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(15, 23, 42, 0.88) !important;
                border: 1px solid rgba(96,165,250,.24) !important;
                border-radius: 20px !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.30) !important;
                color: #e2e8f0 !important;
            }

            [data-testid="stMarkdownContainer"] *,
            .stMarkdown * {
                color: #e2e8f0 !important;
            }

            .section-title,
            .section-title * {
                color: #ffffff !important;
            }

            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                border-radius: 14px !important;
                overflow: hidden !important;
                border: 1px solid rgba(96,165,250,.26) !important;
                margin-top: 8px !important;
            }

            .ag-theme-streamlit,
            .ag-root-wrapper,
            .ag-root,
            .ag-body,
            .ag-center-cols-container,
            .ag-row,
            .ag-row-even,
            .ag-row-odd {
                background: #0f172a !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,.24) !important;
            }

            .ag-header,
            .ag-header-row,
            .ag-header-cell,
            .ag-paging-panel {
                background: #1e293b !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,.24) !important;
            }

            .ag-cell,
            .ag-cell-value,
            .ag-header-cell-text,
            .ag-paging-panel *,
            .ag-icon {
                color: #f8fafc !important;
            }

            div[data-testid="stButton"] > button,
            div[data-testid="stButton"] > button * {
                color: #ffffff !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def _safe_container(border=True):
    try:
        return st.container(border=border)
    except TypeError:
        return st.container()


def _format_file_size(file_size):
    if not file_size:
        return "-"
    try:
        size = float(file_size)
        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        return f"{size / 1024:.2f} KB"
    except Exception:
        return "-"


def show_file_information_page(
    df,
    file_name,
    file_ext,
    file_size,
    saved_file_path,
    numeric_cols,
    categorical_cols,
    date_cols,
    num_stats,
    cat_stats,
    insights,
    save_visualizations,
    render_summary_interpretation,
    calculate_health_score,
    get_health_label
):
    inject_data_management_css()

    st.markdown('<div class="section-title">📄 Complete File Information</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="dm-hero">
            <div class="dm-title">📄 File Information Center</div>
            <div class="dm-subtitle">
                Ringkasan informasi file yang diunggah, termasuk ukuran data, tipe file, lokasi penyimpanan, dan jumlah variabel.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    rows = int(df.shape[0])
    cols = int(df.shape[1])

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("📄", "File Name", file_name or "-"),
        ("🧱", "Rows", f"{rows:,}"),
        ("📊", "Columns", f"{cols:,}"),
        ("💾", "File Size", _format_file_size(file_size)),
    ]

    for col, (icon, label, value) in zip([k1, k2, k3, k4], kpis):
        with col:
            st.markdown(
                f"""
                <div class="dm-kpi">
                    <div class="dm-kpi-icon">{icon}</div>
                    <div class="dm-kpi-label">{label}</div>
                    <div class="dm-kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    if saved_file_path:
        st.markdown(
            f"""
            <div class="dm-path">
                📁 Saved File Path: <b>{saved_file_path}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    info = pd.DataFrame({
        "Item": [
            "File Name",
            "File Type",
            "Rows",
            "Columns",
            "File Size",
            "Saved File Path",
            "Numerical Variables",
            "Categorical Variables",
            "Date Variables"
        ],
        "Value": [
            file_name or "-",
            str(file_ext).upper() if file_ext else "-",
            rows,
            cols,
            _format_file_size(file_size),
            saved_file_path if saved_file_path else "-",
            len(numeric_cols),
            len(categorical_cols),
            len(date_cols)
        ]
    })

    with _safe_container(border=True):
        st.markdown('<div class="dm-card-title">📌 Detailed File Metadata</div>', unsafe_allow_html=True)
        show_table(info, key="file_info", page_size=10, height=320)


def show_data_preview_page(
    df,
    file_name,
    file_ext,
    file_size,
    saved_file_path,
    numeric_cols,
    categorical_cols,
    date_cols,
    num_stats,
    cat_stats,
    insights,
    save_visualizations,
    render_summary_interpretation,
    calculate_health_score,
    get_health_label
):
    inject_data_management_css()

    st.markdown('<div class="section-title">👀 Data Preview</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="dm-hero">
            <div class="dm-title">👀 Data Preview</div>
            <div class="dm-subtitle">
                Menampilkan isi dataset <b>{file_name or '-'}</b> agar struktur data dapat diperiksa sebelum analisis.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    k1, k2, k3 = st.columns(3)
    kpis = [
        ("🧱", "Total Rows", f"{df.shape[0]:,}"),
        ("📊", "Total Columns", f"{df.shape[1]:,}"),
        ("⚠️", "Missing Values", f"{int(df.isna().sum().sum()):,}"),
    ]

    for col, (icon, label, value) in zip([k1, k2, k3], kpis):
        with col:
            st.markdown(
                f"""
                <div class="dm-kpi">
                    <div class="dm-kpi-icon">{icon}</div>
                    <div class="dm-kpi-label">{label}</div>
                    <div class="dm-kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with _safe_container(border=True):
        st.markdown('<div class="dm-card-title">📋 Dataset Preview</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="dm-desc">Tabel berikut menampilkan data yang sudah dimuat ke dashboard.</div>',
            unsafe_allow_html=True
        )
        show_table(df, key="data_preview", page_size=10, height=430)


def show_dataset_information_page(
    df,
    file_name,
    file_ext,
    file_size,
    saved_file_path,
    numeric_cols,
    categorical_cols,
    date_cols,
    num_stats,
    cat_stats,
    insights,
    save_visualizations,
    render_summary_interpretation,
    calculate_health_score,
    get_health_label
):
    inject_data_management_css()

    st.markdown('<div class="section-title">📌 Dataset Information</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="dm-hero">
            <div class="dm-title">📌 Dataset Information</div>
            <div class="dm-subtitle">
                Informasi struktur dataset, tipe data, missing value, dan jumlah nilai unik pada setiap variabel.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("🔢", "Numerical", f"{len(numeric_cols):,}"),
        ("🏷️", "Categorical", f"{len(categorical_cols):,}"),
        ("📅", "Date", f"{len(date_cols):,}"),
        ("⚠️", "Missing", f"{int(df.isna().sum().sum()):,}"),
    ]

    for col, (icon, label, value) in zip([k1, k2, k3, k4], kpis):
        with col:
            st.markdown(
                f"""
                <div class="dm-kpi">
                    <div class="dm-kpi-icon">{icon}</div>
                    <div class="dm-kpi-label">{label}</div>
                    <div class="dm-kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    try:
        data_info = dataset_information(df)
    except Exception:
        data_info = pd.DataFrame({
            "Variable": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Missing Count": df.isna().sum().values,
            "Missing Percentage (%)": (df.isna().mean() * 100).round(2).values,
            "Unique Values": df.nunique(dropna=True).values
        })

    with _safe_container(border=True):
        st.markdown('<div class="dm-card-title">🧾 Variable Metadata</div>', unsafe_allow_html=True)
        show_table(data_info, key="dataset_info", page_size=10, height=430)
