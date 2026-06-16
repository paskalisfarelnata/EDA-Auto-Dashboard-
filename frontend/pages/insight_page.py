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


def show_insight_generator_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
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
