import os
import streamlit as st
import pandas as pd

from backend.data_loader import load_data, detect_columns
from backend.preprocessing import dataset_information, cleaning_summary, remove_duplicates
from backend.descriptive_stats import numerical_statistics
from backend.categorical_analysis import categorical_statistics
import backend.visualization as viz
import backend.time_series as ts
from backend.insight_generator import generate_insights
from backend.export_report import export_excel, export_csv, export_pdf, export_html
from backend.table_utils import show_table
from backend.chart_interpretation import (
    interpret_histogram,
    interpret_boxplot,
    interpret_density,
    interpret_qq_plot,
    interpret_violin,
    interpret_numeric,

    interpret_bar_chart,
    interpret_pie_chart,
    interpret_count_plot,
    interpret_pareto,
    interpret_categorical,

    interpret_scatter_plot,
    interpret_regression_plot,
    interpret_correlation,
    interpret_heatmap,
    interpret_pair_plot,
    interpret_bubble_chart,

    interpret_boxplot_by_category,
    interpret_violin_by_category,
    interpret_grouped_bar,
    interpret_strip_plot,
    interpret_category_numeric,

    interpret_trend_line,
    interpret_time_series_chart,
    interpret_moving_average,
    interpret_time_series,

    interpretation_box,
    summary_numerical_interpretation,
    summary_categorical_interpretation,
    summary_time_series_interpretation
)



