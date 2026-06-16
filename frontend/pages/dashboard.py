import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
# ROUTING HELPER
# =====================================================
def dashboard_go_to(page_name):
    st.session_state.page = page_name
    st.rerun()


# =====================================================
# SMALL UTILITIES
# =====================================================
PLOT_CONFIG = {
    "displayModeBar": False,
    "responsive": True
}


PASTEL_COLORS = [
    "#F8A5C2",  # pink
    "#85C1E9",  # blue
    "#82E0AA",  # green
    "#D7BDE2",  # lilac
    "#F9E79F",  # yellow
    "#A3E4D7",  # mint
]

PASTEL_HEATMAP = [
    [0.00, "#F8A5C2"],
    [0.50, "#85C1E9"],
    [1.00, "#82E0AA"],
]


def _style_plot(fig, height=250, title=None, color_index=0):
    safe_title = "" if title is None else str(title).strip()
    base_color = PASTEL_COLORS[color_index % len(PASTEL_COLORS)]

    fig.update_layout(
        template="plotly_dark",
        height=height,
        title=dict(
            text=safe_title if safe_title else " ",
            x=0.5,
            xanchor="center",
            font=dict(size=14, color="#FFFFFF")
        ),
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        font=dict(color="#EAF6FF", size=11),
        margin=dict(l=35, r=35, t=45, b=45),
        colorway=PASTEL_COLORS,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#EAF6FF"),
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.10)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.18)",
        tickfont=dict(color="#DFF6FF"),
        title_font=dict(color="#EAF6FF")
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.10)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.18)",
        tickfont=dict(color="#DFF6FF"),
        title_font=dict(color="#EAF6FF")
    )

    for i, trace in enumerate(fig.data):
        color = PASTEL_COLORS[(color_index + i) % len(PASTEL_COLORS)]
        trace_type = getattr(trace, "type", "")

        if trace_type in ["histogram", "bar"]:
            trace.update(
                marker=dict(
                    color=color,
                    line=dict(color="rgba(255,255,255,0.35)", width=1)
                )
            )

        elif trace_type in ["box", "violin"]:
            trace.update(
                marker=dict(color=color),
                line=dict(color=color),
                fillcolor=color
            )

        elif trace_type in ["scatter", "scattergl"]:
            trace.update(
                marker=dict(
                    color=color,
                    size=8,
                    opacity=0.75,
                    line=dict(color="rgba(255,255,255,0.45)", width=1)
                ),
                line=dict(color=color, width=3)
            )

        elif trace_type == "pie":
            trace.update(
                marker=dict(
                    colors=PASTEL_COLORS,
                    line=dict(color="#0f172a", width=2)
                ),
                textfont=dict(color="#FFFFFF")
            )

        elif trace_type == "heatmap":
            trace.update(colorscale=PASTEL_HEATMAP)

    return fig


def _safe_file_size(file_size):
    if not file_size:
        return "-"
    try:
        size_kb = file_size / 1024
        if size_kb >= 1024:
            return f"{size_kb / 1024:.2f} MB"
        return f"{size_kb:.2f} KB"
    except Exception:
        return "-"


def _truncate_text(value, limit=34):
    value = str(value) if value is not None else "-"
    return value if len(value) <= limit else value[:limit - 3] + "..."


def _first_numeric(df, numeric_cols):
    for col in numeric_cols:
        if col in df.columns and df[col].dropna().shape[0] > 0:
            return col
    return None


def _first_categorical(df, categorical_cols):
    for col in categorical_cols:
        if col in df.columns and df[col].dropna().shape[0] > 0:
            return col
    return None


def _first_date(df, date_cols):
    for col in date_cols:
        if col in df.columns:
            return col
    return None


def _clean_stats_preview(stats_df, max_rows=6, max_cols=6):
    if isinstance(stats_df, pd.DataFrame) and not stats_df.empty:
        return stats_df.head(max_rows).iloc[:, :max_cols]
    return pd.DataFrame({"Info": ["Summary belum tersedia"]})


# =====================================================
# CSS
# =====================================================

def _safe_card_container(border=True):
    """Container aman untuk Streamlit component agar tidak membuat box kosong di atas tabel/chart."""
    try:
        return st.container(border=border)
    except TypeError:
        return st.container()


