import os
import re
import time
from urllib.parse import quote
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from backend.data_loader import load_data, detect_columns
from backend.preprocessing import dataset_information, cleaning_summary, remove_duplicates
from backend.descriptive_stats import numerical_statistics
from backend.categorical_analysis import categorical_statistics
import backend.visualization as viz
import backend.time_series as ts
from backend.insight_generator import generate_insights
from backend.export_report import export_excel, export_csv, export_pdf, export_html
from backend.theme import apply_manual_theme_css, apply_plotly_manual_theme, get_aggrid_custom_css
from backend.table_utils import show_table
from frontend.pages.auth import show_landing_page, show_login_page
from frontend.pages.empty import show_empty_dashboard_page
from frontend.pages.upload import show_upload_page
from frontend.pages.dashboard import show_dashboard_page
from frontend.pages.data_management import (
    show_file_information_page,
    show_data_preview_page,
    show_dataset_information_page,
)
from frontend.pages.cleaning import show_data_cleaning_page
from frontend.pages.statistics_pages import (
    show_numerical_variables_page,
    show_categorical_variables_page,
)
from frontend.pages.visualization_pages import (
    show_numerical_visualization_page,
    show_categorical_visualization_page,
    show_bivariate_multivariate_page,
    show_categorical_vs_numerical_page,
    show_time_series_page,
)
from frontend.pages.insight_page import show_insight_generator_page
from frontend.pages.reporting import (
    show_download_pdf_page,
    show_download_html_page,
    show_export_excel_csv_page,
)

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

st.set_page_config(
    page_title="Auto EDA Analytics",
    page_icon="📊",
    layout="wide"
)