def show_data_cleaning_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    st.markdown('<div class="section-title">🧹 Data Cleaning</div>', unsafe_allow_html=True)

    missing_values = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    rows_before = int(df.shape[0])
    cols_total = int(df.shape[1])

    if missing_values == 0 and duplicate_rows == 0:
        clean_status = "Clean"
        clean_status_icon = "✅"
        clean_status_color = "#16a34a"
        clean_message = "Dataset sudah bersih. Tidak ditemukan missing value maupun duplicate rows."
    elif duplicate_rows > 0 and missing_values == 0:
        clean_status = "Need Deduplication"
        clean_status_icon = "🔁"
        clean_status_color = "#f97316"
        clean_message = "Dataset cukup baik, tetapi masih terdapat duplicate rows yang dapat dibersihkan."
    elif missing_values > 0 and duplicate_rows == 0:
        clean_status = "Need Missing Check"
        clean_status_icon = "⚠️"
        clean_status_color = "#f97316"
        clean_message = "Dataset memiliki missing value yang perlu diperiksa sebelum analisis lanjutan."
    else:
        clean_status = "Need Cleaning"
        clean_status_icon = "🧹"
        clean_status_color = "#dc2626"
        clean_message = "Dataset memiliki missing value dan duplicate rows, sehingga perlu proses cleaning."

    # =========================
    # CLEANING PAGE STYLE
    # =========================
    st.markdown(
        """
        <style>
            .clean-wrap {
                margin-top: -4px;
            }
            .clean-hero {
                background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 45%, #2563eb 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 20px;
                box-shadow: 0 14px 34px rgba(37, 99, 235, 0.24);
                margin-bottom: 14px;
            }
            .clean-title {
                font-size: 24px;
                font-weight: 950;
                margin-bottom: 3px;
            }
            .clean-subtitle {
                font-size: 13px;
                color: #dbeafe;
                font-weight: 600;
                line-height: 1.5;
            }
            .clean-card {
                background: rgba(255,255,255,0.96);
                border: 1px solid rgba(37,99,235,0.12);
                border-radius: 18px;
                padding: 14px 15px;
                box-shadow: 0 8px 22px rgba(15,23,42,0.08);
                margin-bottom: 12px;
            }
            .clean-kpi {
                background: linear-gradient(135deg, #ffffff, #eff6ff);
                border: 1px solid rgba(37,99,235,0.13);
                border-radius: 18px;
                padding: 14px 15px;
                min-height: 112px;
                box-shadow: 0 8px 20px rgba(37,99,235,0.10);
            }
            .clean-kpi-icon {
                font-size: 21px;
                margin-bottom: 5px;
            }
            .clean-kpi-label {
                font-size: 12px;
                font-weight: 800;
                color: #64748b;
            }
            .clean-kpi-value {
                font-size: 31px;
                font-weight: 950;
                color: #0f172a;
                margin-top: 2px;
                line-height: 1.1;
            }
            .clean-card-title {
                font-size: 15px;
                font-weight: 950;
                color: #1e3a8a;
                margin-bottom: 8px;
            }
            .clean-desc {
                font-size: 13px;
                color: #334155;
                line-height: 1.65;
            }
            .clean-status-box {
                background: linear-gradient(135deg, #f8fafc, #eff6ff);
                border: 1px solid rgba(37,99,235,0.14);
                border-left: 6px solid #2563eb;
                border-radius: 18px;
                padding: 14px 16px;
                min-height: 142px;
                box-shadow: 0 8px 20px rgba(15,23,42,0.07);
            }
            .clean-action-box {
                background: linear-gradient(135deg, #ecfeff, #f0f9ff);
                border: 1px solid rgba(6,182,212,0.20);
                border-left: 6px solid #06b6d4;
                border-radius: 18px;
                padding: 14px 16px;
                min-height: 142px;
                box-shadow: 0 8px 20px rgba(6,182,212,0.10);
            }
            .clean-note {
                background: #eff6ff;
                color: #1e3a8a;
                border-left: 5px solid #2563eb;
                border-radius: 12px;
                padding: 9px 12px;
                font-size: 12px;
                font-weight: 700;
                margin-top: 8px;
            }
            .clean-path {
                font-size: 12px;
                color: #64748b;
                background: #f8fafc;
                padding: 8px 10px;
                border-radius: 12px;
                margin-top: 8px;
                border: 1px dashed rgba(37,99,235,0.25);
                word-break: break-all;
            }
            @media (prefers-color-scheme: dark) {
                .clean-card,
                .clean-kpi,
                .clean-status-box,
                .clean-action-box {
                    background: rgba(15,23,42,0.92);
                    color: #e5e7eb;
                    border-color: rgba(96,165,250,0.25);
                }
                .clean-card-title,
                .clean-kpi-value {
                    color: #93c5fd;
                }
                .clean-desc,
                .clean-kpi-label,
                .clean-path {
                    color: #cbd5e1;
                }
                .clean-note,
                .clean-path {
                    background: rgba(30,41,59,0.88);
                    color: #bfdbfe;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="clean-wrap">
            <div class="clean-hero">
                <div class="clean-title">🧹 Data Cleaning Center</div>
                <div class="clean-subtitle">
                    Cek kualitas dataset, missing value, duplicate rows, dan lakukan cleaning data secara cepat.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # KPI CARDS
    # =========================
    k1, k2, k3, k4 = st.columns(4)

    kpi_cards = [
        ("⚠️", "Missing Values", f"{missing_values:,}"),
        ("🔁", "Duplicate Rows", f"{duplicate_rows:,}"),
        ("📄", "Rows Before", f"{rows_before:,}"),
        ("🧱", "Total Columns", f"{cols_total}")
    ]

    for col, (icon, label, value) in zip([k1, k2, k3, k4], kpi_cards):
        with col:
            st.markdown(
                f"""
                <div class="clean-kpi">
                    <div class="clean-kpi-icon">{icon}</div>
                    <div class="clean-kpi-label">{label}</div>
                    <div class="clean-kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =========================
    # STATUS + ACTION
    # =========================
    status_col, action_col = st.columns([1.2, 1])

    with status_col:
        st.markdown(
            f"""
            <div class="clean-status-box">
                <div class="clean-card-title">{clean_status_icon} Cleaning Status</div>
                <div style="font-size:28px;font-weight:950;color:{clean_status_color};line-height:1.15;">
                    {clean_status}
                </div>
                <div class="clean-desc" style="margin-top:8px;">
                    {clean_message}
                </div>
                <div class="clean-note">
                    Data cleaning membantu memastikan hasil statistik, visualisasi, dan insight lebih akurat.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with action_col:
        st.markdown(
            """
            <div class="clean-action-box">
                <div class="clean-card-title">🚀 Cleaning Action</div>
                <div class="clean-desc">
                    Gunakan tombol di bawah untuk menghapus duplicate rows. File hasil cleaning akan otomatis tersimpan ke folder <b>data/processed</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🧹 Remove Duplicate Rows", use_container_width=True):
            try:
                clean_df = remove_duplicates(df)
            except Exception:
                clean_df = df.drop_duplicates()

            os.makedirs("data/processed", exist_ok=True)
            processed_path = os.path.join("data", "processed", f"cleaned_{file_name}")
            clean_df.to_csv(processed_path, index=False)

            st.session_state.df = clean_df

            st.toast(f"cleaned_{file_name} berhasil disimpan", icon="✅")
            st.toast("Cleaned data tersimpan di folder processed", icon="📁")

            rows_after = clean_df.shape[0]
            removed_rows = rows_before - rows_after

            st.success(f"Cleaning selesai. {removed_rows} duplicate rows dihapus.")
            st.markdown(
                f"""
                <div class="clean-path">
                    📁 Saved cleaned file: <b>{processed_path}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            show_table(clean_df.head(10), key="cleaned_preview", page_size=10, height=300)

    # =========================
    # CLEANING SUMMARY + MISSING DETAIL
    # =========================
    summary_col, missing_col = st.columns([1, 1.25])

    with summary_col:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="clean-card-title">📌 Cleaning Summary</div>', unsafe_allow_html=True)

        try:
            clean_summary = cleaning_summary(df)
        except Exception:
            clean_summary = pd.DataFrame({
                "Item": ["Total Rows", "Total Columns", "Missing Values", "Duplicate Rows"],
                "Value": [df.shape[0], df.shape[1], df.isna().sum().sum(), df.duplicated().sum()]
            })

        show_table(clean_summary, key="cleaning_summary", page_size=10, height=270)
        st.markdown('</div>', unsafe_allow_html=True)

    with missing_col:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="clean-card-title">⚠️ Missing Value per Variable</div>', unsafe_allow_html=True)

        missing_detail = pd.DataFrame({
            "Variable": df.columns,
            "Missing Count": df.isna().sum().values,
            "Missing Percentage (%)": (df.isna().mean() * 100).round(2).values
        }).sort_values("Missing Count", ascending=False)

        show_table(missing_detail, key="missing_detail", page_size=10, height=270)
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # NAVIGATION BUTTONS
    # =========================
    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()

    with nav2:
        if st.button("👀 Data Preview", use_container_width=True):
            st.session_state.page = "Data Preview"
            st.rerun()

    with nav3:
        if st.button("📊 Numerical Statistics", use_container_width=True):
            st.session_state.page = "Numerical Variables"
            st.rerun()