def inject_bi_dashboard_css():
    st.markdown(
        """
        <style>

            /* Header dashboard tanpa tagline */
            .inv-title-card .inv-desc {
                margin-top: 18px !important;
            }


            /* Quick Actions: hilangkan judul dobel dan rapikan judul yang tersisa */
            .inv-quick-compact .bi-action-title {
                color: #e5e7eb !important;
                font-size: 15px !important;
                font-weight: 1000 !important;
                margin-bottom: 10px !important;
                opacity: 1 !important;
            }


            /* =====================================================
               TOP DATASET PREVIEW ALIGN PATCH
               Menurunkan sedikit tabel Top Dataset Preview agar sejajar
               dengan card di sebelahnya tanpa mengubah isi data.
               ===================================================== */

            .inv-preview-table-align {
                margin-top: 10px !important;
            }

            .inv-preview-table-align div[data-testid="stDataFrame"] {
                margin-top: 0 !important;
            }


            /* =====================================================
               LOW QUALITY CARD HEIGHT BALANCE FINAL
               Membesarkan tabel Low Quality dan Data Quality Summary
               agar tidak ada ruang kosong di bawah card.
               ===================================================== */

            .inv-lowquality-table {
                margin-bottom: 10px !important;
            }

            .inv-lowquality-table div[data-testid="stDataFrame"] {
                min-height: 220px !important;
                max-height: 240px !important;
                border-radius: 14px !important;
            }

            .inv-lowquality-table div[data-testid="stDataFrame"] [role="grid"] {
                min-height: 210px !important;
            }

            .inv-quality-summary {
                margin-top: 10px !important;
                padding: 13px 14px !important;
                min-height: 126px !important;
                border-radius: 16px !important;
            }

            .inv-quality-title {
                font-size: 13.2px !important;
                margin-bottom: 10px !important;
                line-height: 1.2 !important;
            }

            .inv-quality-row {
                font-size: 12.2px !important;
                line-height: 1.38 !important;
                padding: 6px 0 !important;
            }

            .inv-quality-value {
                font-size: 12.2px !important;
            }


            /* =====================================================
               TABLE + SUMMARY RESTORE PATCH
               Mengembalikan tabel Low Quality Alert, menaruh Data
               Quality Summary di bawahnya, dan mengisi ruang kanan.
               ===================================================== */

            .inv-quality-summary {
                margin-top: 7px;
                border-radius: 14px;
                border: 1px solid rgba(125, 211, 252, .22);
                background: linear-gradient(135deg, rgba(15,23,42,.96), rgba(30,41,59,.92));
                padding: 8px 10px;
                min-height: 0;
            }

            .inv-quality-title {
                color: #67e8f9;
                font-size: 12.2px;
                font-weight: 1000;
                letter-spacing: .04em;
                text-transform: uppercase;
                margin-bottom: 5px;
                line-height: 1.1;
            }

            .inv-quality-row {
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 8px;
                align-items: center;
                color: #e5e7eb;
                font-size: 11px;
                font-weight: 800;
                line-height: 1.18;
                padding: 2.5px 0;
                border-bottom: 1px solid rgba(148,163,184,.10);
            }

            .inv-quality-row:last-child {
                border-bottom: 0;
            }

            .inv-quality-value {
                color: #86efac;
                font-weight: 1000;
                text-align: right;
                white-space: nowrap;
            }

            .inv-right-fill {
                margin-top: 8px;
                border-radius: 15px;
                border: 1px solid rgba(125, 211, 252, .20);
                background: linear-gradient(135deg, rgba(15,23,42,.96), rgba(30,41,59,.92));
                padding: 10px 12px;
                box-shadow: 0 10px 24px rgba(0,0,0,.12);
            }

            .inv-right-fill-title {
                color: #67e8f9;
                font-size: 12.5px;
                font-weight: 1000;
                letter-spacing: .04em;
                text-transform: uppercase;
                margin-bottom: 6px;
            }

            .inv-right-fill-item {
                display: flex;
                gap: 7px;
                align-items: flex-start;
                color: #e5e7eb;
                font-size: 10.8px;
                font-weight: 800;
                line-height: 1.28;
                margin: 5px 0;
            }

            .inv-right-fill-item span:first-child {
                color: #86efac;
                font-weight: 1000;
            }

            .inv-side-status {
                margin-top: 7px !important;
                padding: 9px 11px !important;
            }

            .inv-side-status-title {
                font-size: 12.2px !important;
                margin-bottom: 5px !important;
            }

            .inv-side-status-item {
                font-size: 10.7px !important;
                line-height: 1.22 !important;
                margin: 4px 0 !important;
            }

            /* Tabel Low Quality agar tidak terlalu tinggi tetapi tetap terlihat */
            .inv-lowquality-table div[data-testid="stDataFrame"] {
                max-height: 168px !important;
            }


            /* =====================================================
               FINAL COMPACT BALANCE PATCH
               Menghilangkan ruang kosong bawah, mencegah card melewati
               garis pembatas, dan membuat panel kanan lebih compact.
               ===================================================== */

            .inv-compact-alert {
                border-radius: 14px;
                border: 1px solid rgba(125, 211, 252, .22);
                background: linear-gradient(135deg, rgba(15,23,42,.96), rgba(30,41,59,.92));
                padding: 10px 12px;
                margin-top: 4px;
                margin-bottom: 0;
            }

            .inv-compact-alert-title {
                color: #67e8f9;
                font-size: 12.5px;
                font-weight: 1000;
                letter-spacing: .04em;
                text-transform: uppercase;
                margin-bottom: 7px;
            }

            .inv-compact-row {
                display: grid;
                grid-template-columns: 1fr auto auto;
                gap: 8px;
                align-items: center;
                padding: 5px 0;
                border-bottom: 1px solid rgba(148,163,184,.12);
                font-size: 11.4px;
                line-height: 1.25;
                color: #e5e7eb;
                font-weight: 800;
            }

            .inv-compact-row:last-child {
                border-bottom: 0;
            }

            .inv-compact-value {
                color: #ffffff;
                font-weight: 950;
                text-align: right;
                min-width: 48px;
            }

            .inv-compact-status {
                color: #86efac;
                font-weight: 1000;
                text-align: right;
                min-width: 72px;
            }

            .inv-side-status {
                margin-top: 6px !important;
                padding: 8px 10px !important;
                border-radius: 14px !important;
                min-height: 0 !important;
            }

            .inv-side-status-title {
                font-size: 12px !important;
                margin-bottom: 4px !important;
                line-height: 1.15 !important;
            }

            .inv-side-status-item {
                font-size: 10.6px !important;
                line-height: 1.18 !important;
                margin: 4px 0 !important;
                gap: 6px !important;
            }

            /* Quick action card dibuat tidak terlalu tinggi */
            .inv-quick-compact div[data-testid="stButton"] > button {
                min-height: 58px !important;
                padding: 8px 6px !important;
                font-size: 12px !important;
                line-height: 1.25 !important;
            }

            /* Hilangkan jarak bawaan Streamlit yang membuat area kosong */
            div[data-testid="stVerticalBlock"] {
                gap: .55rem !important;
            }

            div[data-testid="stHorizontalBlock"] {
                gap: .65rem !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                overflow: hidden !important;
                margin-bottom: 0 !important;
            }

            .inv-mini-summary {
                margin-top: 6px !important;
                margin-bottom: 0 !important;
                min-height: 0 !important;
                padding: 8px 10px !important;
            }

            .inv-mini-row {
                padding: 2px 0 !important;
                line-height: 1.2 !important;
            }

            .inv-mini-summary-title {
                margin-bottom: 4px !important;
            }



            /* Rapikan jarak antar baris dashboard agar tidak ada ruang kosong berlebihan */
            div[data-testid="stHorizontalBlock"] {
                gap: 0.75rem !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                margin-bottom: 0 !important;
            }

            .inv-mini-summary + div,
            div + .inv-mini-summary {
                margin-top: 4px !important;
            }


            /* =====================================================
               FILL EMPTY SPACE PATCH
               Mengisi ruang kosong di bawah Low Quality Alert dan
               panel kanan agar dashboard terlihat penuh dan sejajar.
               ===================================================== */

            .inv-mini-summary {
                margin-top: 4px;
                border-radius: 14px;
                border: 1px solid rgba(125, 211, 252, .22);
                background:
                    linear-gradient(135deg, rgba(15,23,42,.96), rgba(30,41,59,.92));
                padding: 8px 11px;
                min-height: 68px;
            }

            .inv-mini-summary-title {
                color: #67e8f9;
                font-size: 12.2px;
                font-weight: 1000;
                letter-spacing: .04em;
                text-transform: uppercase;
                margin-bottom: 5px;
            }

            .inv-mini-row {
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 8px;
                color: #e5e7eb;
                font-size: 11.2px;
                font-weight: 750;
                line-height: 1.30;
                padding: 2px 0;
                border-bottom: 1px solid rgba(148,163,184,.10);
            }

            .inv-mini-row:last-child {
                border-bottom: 0;
            }

            .inv-mini-value {
                color: #86efac;
                font-weight: 950;
                text-align: right;
            }

            .inv-side-status {
                margin-top: 8px;
                border-radius: 16px;
                border: 1px solid rgba(134,239,172,.24);
                background: linear-gradient(135deg, rgba(236,253,245,.98), rgba(239,246,255,.96));
                color: #0f172a;
                padding: 10px 12px;
                box-shadow: 0 10px 25px rgba(15,23,42,.10);
            }

            .inv-side-status-title {
                color: #14532d;
                font-weight: 1000;
                font-size: 12.8px;
                text-transform: uppercase;
                letter-spacing: .05em;
                margin-bottom: 6px;
            }

            .inv-side-status-item {
                display: flex;
                gap: 8px;
                align-items: flex-start;
                color: #166534;
                font-size: 11.2px;
                font-weight: 850;
                line-height: 1.28;
                margin: 5px 0;
            }

            .inv-side-status-item span:first-child {
                color: #16a34a;
                font-weight: 1000;
            }



            /* Samakan tinggi dan ruang visual preview atas */
            .inv-visual-card-fix div[data-testid="stPlotlyChart"] {
                min-height: 265px !important;
            }

            div[data-testid="stPlotlyChart"] {
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }

            div[data-testid="stPlotlyChart"] > div {
                width: 100% !important;
            }


            /* =====================================================
               INVENTORY STYLE TIDY PATCH
               Rapi seperti referensi, menghapus ruang kosong, dan
               tidak memakai tag div penutup tunggal.
               ===================================================== */

            .main .block-container,
            section.main .block-container,
            div[data-testid="stMainBlockContainer"],
            div[data-testid="stAppViewContainer"] .block-container {
                max-width: 100% !important;
                width: 100% !important;
                padding: .55rem .9rem 1rem .9rem !important;
            }

            .inv-top {
                margin-top: 0 !important;
                margin-bottom: 10px !important;
                gap: 12px !important;
            }

            .inv-title-card,
            .inv-benefit-card {
                min-height: 126px !important;
                border-radius: 20px !important;
            }

            .inv-title-card {
                padding: 16px 22px !important;
            }

            .inv-title {
                font-size: clamp(32px, 3.25vw, 50px) !important;
                letter-spacing: .07em !important;
            }

            .inv-tagline {
                margin-top: 6px !important;
                font-size: 16px !important;
            }

            .inv-desc {
                margin-top: 8px !important;
                max-width: 940px !important;
            }

            .inv-benefit-card {
                padding: 15px 18px !important;
            }

            .inv-benefit-item {
                margin: 4px 0 !important;
                line-height: 1.42 !important;
            }

            .inv-metric-grid {
                grid-template-columns: repeat(6, minmax(0, 1fr)) !important;
                gap: 10px !important;
                margin: 10px 0 10px !important;
            }

            .inv-metric {
                min-height: 90px !important;
                padding: 12px 12px !important;
                border-radius: 16px !important;
                grid-template-columns: 40px 1fr !important;
            }

            .inv-metric-value {
                font-size: 23px !important;
            }

            .inv-metric-sub {
                font-size: 10.8px !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 16px !important;
                padding: .75rem !important;
                background: rgba(15, 23, 42, .90) !important;
                border: 1px solid rgba(148, 163, 184, .24) !important;
                box-shadow: 0 10px 25px rgba(0,0,0,.16) !important;
            }

            .inv-card-title,
            .bi-card-title {
                font-size: 13px !important;
                margin-bottom: 6px !important;
                line-height: 1.35 !important;
            }

            div[data-testid="stDataFrame"] {
                border-radius: 12px !important;
                overflow: hidden !important;
                border: 1px solid rgba(125, 211, 252, .18) !important;
            }

            div[data-testid="stPlotlyChart"] {
                width: 100% !important;
            }

            .inv-panel {
                margin-bottom: 10px !important;
                border-radius: 16px !important;
                padding: 13px 14px !important;
            }

            .inv-panel-title {
                font-size: 14px !important;
                margin-bottom: 8px !important;
            }

            .inv-step {
                margin: 8px 0 !important;
                gap: 8px !important;
            }

            .inv-step-text,
            .inv-bullet {
                font-size: 11.8px !important;
                line-height: 1.38 !important;
            }

            .inv-best {
                margin-top: 10px !important;
                grid-template-columns: 120px repeat(5, 1fr) !important;
            }

            .inv-best-item {
                min-height: 64px !important;
                padding: 10px 11px !important;
            }

            @media (max-width: 1200px) {
                .inv-metric-grid {
                    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
                }
                .inv-top {
                    grid-template-columns: 1fr !important;
                }
                .inv-best {
                    grid-template-columns: 1fr !important;
                }
            }


            /* =====================================================
               INVENTORY-STYLE MAIN DASHBOARD
               ===================================================== */
            .main .block-container,
            section.main .block-container,
            div[data-testid="stMainBlockContainer"],
            div[data-testid="stAppViewContainer"] .block-container {
                max-width: 100% !important;
                width: 100% !important;
                padding-left: 1.05rem !important;
                padding-right: 1.05rem !important;
                padding-top: .8rem !important;
            }
            .inv-page { width: 100%; max-width: 100%; margin: 0; padding: 0; }
            .inv-top { display: grid; grid-template-columns: 1.2fr .78fr; gap: 14px; align-items: stretch; margin-bottom: 12px; }
            .inv-title-card {
                border-radius: 22px; border: 1px solid rgba(125, 211, 252, .28);
                background: radial-gradient(circle at 3% 0%, rgba(34, 211, 238, .18), transparent 24%), linear-gradient(135deg, rgba(15,23,42,.98), rgba(30,64,175,.92));
                box-shadow: 0 18px 42px rgba(37,99,235,.17); padding: 18px 22px; min-height: 132px; display: flex; flex-direction: column; justify-content: center;
            }
            .inv-title { font-size: clamp(30px, 3.25vw, 52px); font-weight: 1000; letter-spacing: .035em; color: #f8fafc; line-height: 1; text-transform: uppercase; }
            .inv-tagline { margin-top: 7px; font-size: 17px; font-weight: 950; letter-spacing: .09em; color: #86efac; text-transform: uppercase; }
            .inv-desc { margin-top: 9px; font-size: 13px; line-height: 1.55; color: #dbeafe; max-width: 780px; font-weight: 650; }
            .inv-benefit-card { border-radius: 22px; border: 1px solid rgba(134,239,172,.25); background: linear-gradient(135deg, rgba(236,253,245,.98), rgba(239,246,255,.96)); color: #0f172a; padding: 16px 18px; box-shadow: 0 18px 42px rgba(15,23,42,.12); min-height: 132px; }
            .inv-benefit-title { font-size: 15px; font-weight: 1000; color: #14532d; letter-spacing: .05em; text-transform: uppercase; margin-bottom: 8px; }
            .inv-benefit-item { display: flex; gap: 8px; align-items: flex-start; font-size: 12.5px; font-weight: 800; color: #166534; line-height: 1.45; margin: 5px 0; }
            .inv-benefit-item span:first-child { color: #16a34a; font-weight: 1000; }
            .inv-metric-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 11px; margin: 10px 0 14px; }
            .inv-metric { min-height: 95px; border-radius: 18px; border: 1px solid rgba(148,163,184,.25); background: rgba(15,23,42,.92); display: grid; grid-template-columns: 42px 1fr; gap: 9px; align-items: center; padding: 13px; box-shadow: 0 12px 28px rgba(0,0,0,.18); }
            .inv-metric-icon { font-size: 25px; line-height: 1; }
            .inv-metric-title { font-size: 10.5px; color: #94a3b8; font-weight: 950; text-transform: uppercase; letter-spacing: .07em; line-height: 1.4; }
            .inv-metric-value { color: #f8fafc; font-size: 24px; font-weight: 1000; line-height: 1.15; margin-top: 5px; }
            .inv-metric-sub { margin-top: 2px; font-size: 11px; color: #cbd5e1; font-weight: 750; }
            .inv-good { border-color: rgba(34,197,94,.34); }
            .inv-warn { border-color: rgba(245,158,11,.38); }
            .inv-bad { border-color: rgba(239,68,68,.40); }
            .inv-blue { border-color: rgba(96,165,250,.40); }
            .inv-purple { border-color: rgba(192,132,252,.38); }
            .inv-layout { display: grid; grid-template-columns: minmax(0, 1fr) 292px; gap: 14px; align-items: start; }
            .inv-panel { border-radius: 18px; border: 1px solid rgba(148,163,184,.25); background: rgba(255,255,255,.97); color: #0f172a; padding: 14px 15px; box-shadow: 0 12px 28px rgba(15,23,42,.10); margin-bottom: 12px; }
            .inv-panel-title { font-size: 15px; font-weight: 1000; color: #0f172a; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 10px; display: flex; gap: 8px; align-items: center; }
            .inv-step { display: grid; grid-template-columns: 25px 1fr; gap: 9px; margin: 10px 0; }
            .inv-step-num { width: 24px; height: 24px; border-radius: 999px; background: #1d4ed8; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 1000; }
            .inv-step-text { font-size: 12px; line-height: 1.45; color: #334155; font-weight: 700; }
            .inv-step-text b { color: #0f172a; font-weight: 1000; }
            .inv-bullet { display: flex; gap: 8px; align-items: flex-start; font-size: 12.5px; color: #166534; font-weight: 800; line-height: 1.45; margin: 8px 0; }
            .inv-best { margin-top: 12px; display: grid; grid-template-columns: 135px repeat(5, 1fr); gap: 0; border-radius: 16px; overflow: hidden; border: 1px solid rgba(148,163,184,.22); box-shadow: 0 10px 24px rgba(0,0,0,.15); }
            .inv-best-title { background: #0f3b63; color: white; font-size: 18px; font-weight: 1000; display: flex; align-items: center; justify-content: center; text-align: center; padding: 12px; text-transform: uppercase; letter-spacing: .05em; }
            .inv-best-item { background: rgba(255,255,255,.98); color: #0f172a; padding: 12px 13px; border-left: 1px solid rgba(15,23,42,.10); font-size: 11.5px; line-height: 1.45; font-weight: 750; min-height: 76px; }
            .inv-best-icon { display: block; font-size: 22px; margin-bottom: 4px; }
            @media (max-width: 1200px) {
                .inv-layout { grid-template-columns: 1fr; }
                .inv-metric-grid { grid-template-columns: repeat(3, 1fr); }
                .inv-top { grid-template-columns: 1fr; }
                .inv-best { grid-template-columns: 1fr; }
            }


            /* =====================================================
               WIDE DASHBOARD LAYOUT FIX
               Tujuan: mengurangi ruang kosong kiri-kanan dashboard utama
               tanpa mengubah data, KPI, table, chart, dan fitur.
               ===================================================== */

            .main .block-container,
            section.main .block-container,
            div[data-testid="stMainBlockContainer"],
            div[data-testid="stAppViewContainer"] .block-container {
                max-width: 100% !important;
                width: 100% !important;
                padding-left: 1.6rem !important;
                padding-right: 1.6rem !important;
                padding-top: 1.2rem !important;
            }

            /* Bungkus dashboard dibuat full mengikuti area kanan setelah sidebar */
            .bi-wrap {
                width: 100% !important;
                max-width: 100% !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
            }

            /* Semua row/kolom Streamlit di dashboard dipaksa memenuhi ruang */
            div[data-testid="stHorizontalBlock"] {
                width: 100% !important;
            }

            div[data-testid="column"] {
                min-width: 0 !important;
            }

            /* Hero dan card dataset tetap rapi saat melebar */
            .bi-hero,
            .bi-dataset-card {
                width: 100% !important;
                box-sizing: border-box !important;
            }

            /* KPI memanfaatkan ruang lebih luas tanpa mengubah isi */
            .bi-kpi {
                width: 100% !important;
                box-sizing: border-box !important;
            }

            /* Card preview, summary, visual, insight dibuat full di kolomnya */
            .bi-card,
            .bi-card-light,
            div[data-testid="stVerticalBlockBorderWrapper"] {
                width: 100% !important;
                box-sizing: border-box !important;
            }

            /* Tombol menu utama melebar rapi */
            div[data-testid="stButton"] {
                width: 100% !important;
            }

            div[data-testid="stButton"] > button {
                width: 100% !important;
            }

            /* Plot/table mengikuti lebar card */
            div[data-testid="stPlotlyChart"],
            div[data-testid="stDataFrame"] {
                width: 100% !important;
            }

            /* Aturan responsive agar tidak terlalu mepet di layar kecil */
            @media (max-width: 900px) {
                .main .block-container,
                section.main .block-container,
                div[data-testid="stMainBlockContainer"],
                div[data-testid="stAppViewContainer"] .block-container {
                    padding-left: 0.8rem !important;
                    padding-right: 0.8rem !important;
                }
            }


            .bi-wrap {
                margin-top: -6px;
            }

            .bi-hero {
                background:
                    radial-gradient(circle at 8% 0%, rgba(34, 211, 238, .18), transparent 26%),
                    radial-gradient(circle at 100% 0%, rgba(124, 58, 237, .22), transparent 32%),
                    linear-gradient(135deg, rgba(15, 23, 42, .98), rgba(30, 64, 175, .92));
                color: white;
                padding: 18px 22px;
                border-radius: 22px;
                box-shadow: 0 18px 42px rgba(37, 99, 235, 0.18);
                border: 1px solid rgba(34, 211, 238, .20);
                min-height: 122px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .bi-title {
                font-size: 28px;
                font-weight: 950;
                letter-spacing: -.5px;
                line-height: 1.1;
                margin-bottom: 8px;
            }

            .bi-subtitle {
                font-size: 13px;
                line-height: 1.65;
                color: #dbeafe;
                font-weight: 650;
                max-width: 760px;
            }

            .bi-dataset-card {
                background:
                    linear-gradient(135deg, rgba(37, 99, 235, .96), rgba(30, 64, 175, .94));
                border: 1px solid rgba(191, 219, 254, .35);
                border-radius: 22px;
                color: white;
                padding: 18px 16px;
                min-height: 122px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                box-shadow: 0 18px 42px rgba(37, 99, 235, 0.19);
            }

            .bi-mini-label {
                font-size: 11px;
                color: #bfdbfe;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: .06em;
                margin-bottom: 8px;
            }

            .bi-dataset-name {
                font-size: 18px;
                font-weight: 950;
                word-break: break-word;
            }

            .bi-kpi {
                background: rgba(15, 23, 42, .86);
                border: 1px solid rgba(96, 165, 250, .22);
                border-radius: 18px;
                padding: 13px 14px;
                min-height: 96px;
                box-shadow: 0 12px 26px rgba(0,0,0,.16);
                transition: .22s ease;
            }

            .bi-kpi:hover {
                transform: translateY(-4px);
                border-color: rgba(34, 211, 238, .48);
                box-shadow: 0 18px 36px rgba(14, 165, 233, .16);
            }

            .bi-kpi-icon {
                font-size: 21px;
                margin-bottom: 7px;
            }

            .bi-kpi-label {
                font-size: 11px;
                font-weight: 850;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: .06em;
            }

            .bi-kpi-value {
                font-size: 25px;
                font-weight: 950;
                color: #60a5fa;
                margin-top: 4px;
            }

            .bi-section-title {
                font-size: 18px;
                font-weight: 950;
                color: #e5e7eb;
                margin: 18px 0 10px 0;
            }

            .bi-card {
                background: rgba(15, 23, 42, .86);
                border: 1px solid rgba(96, 165, 250, .22);
                border-radius: 20px;
                padding: 15px 16px;
                box-shadow: 0 12px 28px rgba(0,0,0,.17);
                min-height: 120px;
            }

            .bi-card-light {
                background: rgba(255, 255, 255, .98);
                border: 1px solid rgba(37,99,235,.12);
                border-radius: 20px;
                padding: 15px 16px;
                box-shadow: 0 12px 28px rgba(15, 23, 42, .08);
                min-height: 120px;
            }

            .bi-card-title {
                font-size: 14px;
                font-weight: 950;
                color: #67e8f9;
                margin-bottom: 10px;
            }

            .bi-card-light .bi-card-title {
                color: #1d4ed8;
            }

            .bi-insight {
                color: #cbd5e1;
                font-size: 13px;
                line-height: 1.65;
            }

            .bi-card-light .bi-insight {
                color: #334155;
            }

            .bi-good {
                color: #22c55e;
                font-weight: 950;
            }

            .bi-warn {
                color: #f59e0b;
                font-weight: 950;
            }

            .bi-bad {
                color: #ef4444;
                font-weight: 950;
            }

            .bi-note {
                margin-top: 10px;
                padding: 10px 12px;
                border-radius: 14px;
                background: rgba(37, 99, 235, .13);
                color: #bfdbfe;
                border-left: 4px solid #38bdf8;
                font-size: 12.5px;
                line-height: 1.55;
            }

            .bi-card-light .bi-note {
                background: #eff6ff;
                color: #1e3a8a;
                border-left-color: #2563eb;
            }

            .bi-action-title {
                font-size: 13px;
                color: #94a3b8;
                font-weight: 900;
                margin-bottom: 8px;
            }

            div[data-testid="stButton"] > button {
                border-radius: 15px !important;
                min-height: 43px !important;
                font-weight: 850 !important;
                border: 1px solid rgba(34, 211, 238, .28) !important;
                background: linear-gradient(135deg, rgba(8, 145, 178, .22), rgba(88, 28, 135, .20)) !important;
                color: #67e8f9 !important;
                transition: all .22s ease !important;
            }

            div[data-testid="stButton"] > button:hover {
                transform: translateY(-3px);
                box-shadow: 0 0 28px rgba(34, 211, 238, .16) !important;
                border-color: rgba(34, 211, 238, .55) !important;
            }

            .modebar-container,
            .modebar,
            .modebar-group {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
            }

            div[data-testid="stDataFrame"] {
                border-radius: 14px !important;
                overflow: hidden !important;
                border: 1px solid rgba(96, 165, 250, .20) !important;
            }

            @media (prefers-color-scheme: light) {
                .bi-section-title {
                    color: #0f172a;
                }

                .bi-kpi,
                .bi-card {
                    background: rgba(255,255,255,.98);
                    border-color: rgba(37,99,235,.13);
                }

                .bi-insight {
                    color: #334155;
                }

                .bi-kpi-label {
                    color: #64748b;
                }
            }

            /* =====================================================
               FEATURE MENU UNDER KPI FINAL
               Menu utama dikembalikan tepat di bawah KPI Rows/Columns,
               bukan di bagian bawah halaman.
               ===================================================== */

            .inv-feature-menu-box {
                width: 100% !important;
                margin: 0 0 12px 0 !important;
                padding: 12px 14px 13px 14px !important;
                border-radius: 18px !important;
                border: 1px solid rgba(125, 211, 252, .25) !important;
                background:
                    radial-gradient(circle at 2% 0%, rgba(34, 211, 238, .14), transparent 24%),
                    linear-gradient(135deg, rgba(15,23,42,.96), rgba(30,41,59,.94)) !important;
                box-shadow: 0 14px 32px rgba(0,0,0,.18) !important;
                box-sizing: border-box !important;
            }

            .inv-feature-head {
                display: block !important;
                margin-bottom: 10px !important;
            }

            .inv-feature-title {
                color: #67e8f9 !important;
                font-size: 15px !important;
                font-weight: 1000 !important;
                letter-spacing: .06em !important;
                text-transform: uppercase !important;
                line-height: 1.2 !important;
            }

            .inv-feature-sub {
                color: #dbeafe !important;
                font-size: 11.5px !important;
                font-weight: 750 !important;
                line-height: 1.3 !important;
                margin-top: 3px !important;
            }

            .inv-feature-badge {
                color: #86efac !important;
                font-size: 10.5px !important;
                font-weight: 1000 !important;
                letter-spacing: .06em !important;
                text-transform: uppercase !important;
                border: 1px solid rgba(134,239,172,.28) !important;
                background: rgba(22, 163, 74, .12) !important;
                border-radius: 999px !important;
                padding: 6px 10px !important;
                white-space: nowrap !important;
            }

            .inv-feature-menu-box div[data-testid="stHorizontalBlock"] {
                gap: 0.55rem !important;
                margin-bottom: 0.45rem !important;
            }

            .inv-feature-menu-box div[data-testid="stButton"] > button {
                min-height: 54px !important;
                height: 54px !important;
                padding: 8px 9px !important;
                border-radius: 15px !important;
                color: #EAF6FF !important;
                font-size: 12px !important;
                font-weight: 900 !important;
                line-height: 1.18 !important;
                background:
                    linear-gradient(135deg, rgba(8,145,178,.22), rgba(88,28,135,.22)) !important;
                border: 1px solid rgba(34,211,238,.30) !important;
                box-shadow: 0 10px 22px rgba(0,0,0,.12) !important;
            }

            .inv-feature-menu-box div[data-testid="stButton"] > button:hover {
                transform: translateY(-2px) !important;
                border-color: rgba(34,211,238,.62) !important;
                box-shadow: 0 0 24px rgba(34,211,238,.16) !important;
                color: #67e8f9 !important;
            }

            /* Best Practices lama disembunyikan agar menu tidak muncul di bawah halaman */
            .inv-best {
                display: none !important;
            }


            /* FEATURE MENU CLEAN HEADER FINAL */
            .inv-feature-sub,
            .inv-feature-badge {
                display: none !important;
            }

        </style>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# SECTION: KPI
# =====================================================
def render_kpi_row(total_rows, total_cols, numeric_count, categorical_count, total_missing, duplicate_rows):
    kpi_data = [
        ("📄", "Total Rows", f"{total_rows:,}"),
        ("🧱", "Total Columns", f"{total_cols}"),
        ("🔢", "Numerical", f"{numeric_count}"),
        ("🏷️", "Categorical", f"{categorical_count}"),
        ("⚠️", "Missing Cells", f"{total_missing:,}"),
        ("🔁", "Duplicate Rows", f"{duplicate_rows:,}")
    ]

    cols = st.columns(6)
    for col, (icon, label, value) in zip(cols, kpi_data):
        with col:
            st.markdown(
                f"""
                <div class="bi-kpi">
                    <div class="bi-kpi-icon">{icon}</div>
                    <div class="bi-kpi-label">{label}</div>
                    <div class="bi-kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


# =====================================================
# SECTION: DATA PREVIEW & SUMMARY
# =====================================================


def _table_dynamic_height(data, min_height=140, max_height=560, row_height=38):
    """Atur tinggi tabel mengikuti jumlah baris agar tidak ada area kosong terlalu besar."""
    try:
        row_count = len(data)
    except Exception:
        row_count = 6

    # header + baris + sedikit padding
    calculated_height = 46 + (max(row_count, 1) * row_height) + 12

    return int(min(max(calculated_height, min_height), max_height))


def _open_large_table(title, data, height=None):
    """Tampilkan tabel versi besar tanpa mengubah layout utama."""
    table_height = height if height is not None else _table_dynamic_height(
        data,
        min_height=150,
        max_height=560,
        row_height=38
    )

    def _content():
        st.caption("Mode tampilan besar untuk melihat data dengan lebih jelas.")
        st.dataframe(data, use_container_width=True, height=table_height)

    if hasattr(st, "dialog"):
        try:
            dialog_decorator = st.dialog(title, width="large")
        except TypeError:
            dialog_decorator = st.dialog(title)

        @dialog_decorator
        def _dialog():
            _content()

        _dialog()
    else:
        with st.expander(f"⛶ {title} - Tampilan Besar", expanded=True):
            _content()


def _open_large_chart(title, fig, height=620):
    """Tampilkan chart versi besar tanpa modebar yang mengganggu."""
    large_fig = go.Figure(fig)

    current_title = ""
    try:
        current_title = large_fig.layout.title.text
    except Exception:
        current_title = ""

    if current_title is None or str(current_title).strip().lower() in ["", "none", "undefined"]:
        large_fig.update_layout(
            title=dict(
                text=" ",
                font=dict(size=1, color="rgba(0,0,0,0)")
            )
        )

    large_fig.update_layout(
        height=height,
        margin=dict(l=25, r=25, t=35, b=55)
    )

    def _content():
        st.caption("Mode tampilan besar untuk melihat visualisasi dengan lebih jelas.")
        st.plotly_chart(large_fig, use_container_width=True, config=PLOT_CONFIG)

    if hasattr(st, "dialog"):
        try:
            dialog_decorator = st.dialog(title, width="large")
        except TypeError:
            dialog_decorator = st.dialog(title)

        @dialog_decorator
        def _dialog():
            _content()

        _dialog()
    else:
        with st.expander(f"⛶ {title} - Tampilan Besar", expanded=True):
            _content()


def _card_header_with_expand(title, key, kind, payload=None):
    """Header card dengan tombol perbesar di kanan atas, tapi ukurannya dibuat proporsional."""
    h1, h2 = st.columns([0.91, 0.09], vertical_alignment="center")

    with h1:
        st.markdown(f'<div class="bi-card-title">{title}</div>', unsafe_allow_html=True)

    with h2:
        expand_clicked = st.button(
            "⛶",
            key=key,
            help="Perbesar tampilan",
            use_container_width=True
        )

    if expand_clicked and payload is not None:
        if kind == "table":
            _open_large_table(title, payload)
        elif kind == "chart":
            _open_large_chart(title, payload)


def render_data_summary_preview(df, num_stats, cat_stats):
    st.markdown('<div class="bi-section-title">🧾 Dataset Preview & Summary</div>', unsafe_allow_html=True)

    p1, p2, p3 = st.columns([1.25, 1, 1])

    raw_preview = df.head(6)
    num_preview = _clean_stats_preview(num_stats, 6, 6)
    cat_preview = _clean_stats_preview(cat_stats, 6, 6)

    with p1:
        with _safe_card_container(border=True):
            _card_header_with_expand(
                "Raw Preview",
                "expand_raw_preview",
                "table",
                df
            )
            st.dataframe(raw_preview, use_container_width=True, height=_table_dynamic_height(raw_preview, min_height=180, max_height=235, row_height=32))

    with p2:
        with _safe_card_container(border=True):
            _card_header_with_expand(
                "Numerical Summary",
                "expand_numerical_summary",
                "table",
                num_stats
            )
            st.dataframe(num_preview, use_container_width=True, height=_table_dynamic_height(num_preview, min_height=180, max_height=235, row_height=32))

    with p3:
        with _safe_card_container(border=True):
            _card_header_with_expand(
                "Categorical Summary",
                "expand_categorical_summary",
                "table",
                cat_stats
            )
            st.dataframe(cat_preview, use_container_width=True, height=_table_dynamic_height(cat_preview, min_height=180, max_height=235, row_height=32))


# =====================================================
# SECTION: VISUAL OVERVIEW
# =====================================================
# =====================================================
# SECTION: VISUAL OVERVIEW
# =====================================================
def render_dashboard_visual_overview(df, numeric_cols, categorical_cols, date_cols=None):
    st.markdown('<div class="bi-section-title">📈 Visualization Preview</div>', unsafe_allow_html=True)

    numeric_cols = [c for c in numeric_cols if c in df.columns]
    categorical_cols = [c for c in categorical_cols if c in df.columns]
    date_cols = [c for c in (date_cols or []) if c in df.columns]

    selected_num = _first_numeric(df, numeric_cols)
    selected_cat = _first_categorical(df, categorical_cols)

    v1, v2, v3 = st.columns(3)

    with v1:
        with _safe_card_container(border=True):
            num_count = len(numeric_cols)
            cat_count = len(categorical_cols)
            date_count = len(date_cols)
            other_count = max(0, df.shape[1] - num_count - cat_count - date_count)

            type_df = pd.DataFrame({
                "Type": ["Numeric", "Categorical", "Date", "Other"],
                "Count": [num_count, cat_count, date_count, other_count]
            })
            type_df = type_df[type_df["Count"] > 0]

            if not type_df.empty:
                fig_type = px.pie(type_df, names="Type", values="Count", hole=0.55)
                fig_type = _style_plot(fig_type, height=245)
                _card_header_with_expand(
                    "🧩 Data Type Composition",
                    "expand_chart_type",
                    "chart",
                    fig_type
                )
                st.plotly_chart(fig_type, use_container_width=True, config=PLOT_CONFIG)
            else:
                st.markdown('<div class="bi-card-title">🧩 Data Type Composition</div>', unsafe_allow_html=True)
                st.info("Tipe data belum tersedia.")

    with v2:
        with _safe_card_container(border=True):
            missing_data = df.isna().sum()
            missing_data = missing_data[missing_data > 0].sort_values(ascending=False).head(10)

            if len(missing_data) > 0:
                fig_missing = px.bar(
                    x=missing_data.index.astype(str),
                    y=missing_data.values,
                    labels={"x": "Column", "y": "Missing"}
                )
                fig_missing = _style_plot(fig_missing, height=245)
                _card_header_with_expand(
                    "⚠️ Missing Value Overview",
                    "expand_chart_missing",
                    "chart",
                    fig_missing
                )
                st.plotly_chart(fig_missing, use_container_width=True, config=PLOT_CONFIG)
            else:
                st.markdown('<div class="bi-card-title">⚠️ Missing Value Overview</div>', unsafe_allow_html=True)
                st.success("Tidak ada missing value pada dataset ini.")

    with v3:
        with _safe_card_container(border=True):
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr(numeric_only=True)
                fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto")
                fig_corr = _style_plot(fig_corr, height=245)
                _card_header_with_expand(
                    "🔗 Correlation Heatmap",
                    "expand_chart_corr",
                    "chart",
                    fig_corr
                )
                st.plotly_chart(fig_corr, use_container_width=True, config=PLOT_CONFIG)
            else:
                st.markdown('<div class="bi-card-title">🔗 Correlation Heatmap</div>', unsafe_allow_html=True)
                st.info("Correlation membutuhkan minimal 2 variabel numerik.")

    v4, v5, v6 = st.columns(3)

    with v4:
        with _safe_card_container(border=True):
            if selected_num:
                fig_hist = px.histogram(df, x=selected_num, nbins=25)
                fig_hist = _style_plot(fig_hist, height=255, title=f"Distribution of {selected_num}")
                _card_header_with_expand(
                    "📊 Numerical Distribution",
                    "expand_chart_hist",
                    "chart",
                    fig_hist
                )
                st.plotly_chart(fig_hist, use_container_width=True, config=PLOT_CONFIG)
            else:
                st.markdown('<div class="bi-card-title">📊 Numerical Distribution</div>', unsafe_allow_html=True)
                st.info("Tidak ada variabel numerik.")

    with v5:
        with _safe_card_container(border=True):
            if selected_cat:
                cat_count = df[selected_cat].astype(str).value_counts().head(8)
                fig_cat = px.bar(
                    x=cat_count.index.astype(str),
                    y=cat_count.values,
                    labels={"x": selected_cat, "y": "Count"}
                )
                fig_cat = _style_plot(fig_cat, height=255, title=f"Top Categories of {selected_cat}")
                _card_header_with_expand(
                    "🏷️ Categorical Overview",
                    "expand_chart_cat",
                    "chart",
                    fig_cat
                )
                st.plotly_chart(fig_cat, use_container_width=True, config=PLOT_CONFIG)
            else:
                st.markdown('<div class="bi-card-title">🏷️ Categorical Overview</div>', unsafe_allow_html=True)
                st.info("Tidak ada variabel kategorikal.")

    with v6:
        with _safe_card_container(border=True):
            if selected_cat and selected_num:
                sample_df = df[[selected_cat, selected_num]].dropna()
                if not sample_df.empty:
                    top_categories = sample_df[selected_cat].astype(str).value_counts().head(6).index
                    sample_df = sample_df[sample_df[selected_cat].astype(str).isin(top_categories)]
                    fig_mix = px.box(
                        sample_df,
                        x=selected_cat,
                        y=selected_num,
                        points=False
                    )
                    fig_mix = _style_plot(fig_mix, height=255, title=f"{selected_num} by {selected_cat}")
                    _card_header_with_expand(
                        "📌 Cat vs Numerical / Time Series",
                        "expand_chart_mix",
                        "chart",
                        fig_mix
                    )
                    st.plotly_chart(fig_mix, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.markdown('<div class="bi-card-title">📌 Cat vs Numerical / Time Series</div>', unsafe_allow_html=True)
                    st.info("Data cat vs num tidak tersedia.")
            elif date_cols and selected_num:
                date_col = _first_date(df, date_cols)
                if date_col:
                    ts_df = df[[date_col, selected_num]].dropna().sort_values(date_col)
                    fig_ts = px.line(ts_df.head(200), x=date_col, y=selected_num)
                    fig_ts = _style_plot(fig_ts, height=255, title=f"Trend of {selected_num}")
                    _card_header_with_expand(
                        "📌 Cat vs Numerical / Time Series",
                        "expand_chart_mix",
                        "chart",
                        fig_ts
                    )
                    st.plotly_chart(fig_ts, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.markdown('<div class="bi-card-title">📌 Cat vs Numerical / Time Series</div>', unsafe_allow_html=True)
                    st.info("Time series membutuhkan kolom tanggal.")
            else:
                st.markdown('<div class="bi-card-title">📌 Cat vs Numerical / Time Series</div>', unsafe_allow_html=True)
                st.info("Membutuhkan variabel kategorikal + numerik atau tanggal + numerik.")


# =====================================================
# SECTION: MENU & ACTIONS
# =====================================================
# =====================================================
# SECTION: MENU & ACTIONS
# =====================================================
def render_main_feature_menu():
    st.markdown('<div class="bi-section-title">🚀 Main Feature Menu</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        if st.button("📁 Data Management", use_container_width=True, key="dash_data_management"):
            dashboard_go_to("Upload Data")

    with m2:
        if st.button("📊 Descriptive Stats", use_container_width=True, key="dash_descriptive"):
            dashboard_go_to("Numerical Variables")

    with m3:
        if st.button("📈 Visualization", use_container_width=True, key="dash_visualization"):
            dashboard_go_to("Numerical Visualization")

    with m4:
        if st.button("🧠 Insight Generator", use_container_width=True, key="dash_insight"):
            dashboard_go_to("Intelligent Insight Generator")

    with m5:
        if st.button("📄 Reporting System", use_container_width=True, key="dash_reporting"):
            dashboard_go_to("Download Report PDF")

    n1, n2, n3, n4, n5 = st.columns(5)

    with n1:
        if st.button("📌 Dataset Info", use_container_width=True, key="dash_dataset_info"):
            dashboard_go_to("Dataset Information")

    with n2:
        if st.button("🧹 Data Cleaning", use_container_width=True, key="dash_cleaning"):
            dashboard_go_to("Data Cleaning")

    with n3:
        if st.button("🔗 Bivariate", use_container_width=True, key="dash_bivariate"):
            dashboard_go_to("Bivariate & Multivariate Analysis")

    with n4:
        if st.button("📌 Cat vs Num", use_container_width=True, key="dash_cat_num"):
            dashboard_go_to("Categorical vs Numerical Analysis")

    with n5:
        if st.button("⏱️ Time Series", use_container_width=True, key="dash_time_series"):
            dashboard_go_to("Time Series Analytics")



def render_inventory_feature_menu():
    st.markdown(
        """
        <div class="inv-feature-menu-box">
            <div class="inv-feature-head">
                <div>
                    <div class="inv-feature-title">🚀 Feature Menu</div>
                </div>
            </div>
        """,
        unsafe_allow_html=True
    )

    f1, f2, f3, f4, f5 = st.columns(5, gap="small")

    with f1:
        if st.button("📁 Upload Data", use_container_width=True, key="inv_menu_upload_data"):
            dashboard_go_to("Upload Data")

    with f2:
        if st.button("📌 Dataset Info", use_container_width=True, key="inv_menu_dataset_info"):
            dashboard_go_to("Dataset Information")

    with f3:
        if st.button("🧹 Data Cleaning", use_container_width=True, key="inv_menu_data_cleaning"):
            dashboard_go_to("Data Cleaning")

    with f4:
        if st.button("📊 Statistics", use_container_width=True, key="inv_menu_statistics"):
            dashboard_go_to("Numerical Variables")

    with f5:
        if st.button("📈 Visualization", use_container_width=True, key="inv_menu_visualization"):
            dashboard_go_to("Numerical Visualization")

    g1, g2, g3, g4, g5 = st.columns(5, gap="small")

    with g1:
        if st.button("🔗 Bivariate", use_container_width=True, key="inv_menu_bivariate"):
            dashboard_go_to("Bivariate & Multivariate Analysis")

    with g2:
        if st.button("📌 Cat vs Num", use_container_width=True, key="inv_menu_cat_num"):
            dashboard_go_to("Categorical vs Numerical Analysis")

    with g3:
        if st.button("⏱️ Time Series", use_container_width=True, key="inv_menu_time_series"):
            dashboard_go_to("Time Series Analytics")

    with g4:
        if st.button("🧠 Insight", use_container_width=True, key="inv_menu_insight"):
            dashboard_go_to("Intelligent Insight Generator")

    with g5:
        if st.button("📄 Reporting", use_container_width=True, key="inv_menu_reporting"):
            dashboard_go_to("Download Report PDF")

    st.markdown("</div>", unsafe_allow_html=True)

def render_quick_actions():
    st.markdown('<div class="bi-action-title">Quick Actions</div>', unsafe_allow_html=True)

    q1, q2 = st.columns(2)

    with q1:
        if st.button("📄 Generate Report", use_container_width=True, key="quick_report"):
            dashboard_go_to("Download Report PDF")

    with q2:
        if st.button("📈 Open Visualization", use_container_width=True, key="quick_visual"):
            dashboard_go_to("Numerical Visualization")

    q3, q4 = st.columns(2)

    with q3:
        if st.button("🧠 Open Insight", use_container_width=True, key="quick_insight"):
            dashboard_go_to("Intelligent Insight Generator")

    with q4:
        if st.button("📊 Export Result", use_container_width=True, key="quick_export"):
            dashboard_go_to("Export Result to Excel/CSV")




# =====================================================
# INVENTORY-STYLE DASHBOARD HELPERS
# =====================================================
def _top_missing_columns(df, limit=5):
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False).head(limit)
    if missing.empty:
        return pd.DataFrame({"Column": ["No Missing"], "Missing": [0]})
    return pd.DataFrame({"Column": missing.index.astype(str), "Missing": missing.values})


def _main_numeric_distribution(df, numeric_cols):
    selected_num = _first_numeric(df, numeric_cols)
    if selected_num:
        fig = px.histogram(df, x=selected_num, nbins=25)
        return _style_plot(fig, height=265, title=f"Distribution of {selected_num}", color_index=0)
    return None


def _main_categorical_bar(df, categorical_cols):
    selected_cat = _first_categorical(df, categorical_cols)
    if selected_cat:
        cat_count = df[selected_cat].astype(str).value_counts().head(7)
        fig = px.bar(x=cat_count.index.astype(str), y=cat_count.values, labels={"x": selected_cat, "y": "Count"})
        return _style_plot(fig, height=265, title=f"Top Categories of {selected_cat}", color_index=1)
    return None


def _data_type_donut(df, numeric_cols, categorical_cols, date_cols):
    num_count = len([c for c in numeric_cols if c in df.columns])
    cat_count = len([c for c in categorical_cols if c in df.columns])
    date_count = len([c for c in (date_cols or []) if c in df.columns])
    other_count = max(0, df.shape[1] - num_count - cat_count - date_count)
    type_df = pd.DataFrame({"Type": ["Numeric", "Categorical", "Date", "Other"], "Count": [num_count, cat_count, date_count, other_count]})
    type_df = type_df[type_df["Count"] > 0]
    if type_df.empty:
        return None
    fig = px.pie(type_df, names="Type", values="Count", hole=0.55)
    return _style_plot(fig, height=265, title="Data Type Composition", color_index=0)


def _missing_overview_chart(df):
    missing_df = _top_missing_columns(df, limit=6)

    # Dibuat horizontal agar ruang chart lebih penuh dan sejajar dengan visual lain.
    fig = px.bar(
        missing_df,
        x="Missing",
        y="Column",
        orientation="h",
        labels={"Column": "Column", "Missing": "Missing"}
    )

    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)

    fig = _style_plot(fig, height=265, title="Missing Value Overview", color_index=1)
    fig.update_layout(
        margin=dict(l=82, r=26, t=48, b=38),
        showlegend=False
    )

    return fig


def _correlation_preview(df, numeric_cols):
    valid_numeric_cols = [c for c in numeric_cols if c in df.columns]
    if len(valid_numeric_cols) < 2:
        return None
    corr = df[valid_numeric_cols].corr(numeric_only=True)
    fig = px.imshow(corr, text_auto=".2f", aspect="auto")
    return _style_plot(fig, height=265, title="Correlation Heatmap", color_index=2)


def _inventory_metric_card(icon, title, value, subtext, status="neutral"):
    return (
        f'<div class="inv-metric inv-{status}">'
        f'<div class="inv-metric-icon">{icon}</div>'
        f'<div class="inv-metric-body">'
        f'<div class="inv-metric-title">{title}</div>'
        f'<div class="inv-metric-value">{value}</div>'
        f'<div class="inv-metric-sub">{subtext}</div>'
        f'</div>'
        f'</div>'
    )


def _inventory_bullet(text):
    return f'<div class="inv-bullet">✓ <span>{text}</span></div>'

# =====================================================
# MAIN DASHBOARD PAGE
# =====================================================
def show_dashboard_page(
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
    total_rows = df.shape[0]
    total_cols = df.shape[1]
    total_missing = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    health_score = calculate_health_score(df)
    health_label = get_health_label(health_score)

    numeric_count = len(numeric_cols)
    categorical_count = len(categorical_cols)
    date_count = len(date_cols)

    if total_missing == 0 and duplicate_rows == 0:
        quality_message = "Dataset clean dan siap dianalisis."
    elif health_score >= 75:
        quality_message = "Dataset cukup baik, perlu pengecekan ringan."
    else:
        quality_message = "Dataset perlu data cleaning sebelum analisis lanjut."

    if numeric_count > categorical_count:
        dominant_type = "variabel numerik paling dominan"
    elif categorical_count > numeric_count:
        dominant_type = "variabel kategorikal paling dominan"
    else:
        dominant_type = "komposisi numerik dan kategorikal cukup seimbang"

    inject_bi_dashboard_css()

    fig_type = _data_type_donut(df, numeric_cols, categorical_cols, date_cols)
    fig_missing = _missing_overview_chart(df)
    fig_corr = _correlation_preview(df, numeric_cols)
    fig_hist = _main_numeric_distribution(df, numeric_cols)
    fig_cat = _main_categorical_bar(df, categorical_cols)

    raw_preview = df.head(7)
    alert_df = pd.DataFrame({
        "Indicator": ["Missing Cells", "Duplicate Rows", "Health Score", "Numeric Columns", "Categorical Columns"],
        "Value": [total_missing, duplicate_rows, f"{health_score}/100", numeric_count, categorical_count],
        "Status": [
            "Check" if total_missing else "Good",
            "Check" if duplicate_rows else "Good",
            health_label,
            "Available" if numeric_count else "None",
            "Available" if categorical_count else "None"
        ]
    })

    st.markdown(
        f"""
        <div class="inv-top">
            <div class="inv-title-card">
                <div class="inv-title">EDA DASHBOARD</div>
                <div class="inv-desc">
                    Dashboard analitik otomatis untuk membaca dataset, melihat statistik deskriptif,
                    memantau kualitas data, menampilkan visualisasi, dan menghasilkan insight awal.
                </div>
            </div>
            <div class="inv-benefit-card">
                <div class="inv-benefit-title">Benefits</div>
                <div class="inv-benefit-item"><span>✓</span><div>Memantau kualitas dataset secara real time</div></div>
                <div class="inv-benefit-item"><span>✓</span><div>Mengidentifikasi missing value dan duplicate rows</div></div>
                <div class="inv-benefit-item"><span>✓</span><div>Membantu analisis numerik, kategorikal, korelasi, dan insight</div></div>
                <div class="inv-benefit-item"><span>✓</span><div>Mempercepat proses eksplorasi data sebelum modeling/reporting</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    kpi_html = (
        '<div class="inv-metric-grid">'
        + _inventory_metric_card("📄", "Total Rows", f"{total_rows:,}", "jumlah baris dataset", "blue")
        + _inventory_metric_card("🧱", "Total Columns", f"{total_cols}", "jumlah kolom dataset", "purple")
        + _inventory_metric_card("🔢", "Numerical", f"{numeric_count}", "variabel numerik", "blue")
        + _inventory_metric_card("🏷️", "Categorical", f"{categorical_count}", "variabel kategorikal", "purple")
        + _inventory_metric_card("⚠️", "Missing Cells", f"{total_missing:,}", "sel kosong terdeteksi", "warn" if total_missing else "good")
        + _inventory_metric_card("🔁", "Duplicate Rows", f"{duplicate_rows:,}", "baris duplikat", "warn" if duplicate_rows else "good")
        + '</div>'
    )
    st.markdown(kpi_html, unsafe_allow_html=True)

    render_inventory_feature_menu()

    main_area, side_area = st.columns([4.35, 1.05], gap="small")

    with main_area:
        v1, v2, v3 = st.columns(3, gap="small")

        with v1:
            with _safe_card_container(border=True):
                _card_header_with_expand("Inventory / Data Type Value", "inv_expand_type", "chart", fig_type)
                if fig_type:
                    st.plotly_chart(fig_type, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.info("Tipe data belum tersedia.")

        with v2:
            with _safe_card_container(border=True):
                _card_header_with_expand("Stock Status / Missing Overview", "inv_expand_missing", "chart", fig_missing)
                st.plotly_chart(fig_missing, use_container_width=True, config=PLOT_CONFIG)

        with v3:
            with _safe_card_container(border=True):
                _card_header_with_expand("Inventory Value Trend / Correlation", "inv_expand_corr", "chart", fig_corr)
                if fig_corr:
                    st.plotly_chart(fig_corr, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.info("Correlation membutuhkan minimal 2 variabel numerik.")

        t1, t2 = st.columns([1.55, .95], gap="small")

        with t1:
            with _safe_card_container(border=True):
                _card_header_with_expand("Top Dataset Preview", "inv_expand_raw_table", "table", df)
                st.markdown('<div class="inv-preview-table-align">', unsafe_allow_html=True)
                st.dataframe(
                    raw_preview,
                    use_container_width=True,
                    height=_table_dynamic_height(raw_preview, min_height=235, max_height=275, row_height=30)
                )
                st.markdown('', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="inv-mini-summary">
                        <div class="inv-mini-summary-title">🧾 Dataset Summary</div>
                        <div class="inv-mini-row"><span>File Type</span><span class="inv-mini-value">{file_ext.upper()}</span></div>
                        <div class="inv-mini-row"><span>Dataset Size</span><span class="inv-mini-value">{_safe_file_size(file_size)}</span></div>
                        <div class="inv-mini-row"><span>Active Columns</span><span class="inv-mini-value">{total_cols}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with t2:
            with _safe_card_container(border=True):
                _card_header_with_expand("Low Quality Alert", "inv_expand_alert", "table", alert_df)

                st.markdown('<div class="inv-lowquality-table">', unsafe_allow_html=True)
                st.dataframe(
                    alert_df,
                    use_container_width=True,
                    height=_table_dynamic_height(alert_df, min_height=220, max_height=240, row_height=32)
                )
                st.markdown('', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="inv-quality-summary">
                        <div class="inv-quality-title">📌 Data Quality Summary</div>
                        <div class="inv-quality-row"><span>Health Status</span><span class="inv-quality-value">{health_label}</span></div>
                        <div class="inv-quality-row"><span>Missing Check</span><span class="inv-quality-value">{"Perlu dicek" if total_missing else "Aman"}</span></div>
                        <div class="inv-quality-row"><span>Duplicate Check</span><span class="inv-quality-value">{"Perlu dicek" if duplicate_rows else "Aman"}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        b1, b2 = st.columns(2, gap="small")

        with b1:
            with _safe_card_container(border=True):
                _card_header_with_expand("Numerical Distribution", "inv_expand_hist", "chart", fig_hist)
                if fig_hist:
                    st.plotly_chart(fig_hist, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.info("Tidak ada variabel numerik.")

        with b2:
            with _safe_card_container(border=True):
                _card_header_with_expand("Categorical Ranking", "inv_expand_cat", "chart", fig_cat)
                if fig_cat:
                    st.plotly_chart(fig_cat, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.info("Tidak ada variabel kategorikal.")

    with side_area:
        st.markdown(
            f"""
            <div class="inv-panel">
                <div class="inv-panel-title">⚙️ How It Works</div>
                <div class="inv-step"><div class="inv-step-num">1</div><div class="inv-step-text"><b>Data Input</b><br>Upload CSV, XLSX, atau TXT melalui menu Data Management.</div></div>
                <div class="inv-step"><div class="inv-step-num">2</div><div class="inv-step-text"><b>Dashboard Updates</b><br>Ringkasan baris, kolom, missing, duplicate, dan tipe data otomatis diperbarui.</div></div>
                <div class="inv-step"><div class="inv-step-num">3</div><div class="inv-step-text"><b>Key Metrics</b><br>Lihat KPI, statistik, visualisasi, dan alert kualitas data.</div></div>
                <div class="inv-step"><div class="inv-step-num">4</div><div class="inv-step-text"><b>Analyze & Act</b><br>Lanjutkan ke visualization, insight generator, atau reporting.</div></div>
            </div>
            <div class="inv-panel">
                <div class="inv-panel-title">🔍 Key Insights</div>
                {_inventory_bullet(f"Dataset aktif: {_truncate_text(file_name, 28)}")}
                {_inventory_bullet(f"{dominant_type}.")}
                {_inventory_bullet(f"Health score dataset adalah {health_score}/100.")}
                {_inventory_bullet(quality_message)}
            </div>
            """,
            unsafe_allow_html=True
        )

        with _safe_card_container(border=True):
            st.markdown('<div class="inv-quick-compact">', unsafe_allow_html=True)
            render_quick_actions()
            st.markdown('', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="inv-side-status">
                <div class="inv-side-status-title">⭐ Dashboard Status</div>
                <div class="inv-side-status-item"><span>✓</span><div>Dataset siap dianalisis.</div></div>
                <div class="inv-side-status-item"><span>✓</span><div>Visualisasi dan reporting tersedia.</div></div>
                <div class="inv-side-status-item"><span>✓</span><div>Health score: {health_score}/100.</div></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="inv-right-fill">
                <div class="inv-right-fill-title">🧭 Next Analysis</div>
                <div class="inv-right-fill-item"><span>✓</span><div>Cek missing dan duplicate melalui menu Data Cleaning.</div></div>
                <div class="inv-right-fill-item"><span>✓</span><div>Lanjutkan korelasi dan cat vs num untuk insight lanjutan.</div></div>
                <div class="inv-right-fill-item"><span>✓</span><div>Generate report setelah visualisasi final.</div></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Best Practices lama dihapus karena menu utama sudah dipindahkan ke bawah KPI.