def load_css():
    try:
        with open("frontend/static/css/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass



def load_js():
    try:
        with open("frontend/static/js/script.js", "r", encoding="utf-8") as f:
            js_code = f.read()
        components.html(f"<script>{js_code}</script>", height=0)
    except FileNotFoundError:
        pass


load_css()
load_js()


# =========================
# CLEAN MANUAL THEME
# =========================
def apply_clean_manual_theme():
    """
    Theme yang bersih dan tidak saling tabrak.
    - Dark mode: background gelap, teks terang.
    - Light mode: background terang, teks gelap.
    - Tidak memaksa semua style secara berlebihan.
    """
    is_dark = bool(st.session_state.get("manual_dark_mode", False))

    if is_dark:
        st.markdown(
            """
            <style>
                :root { color-scheme: dark; }

                .stApp,
                .main,
                [data-testid="stAppViewContainer"],
                [data-testid="stMain"],
                [data-testid="stMainBlockContainer"],
                .block-container {
                    background:
                        radial-gradient(circle at 8% 0%, rgba(56,189,248,.10), transparent 30%),
                        radial-gradient(circle at 92% 8%, rgba(167,139,250,.11), transparent 32%),
                        linear-gradient(135deg, #020617 0%, #0f172a 58%, #111827 100%) !important;
                    color: #f8fafc !important;
                }

                .stApp,
                .stApp p,
                .stApp span,
                .stApp label,
                .stApp li,
                .stMarkdown,
                .stMarkdown *,
                [data-testid="stMarkdownContainer"],
                [data-testid="stMarkdownContainer"] * {
                    color: #e2e8f0 !important;
                }

                .stApp h1,
                .stApp h2,
                .stApp h3,
                .stApp h4,
                .stApp h5,
                .stApp h6,
                .stApp strong,
                .stApp b {
                    color: #ffffff !important;
                }

                .section-title,
                .section-title *,
                .stButton > button,
                .stButton > button *,
                div[data-testid="stButton"] > button,
                div[data-testid="stButton"] > button * {
                    color: #ffffff !important;
                }

                [data-testid="stSidebar"],
                [data-testid="stSidebar"] > div {
                    background: linear-gradient(180deg, #020617, #0f172a) !important;
                    color: #e2e8f0 !important;
                }

                [data-testid="stSidebar"] *,
                [data-testid="stSidebar"] label,
                [data-testid="stSidebar"] span,
                [data-testid="stSidebar"] p {
                    color: #e2e8f0 !important;
                }

                input,
                textarea,
                select,
                [data-baseweb="select"] > div,
                [data-baseweb="input"] > div {
                    background: rgba(15,23,42,.92) !important;
                    color: #f8fafc !important;
                    border-color: rgba(96,165,250,.35) !important;
                }

                [data-baseweb="select"] *,
                [data-baseweb="popover"] *,
                [role="listbox"] *,
                [role="option"] * {
                    color: #f8fafc !important;
                }

                [data-baseweb="popover"],
                [role="listbox"] {
                    background: #0f172a !important;
                }

                .ag-theme-streamlit,
                .ag-root-wrapper,
                .ag-root,
                .ag-body,
                .ag-row,
                .ag-row-even,
                .ag-row-odd,
                [data-testid="stDataFrame"],
                [data-testid="stTable"],
                table {
                    background: #0f172a !important;
                    color: #f8fafc !important;
                    border-color: rgba(96,165,250,.25) !important;
                }

                .ag-header,
                .ag-header-row,
                .ag-header-cell,
                .ag-paging-panel,
                th {
                    background: #1e293b !important;
                    color: #f8fafc !important;
                }

                .ag-cell,
                .ag-cell-value,
                .ag-header-cell-text,
                .ag-paging-panel *,
                .ag-icon,
                table * {
                    color: #f8fafc !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
                :root { color-scheme: light; }

                .stApp,
                .main,
                [data-testid="stAppViewContainer"],
                [data-testid="stMain"],
                [data-testid="stMainBlockContainer"],
                .block-container {
                    color: #0f172a !important;
                }

                .stApp p,
                .stApp span,
                .stApp label,
                .stApp li,
                .stMarkdown,
                .stMarkdown *,
                [data-testid="stMarkdownContainer"],
                [data-testid="stMarkdownContainer"] * {
                    color: #334155 !important;
                }

                .stApp h1,
                .stApp h2,
                .stApp h3,
                .stApp h4,
                .stApp h5,
                .stApp h6,
                .stApp strong,
                .stApp b {
                    color: #0f172a !important;
                }

                .section-title,
                .section-title *,
                .stButton > button,
                .stButton > button *,
                div[data-testid="stButton"] > button,
                div[data-testid="stButton"] > button * {
                    color: #ffffff !important;
                }

                [data-testid="stSidebar"] *,
                [data-testid="stSidebar"] label,
                [data-testid="stSidebar"] span,
                [data-testid="stSidebar"] p {
                    color: #0f172a !important;
                }

                input,
                textarea,
                select,
                [data-baseweb="select"] *,
                [data-baseweb="input"] * {
                    color: #0f172a !important;
                }

                .ag-cell,
                .ag-cell-value,
                .ag-header-cell-text,
                .ag-paging-panel *,
                .ag-icon,
                table * {
                    color: #0f172a !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )



def safe_name(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9_]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")

def get_output_base_name():
    if st.session_state.file_name:
        base_name = os.path.splitext(st.session_state.file_name)[0]
        return safe_name(base_name)

    return "dataset"


def calculate_health_score(df):
    if df is None or df.empty:
        return 0

    total_cells = max(1, df.shape[0] * df.shape[1])
    missing_pct = (df.isna().sum().sum() / total_cells) * 100
    duplicate_pct = (df.duplicated().sum() / max(1, len(df))) * 100

    score = 100
    score -= missing_pct
    score -= duplicate_pct

    return max(0, min(100, round(score)))


def get_health_label(score):
    if score >= 90:
        return "🟢 Excellent"
    elif score >= 75:
        return "🟡 Good"
    elif score >= 60:
        return "🟠 Fair"
    return "🔴 Needs Cleaning"


def render_summary_interpretation(title, summary_text, caption=None):
    """
    Menampilkan ringkasan interpretasi sebagai card yang sama dengan interpretasi grafik.
    summary_text boleh berupa bullet plain text dari fungsi summary_*.
    """
    if caption:
        st.caption(caption)

    items = []
    for line in str(summary_text).splitlines():
        clean_line = line.strip()
        if not clean_line:
            continue

        if clean_line.startswith("•"):
            clean_line = clean_line[1:].strip()

        items.append(clean_line)

    if not items:
        items = ["Ringkasan interpretasi belum tersedia."]

    st.markdown(f"### 📝 {title}")
    st.markdown(
        interpretation_box(items),
        unsafe_allow_html=True
    )



def logout():
    st.session_state.is_logged_in = False
    st.session_state.auth_page = "landing"
    st.session_state.logged_user = None
    st.session_state.page = "Dashboard"

def save_visualizations(figures, folder):
    os.makedirs(folder, exist_ok=True)

    saved_files = []

    for chart_name, fig in figures.items():
        file_name = safe_name(chart_name)

        html_path = os.path.join(folder, f"{file_name}.html")
        png_path = os.path.join(folder, f"{file_name}.png")

        fig.write_html(html_path)

        try:
            fig.write_image(png_path)
            saved_files.append(png_path)
        except Exception:
            st.toast(
                "⚠️ PNG gagal disimpan. Pastikan package kaleido sudah terinstall.",
                icon="⚠️"
            )

        saved_files.append(html_path)

    return saved_files



if "df" not in st.session_state:
    st.session_state.df = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "file_ext" not in st.session_state:
    st.session_state.file_ext = None

if "file_size" not in st.session_state:
    st.session_state.file_size = None

if "saved_file_path" not in st.session_state:
    st.session_state.saved_file_path = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "landing"

if "logged_user" not in st.session_state:
    st.session_state.logged_user = None

def go_to(page_name):
    st.session_state.page = page_name


PAGE_GROUP = {
    "Dashboard": "Dashboard",

    "Upload Data": "Data Management",
    "File Information": "Data Management",
    "Data Preview": "Data Management",
    "Dataset Information": "Data Management",
    "Data Cleaning": "Data Management",

    "Numerical Variables": "Descriptive Statistics",
    "Categorical Variables": "Descriptive Statistics",

    "Numerical Visualization": "Visualization Analytics",
    "Categorical Visualization": "Visualization Analytics",
    "Bivariate & Multivariate Analysis": "Visualization Analytics",
    "Categorical vs Numerical Analysis": "Visualization Analytics",
    "Time Series Analytics": "Visualization Analytics",

    "Intelligent Insight Generator": "Intelligent Insight Generator",

    "Download Report PDF": "Reporting System",
    "Download HTML Dashboard": "Reporting System",
    "Export Result to Excel/CSV": "Reporting System",
}


def get_active_group():
    return PAGE_GROUP.get(st.session_state.page, "Dashboard")


def nav_button(label, target_page, icon=""):
    is_active = st.session_state.page == target_page

    button_label = f"{icon} {label}"
    if is_active:
        button_label += " ✅"

    if st.button(
        button_label,
        use_container_width=True,
        type="primary" if is_active else "secondary",
        key=f"nav_{target_page}"
    ):
        go_to(target_page)
        st.rerun()


# =========================
# MINI SIDEBAR ICONS WHEN COLLAPSED
# =========================
def handle_collapsed_sidebar_navigation():
    """Tidak dipakai lagi. Mini sidebar sekarang memakai st.button supaya tidak reload ke login."""
    return


def render_collapsed_sidebar_icons():
    """Mini sidebar saat sidebar utama ditutup.

    Perilaku:
    - Rail ikon selalu tetap dan tidak menggeser konten dashboard.
    - Ikon bab mempunyai posisi tetap di tengah rail.
    - Klik ikon bab membuka submenu ke bawah, bukan ke samping.
    - Ikon anak bab lebih kecil, rapi, dan berada di tengah jalur submenu.
    - Bab tanpa anak bab langsung membuka halamannya.
    """
    if not st.session_state.get("is_logged_in", False):
        return

    if "mini_open_group_v3" not in st.session_state:
        st.session_state.mini_open_group_v3 = None

    active_group = get_active_group()

    mini_items = [
        {
            "icon": "🏠", "label": "Dashboard", "target": "Dashboard", "group": "Dashboard",
            "children": []
        },
        {
            "icon": "📁", "label": "Data Management", "target": "Upload Data", "group": "Data Management",
            "children": [
                {"icon": "📤", "label": "Upload Data", "target": "Upload Data"},
                {"icon": "📄", "label": "File Information", "target": "File Information"},
                {"icon": "👁️", "label": "Data Preview", "target": "Data Preview"},
                {"icon": "📌", "label": "Dataset Information", "target": "Dataset Information"},
                {"icon": "🧹", "label": "Data Cleaning", "target": "Data Cleaning"},
            ],
        },
        {
            "icon": "📊", "label": "Descriptive Statistics", "target": "Numerical Variables", "group": "Descriptive Statistics",
            "children": [
                {"icon": "🔢", "label": "Numerical Variables", "target": "Numerical Variables"},
                {"icon": "🏷️", "label": "Categorical Variables", "target": "Categorical Variables"},
            ],
        },
        {
            "icon": "📈", "label": "Visualization Analytics", "target": "Numerical Visualization", "group": "Visualization Analytics",
            "children": [
                {"icon": "📈", "label": "Numerical Visualization", "target": "Numerical Visualization"},
                {"icon": "📊", "label": "Categorical Visualization", "target": "Categorical Visualization"},
                {"icon": "🔗", "label": "Bivariate & Multivariate Analysis", "target": "Bivariate & Multivariate Analysis"},
                {"icon": "📌", "label": "Categorical vs Numerical Analysis", "target": "Categorical vs Numerical Analysis"},
                {"icon": "⏱️", "label": "Time Series Analytics", "target": "Time Series Analytics"},
            ],
        },
        {
            "icon": "🧠", "label": "Intelligent Insight Generator", "target": "Intelligent Insight Generator", "group": "Intelligent Insight Generator",
            "children": []
        },
        {
            "icon": "📄", "label": "Reporting System", "target": "Download Report PDF", "group": "Reporting System",
            "children": [
                {"icon": "📄", "label": "Download Report PDF", "target": "Download Report PDF"},
                {"icon": "🌐", "label": "Download HTML Dashboard", "target": "Download HTML Dashboard"},
                {"icon": "📦", "label": "Export Result to Excel/CSV", "target": "Export Result to Excel/CSV"},
            ],
        },
    ]

    with st.container(key="mini_sidebar_rail_native"):
        st.markdown(
            '<div class="mini-sidebar-brand-native" title="Auto EDA Analytics">📊</div>',
            unsafe_allow_html=True,
        )

        for item in mini_items:
            children = item.get("children", [])
            has_children = bool(children)
            is_active = active_group == item["group"]
            is_open = st.session_state.mini_open_group_v3 == item["group"]
            item_key = safe_name(item["group"])

            with st.container(key=f"mini_item_{item_key}"):
                if has_children:
                    parent_help = (
                        f"{item['label']} — klik untuk "
                        f"{'menutup' if is_open else 'membuka'} submenu"
                    )
                else:
                    parent_help = item["label"]

                if st.button(
                    item["icon"],
                    key=f"mini_parent_{item_key}",
                    help=parent_help,
                    use_container_width=False,
                    type="primary" if (is_active or is_open) else "secondary",
                ):
                    if has_children:
                        st.session_state.mini_open_group_v3 = (
                            None if is_open else item["group"]
                        )
                    else:
                        st.session_state.mini_open_group_v3 = None
                        go_to(item["target"])

                    st.rerun()

                if has_children and is_open:
                    with st.container(key=f"mini_child_{item_key}"):
                        for child in children:
                            child_active = st.session_state.page == child["target"]

                            if st.button(
                                child["icon"],
                                key=f"mini_child_nav_{item_key}_{safe_name(child['target'])}",
                                help=child["label"],
                                use_container_width=False,
                                type="primary" if child_active else "secondary",
                            ):
                                st.session_state.mini_open_group_v3 = item["group"]
                                go_to(child["target"])
                                st.rerun()


# =========================
# SIDEBAR THEME TOGGLE
# =========================
with st.sidebar:
    st.title("📊 Auto EDA Analytics")

    active_group = get_active_group()

    nav_button("Dashboard", "Dashboard", "🏠")

    with st.expander("📁 Data Management", expanded=active_group == "Data Management"):
        nav_button("Upload Data", "Upload Data", "📤")
        nav_button("File Information", "File Information", "📄")
        nav_button("Data Preview", "Data Preview", "👁️")
        nav_button("Dataset Information", "Dataset Information", "📌")
        nav_button("Data Cleaning", "Data Cleaning", "🧹")

    with st.expander("📊 Descriptive Statistics", expanded=active_group == "Descriptive Statistics"):
        nav_button("Numerical Variables", "Numerical Variables", "🔢")
        nav_button("Categorical Variables", "Categorical Variables", "🏷️")

    with st.expander("📈 Visualization Analytics", expanded=active_group == "Visualization Analytics"):
        nav_button("Numerical Visualization", "Numerical Visualization", "📈")
        nav_button("Categorical Visualization", "Categorical Visualization", "📊")
        nav_button("Bivariate & Multivariate Analysis", "Bivariate & Multivariate Analysis", "🔗")
        nav_button("Categorical vs Numerical Analysis", "Categorical vs Numerical Analysis", "📌")
        nav_button("Time Series Analytics", "Time Series Analytics", "⏱️")

    nav_button(
        "Intelligent Insight Generator",
        "Intelligent Insight Generator",
        "🧠"
    )

    with st.expander("📄 Reporting System", expanded=active_group == "Reporting System"):
        nav_button("Download Report PDF", "Download Report PDF", "📄")
        nav_button("Download HTML Dashboard", "Download HTML Dashboard", "🌐")
        nav_button("Export Result to Excel/CSV", "Export Result to Excel/CSV", "📊")

# =========================
# SIDEBAR USER INFO - BOTTOM
# =========================
if st.session_state.get("is_logged_in"):
    st.sidebar.markdown(
        f"""
        <div class="sidebar-user-box">
            <div class="sidebar-user-label">👤 Login sebagai</div>
            <div class="sidebar-user-name">{st.session_state.get('logged_user', '-')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()



handle_collapsed_sidebar_navigation()
render_collapsed_sidebar_icons()

page = st.session_state.page


# =========================
# AUTHENTICATION GATE
# =========================
if not st.session_state.is_logged_in:
    if st.session_state.auth_page == "landing":
        show_landing_page()
    else:
        show_login_page()



# =========================
# PAGE ROUTER
# =========================
if page == "Upload Data":
    show_upload_page()

elif st.session_state.df is None:
    show_empty_dashboard_page()

else:
    df = st.session_state.df
    file_name = st.session_state.file_name
    file_ext = st.session_state.file_ext
    file_size = st.session_state.file_size
    saved_file_path = st.session_state.saved_file_path


    try:
        numeric_cols, categorical_cols, date_cols = detect_columns(df)
    except Exception:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = []


    try:
        num_stats = numerical_statistics(df)
    except Exception:
        num_stats = pd.DataFrame({"Message": ["Numerical statistics tidak tersedia."]})


    try:
        cat_stats = categorical_statistics(df)
    except Exception:
        cat_stats = pd.DataFrame({"Message": ["Categorical statistics tidak tersedia."]})


    try:
        insights = generate_insights(df, numeric_cols, date_cols, categorical_cols)
    except Exception:
        insights = [
            f"Dataset memiliki {df.shape[0]} baris dan {df.shape[1]} kolom.",
            f"Total missing value: {df.isna().sum().sum()}",
            "Insight generator lanjutan sementara tidak tersedia."
        ]


    common_args = (
        df, file_name, file_ext, file_size, saved_file_path,
        numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights,
        save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label
    )

    if page == "Dashboard":
        show_dashboard_page(*common_args)

    elif page == "File Information":
        show_file_information_page(*common_args)

    elif page == "Data Preview":
        show_data_preview_page(*common_args)

    elif page == "Dataset Information":
        show_dataset_information_page(*common_args)

    elif page == "Data Cleaning":
        show_data_cleaning_page(*common_args)

    elif page == "Numerical Variables":
        show_numerical_variables_page(*common_args)

    elif page == "Categorical Variables":
        show_categorical_variables_page(*common_args)

    elif page == "Numerical Visualization":
        show_numerical_visualization_page(*common_args)

    elif page == "Categorical Visualization":
        show_categorical_visualization_page(*common_args)

    elif page == "Bivariate & Multivariate Analysis":
        show_bivariate_multivariate_page(*common_args)

    elif page == "Categorical vs Numerical Analysis":
        show_categorical_vs_numerical_page(*common_args)

    elif page == "Time Series Analytics":
        show_time_series_page(*common_args)

    elif page == "Intelligent Insight Generator":
        show_insight_generator_page(*common_args)

    elif page == "Download Report PDF":
        show_download_pdf_page(*common_args)

    elif page == "Download HTML Dashboard":
        show_download_html_page(*common_args)

    elif page == "Export Result to Excel/CSV":
        show_export_excel_csv_page(*common_args)

