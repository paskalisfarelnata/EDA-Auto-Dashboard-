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



def show_upload_page():
    st.markdown('<div class="section-title">📁 Upload Data</div>', unsafe_allow_html=True)

    # =====================================================
    # FAST UPLOAD DATA PAGE
    # =====================================================

    st.markdown(
        """
        <style>
            .upload-hero {
                background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 45%, #2563eb 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 20px;
                box-shadow: 0 14px 32px rgba(37,99,235,0.22);
                margin-bottom: 14px;
            }

            .upload-hero-title {
                font-size: 24px;
                font-weight: 950;
                margin-bottom: 3px;
            }

            .upload-hero-subtitle {
                font-size: 13px;
                color: #dbeafe;
                font-weight: 600;
                line-height: 1.5;
            }

            .upload-card {
                background: rgba(255,255,255,0.96);
                border: 1px solid rgba(37,99,235,0.12);
                border-radius: 18px;
                padding: 15px;
                box-shadow: 0 8px 20px rgba(15,23,42,0.08);
                min-height: 130px;
                margin-bottom: 12px;
            }

            .upload-card-title {
                font-size: 15px;
                font-weight: 950;
                color: #1e3a8a;
                margin-bottom: 7px;
            }

            .upload-desc {
                font-size: 13px;
                line-height: 1.65;
                color: #334155;
            }

            .upload-kpi {
                background: linear-gradient(135deg, #ffffff, #eff6ff);
                border: 1px solid rgba(37,99,235,0.13);
                border-radius: 18px;
                padding: 13px 14px;
                min-height: 100px;
                box-shadow: 0 8px 18px rgba(37,99,235,0.10);
            }

            .upload-kpi-icon {
                font-size: 20px;
                margin-bottom: 4px;
            }

            .upload-kpi-label {
                font-size: 12px;
                font-weight: 800;
                color: #64748b;
            }

            .upload-kpi-value {
                font-size: 28px;
                font-weight: 950;
                color: #0f172a;
                margin-top: 2px;
                line-height: 1.15;
            }

            .upload-success-box {
                background: linear-gradient(135deg, #ecfdf5, #eff6ff);
                border: 1px solid rgba(34,197,94,0.25);
                border-left: 6px solid #22c55e;
                border-radius: 16px;
                padding: 12px 14px;
                font-size: 13px;
                font-weight: 750;
                color: #14532d;
                margin: 12px 0;
            }

            .upload-path {
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
                .upload-card,
                .upload-kpi {
                    background: rgba(15,23,42,0.92);
                    color: #e5e7eb;
                    border-color: rgba(96,165,250,0.25);
                }

                .upload-card-title,
                .upload-kpi-value {
                    color: #93c5fd;
                }

                .upload-desc,
                .upload-kpi-label,
                .upload-path {
                    color: #cbd5e1;
                }

                .upload-path {
                    background: rgba(30,41,59,0.88);
                }

                .upload-success-box {
                    background: rgba(20,83,45,0.35);
                    color: #bbf7d0;
                    border-color: rgba(34,197,94,0.28);
                }
            }
        </style>


        """,
        unsafe_allow_html=True
    )

    upload_col, guide_col = st.columns([1.45, 1])

    with upload_col:
        st.markdown(
            """
            <div class="upload-card">
                <div class="upload-card-title">📤 Upload File Area</div>
                <div class="upload-desc">
                    Pilih dataset yang akan dianalisis. Setelah upload berhasil,
                    dashboard akan menampilkan summary jumlah baris, kolom, format,
                    ukuran file, dan preview data.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "Upload Dataset CSV / XLSX / TXT",
            type=["csv", "xlsx", "txt"],
            label_visibility="collapsed"
        )



    if uploaded_file is not None:
        try:
            os.makedirs("data/raw", exist_ok=True)

            save_path = os.path.join("data", "raw", uploaded_file.name)

            with open(save_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

            with st.spinner("Membaca dataset..."):
                df, file_ext = load_data(uploaded_file)

            st.session_state.df = df
            st.session_state.file_name = uploaded_file.name
            st.session_state.file_ext = file_ext
            st.session_state.file_size = uploaded_file.size
            st.session_state.saved_file_path = save_path

            st.toast("Dataset berhasil diupload", icon="✅")
            st.toast(f"File tersimpan: {uploaded_file.name}", icon="📁")

            st.markdown(
                f"""
                <div class="upload-success-box">
                    ✅ Dataset berhasil diupload dan diproses otomatis.<br>
                    File aktif: <b>{uploaded_file.name}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### 📌 File Summary")
            c1, c2, c3, c4 = st.columns(4)

            summary_cards = [
                ("📄", "Rows", f"{df.shape[0]:,}"),
                ("🧱", "Columns", f"{df.shape[1]}"),
                ("📦", "Format", str(file_ext).upper()),
                ("💾", "File Size", f"{uploaded_file.size / 1024:.2f} KB")
            ]

            for col, (icon, label, value) in zip([c1, c2, c3, c4], summary_cards):
                with col:
                    st.markdown(
                        f"""
                        <div class="upload-kpi">
                            <div class="upload-kpi-icon">{icon}</div>
                            <div class="upload-kpi-label">{label}</div>
                            <div class="upload-kpi-value">{value}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown(
                f"""
                <div class="upload-path">
                    📁 Saved file path: <b>{save_path}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            nav1, nav2, nav3 = st.columns(3)

            with nav1:
                if st.button("🏠 Go to Dashboard", use_container_width=True):
                    st.session_state.page = "Dashboard"
                    st.rerun()

            with nav2:
                if st.button("📌 Dataset Information", use_container_width=True):
                    st.session_state.page = "Dataset Information"
                    st.rerun()

            with nav3:
                if st.button("🧹 Data Cleaning", use_container_width=True):
                    st.session_state.page = "Data Cleaning"
                    st.rerun()

        except Exception as e:
            st.toast("Upload gagal", icon="❌")
            st.error("Upload gagal.")
            st.code(str(e))
    st.stop()

