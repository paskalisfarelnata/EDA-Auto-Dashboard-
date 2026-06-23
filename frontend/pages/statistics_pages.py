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


# =====================================================
# STATISTICS PAGE DARK THEME
# =====================================================
def inject_statistics_page_css():
    st.markdown(
        """
        <style>
            section.main div[data-testid="stMarkdownContainer"],
            section.main div[data-testid="stMarkdownContainer"] *,
            section.main p,
            section.main li,
            section.main span,
            section.main label {
                color: #EAF6FF !important;
                opacity: 1 !important;
            }
            .section-title,
            .section-title * {
                color: #FFFFFF !important;
                opacity: 1 !important;
                font-weight: 1000 !important;
            }
            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                border-radius: 16px !important;
                overflow: hidden !important;
                border: 1px solid rgba(103, 232, 249, .22) !important;
                box-shadow: 0 14px 34px rgba(0, 0, 0, .22) !important;
            }
            .ag-theme-streamlit,
            .ag-root-wrapper,
            .ag-root,
            .ag-body,
            .ag-center-cols-container,
            .ag-row,
            .ag-row-even,
            .ag-row-odd {
                background: #0F172A !important;
                color: #EAF6FF !important;
                border-color: rgba(103, 232, 249, .18) !important;
            }
            .ag-header,
            .ag-header-row,
            .ag-header-cell,
            .ag-paging-panel {
                background: #1E293B !important;
                color: #FFFFFF !important;
                border-color: rgba(103, 232, 249, .18) !important;
            }
            .ag-cell,
            .ag-cell-value,
            .ag-header-cell-text,
            .ag-paging-panel *,
            .ag-icon {
                color: #EAF6FF !important;
                opacity: 1 !important;
            }
            div[data-testid="stAlert"] *,
            div[data-testid="stWarning"] * {
                color: #F8FAFC !important;
                opacity: 1 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def show_numerical_variables_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    inject_statistics_page_css()
    st.markdown('<div class="section-title">📊 Numerical Variables Statistics</div>', unsafe_allow_html=True)

    if len(num_stats) > 0:
        show_table(num_stats, key="num_stats", page_size=10)
    else:
        st.warning("Tidak ada variabel numerik.")




def show_categorical_variables_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    inject_statistics_page_css()
    st.markdown('<div class="section-title">🏷️ Categorical Variables Statistics</div>', unsafe_allow_html=True)

    if len(cat_stats) > 0:
        show_table(cat_stats, key="cat_stats", page_size=10)
    else:
        st.warning("Tidak ada variabel kategorik.")


