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



def inject_insight_full_width_css():
    st.markdown(
        """
        <style>
            /* =====================================================
               INSIGHT FULL WIDTH FINAL
               Merapikan ruang kosong kiri-kanan khusus halaman
               Intelligent Insight Generator tanpa mengubah logic lama.
               ===================================================== */

            .main .block-container,
            section.main .block-container,
            div[data-testid="stMainBlockContainer"],
            div[data-testid="stAppViewContainer"] .block-container {
                width: 100% !important;
                max-width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 0.75rem !important;
                padding-bottom: 1rem !important;
                box-sizing: border-box !important;
            }

            section.main div[data-testid="stVerticalBlock"],
            section.main div[data-testid="stVerticalBlock"] > div {
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }

            section.main div[data-testid="stHorizontalBlock"] {
                width: 100% !important;
                max-width: 100% !important;
                gap: 1rem !important;
                box-sizing: border-box !important;
            }

            /* Judul halaman insight dibuat melebar rapi */
            section.main .section-title {
                width: 100% !important;
                max-width: 100% !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
                box-sizing: border-box !important;
            }

            /* Box insight utama memenuhi lebar area konten */
            section.main .insight-box {
                width: 100% !important;
                max-width: 100% !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
                margin-bottom: 1.05rem !important;
                padding: 1.55rem 1.75rem !important;
                box-sizing: border-box !important;
                border-radius: 24px !important;
                background:
                    linear-gradient(135deg, rgba(8, 20, 38, .98), rgba(15, 23, 42, .96)) !important;
                border: 1px solid rgba(103, 232, 249, .22) !important;
                box-shadow: 0 16px 34px rgba(0, 0, 0, .20) !important;
            }

            section.main .insight-box h4 {
                color: #FFFFFF !important;
                opacity: 1 !important;
                font-weight: 1000 !important;
                letter-spacing: .04em !important;
                line-height: 1.25 !important;
            }

            section.main .insight-box div,
            section.main .insight-box p,
            section.main .insight-box span,
            section.main .insight-box li {
                color: #EAF6FF !important;
                opacity: 1 !important;
                filter: none !important;
                text-shadow: none !important;
                font-weight: 700 !important;
            }

            /* Supaya teks panjang tidak membuat card terasa sempit */
            section.main .insight-box div[style*="line-height"] {
                width: 100% !important;
                max-width: 100% !important;
                line-height: 1.75 !important;
                font-size: 17px !important;
                box-sizing: border-box !important;
            }

            /* Override class atau style lama yang membatasi lebar */
            section.main [class*="insight"],
            section.main [class*="Insight"] {
                max-width: 100% !important;
                box-sizing: border-box !important;
            }

            @media (max-width: 900px) {
                .main .block-container,
                section.main .block-container,
                div[data-testid="stMainBlockContainer"] {
                    padding-left: 0.75rem !important;
                    padding-right: 0.75rem !important;
                }

                section.main .insight-box {
                    padding: 1.1rem 1.05rem !important;
                    border-radius: 18px !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )



def show_insight_generator_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    inject_insight_full_width_css()
    st.markdown(
        '<div class="section-title">🧠 Intelligent Insight Generator</div>',
        unsafe_allow_html=True
    )

    section_titles = [
        "📊 DATASET OVERVIEW",
        "⚠ MISSING VALUE INSIGHT",
        "🔢 NUMERICAL INSIGHT",
        "📋 CATEGORICAL INSIGHT",
        "🔗 CORRELATION INSIGHT",
        "📈 TIME SERIES INSIGHT",
        "💡 FINAL BUSINESS INSIGHT"
    ]

    current_title = None
    current_content = []

    for item in insights:
        if item in section_titles:
            if current_title is not None:
                content_html = "<br>".join(current_content)

                st.markdown(
                    f"""
                    <div class="insight-box">
                        <h4 style="margin-top:0; margin-bottom:12px;">
                            {current_title}
                        </h4>
                        <div style="line-height:1.8; font-size:16px;">
                            {content_html}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            current_title = item
            current_content = []

        elif item.strip() != "":
            current_content.append(item)

    if current_title is not None:
        content_html = "<br>".join(current_content)

        st.markdown(
            f"""
            <div class="insight-box">
                <h4 style="margin-top:0; margin-bottom:12px;">
                    {current_title}
                </h4>
                <div style="line-height:1.8; font-size:16px;">
                    {content_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    # =========================
    # REPORTING SYSTEM
    # =========================
