import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PLOT_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}

PASTEL_COLORS = [
    "#60A5FA",  # blue
    "#A78BFA",  # purple
    "#34D399",  # mint
    "#F472B6",  # pink
    "#FBBF24",  # yellow
    "#22D3EE",  # cyan
    "#FB923C",  # orange
]

PASTEL_HEATMAP = [
    [0.00, "#DBEAFE"],
    [0.35, "#60A5FA"],
    [0.70, "#A78BFA"],
    [1.00, "#F472B6"],
]


def dashboard_go_to(page_name):
    st.session_state.page = page_name
    st.rerun()


def _is_dark():
    # Dark theme permanen: tidak lagi bergantung pada manual_dark_mode.
    return True


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


def _style_plot(fig, height=260, title=None, color_index=0):
    is_dark = _is_dark()
    text_color = "#E2E8F0" if is_dark else "#0F172A"
    title_color = "#FFFFFF" if is_dark else "#0F172A"
    paper_bg = "#0F172A" if is_dark else "rgba(255,255,255,0.96)"
    plot_bg = "#111827" if is_dark else "rgba(248,250,252,0.98)"
    grid_color = "rgba(255,255,255,0.10)" if is_dark else "rgba(15,23,42,0.10)"
    line_color = "rgba(255,255,255,0.18)" if is_dark else "rgba(15,23,42,0.18)"
    template = "plotly_dark" if is_dark else "plotly_white"

    fig.update_layout(
        template=template,
        height=height,
        title=dict(
            text=str(title or " "),
            x=0.5,
            xanchor="center",
            font=dict(size=14, color=title_color),
        ),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=text_color, size=11),
        margin=dict(l=35, r=25, t=48, b=42),
        colorway=PASTEL_COLORS,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_color),
            orientation="h",
            yanchor="bottom",
            y=-0.28,
            xanchor="center",
            x=0.5,
        ),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=grid_color,
        zeroline=False,
        linecolor=line_color,
        tickfont=dict(color=text_color),
        title_font=dict(color=text_color),
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=grid_color,
        zeroline=False,
        linecolor=line_color,
        tickfont=dict(color=text_color),
        title_font=dict(color=text_color),
    )

    for i, trace in enumerate(fig.data):
        color = PASTEL_COLORS[(color_index + i) % len(PASTEL_COLORS)]
        trace_type = getattr(trace, "type", "")

        if trace_type in ["histogram", "bar"]:
            trace.update(marker=dict(color=color, line=dict(color="white", width=1)))
        elif trace_type in ["box", "violin"]:
            trace.update(marker=dict(color=color), line=dict(color=color), fillcolor=color)
        elif trace_type in ["scatter", "scattergl"]:
            trace.update(
                marker=dict(color=color, size=8, opacity=0.82, line=dict(color="white", width=1)),
                line=dict(color=color, width=3),
            )
        elif trace_type == "pie":
            trace.update(
                marker=dict(colors=PASTEL_COLORS, line=dict(color="#ffffff" if not is_dark else "#0f172a", width=2)),
                textfont=dict(color=title_color),
            )
        elif trace_type == "heatmap":
            trace.update(colorscale=PASTEL_HEATMAP)

    return fig


def _safe_card_container(border=True):
    try:
        return st.container(border=border)
    except TypeError:
        return st.container()


def _table_dynamic_height(data, min_height=150, max_height=320, row_height=32):
    try:
        row_count = len(data)
    except Exception:
        row_count = 6
    calculated_height = 46 + (max(row_count, 1) * row_height) + 12
    return int(min(max(calculated_height, min_height), max_height))


def _inject_dashboard_css():
    if _is_dark():
        page_bg = "rgba(15,23,42,.92)"
        card_bg = "rgba(15,23,42,.90)"
        light_card_bg = "rgba(15,23,42,.90)"
        border = "rgba(96,165,250,.32)"
        text_1 = "#F8FAFC"
        text_2 = "#E2E8F0"
        text_3 = "#CBD5E1"
        title_bg = "linear-gradient(135deg, rgba(15,23,42,.98), rgba(30,64,175,.92))"
        benefit_bg = "rgba(15,23,42,.90)"
        shadow = "0 14px 34px rgba(0,0,0,.35)"
    else:
        page_bg = "rgba(255,255,255,.96)"
        card_bg = "rgba(255,255,255,.96)"
        light_card_bg = "rgba(255,255,255,.96)"
        border = "rgba(37,99,235,.16)"
        text_1 = "#0F172A"
        text_2 = "#334155"
        text_3 = "#475569"
        title_bg = "linear-gradient(135deg, #EFF6FF, #EDE9FE)"
        benefit_bg = "linear-gradient(135deg, #ECFDF5, #EFF6FF)"
        shadow = "0 12px 28px rgba(15,23,42,.08)"

    st.markdown(
        f"""
        <style>
            .main .block-container,
            section.main .block-container,
            div[data-testid="stMainBlockContainer"],
            div[data-testid="stAppViewContainer"] .block-container {{
                max-width: 100% !important;
                width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: .65rem !important;
            }}

            div[data-testid="stHorizontalBlock"] {{
                gap: .75rem !important;
            }}

            div[data-testid="stVerticalBlock"] {{
                gap: .55rem !important;
            }}

            div[data-testid="stVerticalBlockBorderWrapper"] {{
                background: {card_bg} !important;
                border: 1px solid {border} !important;
                box-shadow: {shadow} !important;
                border-radius: 18px !important;
                padding: .8rem !important;
                color: {text_2} !important;
            }}

            .dash-top {{
                display: grid;
                grid-template-columns: 1.35fr .75fr;
                gap: 14px;
                align-items: stretch;
                margin-bottom: 12px;
            }}

            .dash-title-card {{
                border-radius: 22px;
                border: 1px solid {border};
                background: {title_bg};
                padding: 18px 22px;
                min-height: 128px;
                box-shadow: {shadow};
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}

            .dash-title {{
                font-size: clamp(30px, 3.2vw, 50px);
                font-weight: 1000;
                letter-spacing: .05em;
                color: {text_1} !important;
                line-height: 1;
                text-transform: uppercase;
            }}

            .dash-desc {{
                margin-top: 10px;
                font-size: 13px;
                line-height: 1.55;
                color: {text_2} !important;
                max-width: 900px;
                font-weight: 650;
            }}

            .dash-benefit-card {{
                border-radius: 22px;
                border: 1px solid {border};
                background: {benefit_bg};
                color: {text_2} !important;
                padding: 16px 18px;
                box-shadow: {shadow};
                min-height: 128px;
            }}

            .dash-benefit-title {{
                font-size: 15px;
                font-weight: 1000;
                color: {text_1} !important;
                letter-spacing: .05em;
                text-transform: uppercase;
                margin-bottom: 8px;
            }}

            .dash-benefit-item {{
                display: flex;
                gap: 8px;
                align-items: flex-start;
                font-size: 12.5px;
                font-weight: 800;
                color: {text_2} !important;
                line-height: 1.45;
                margin: 5px 0;
            }}

            .dash-benefit-item span:first-child {{
                color: #34D399 !important;
                font-weight: 1000;
            }}

            .dash-metric-grid {{
                display: grid;
                grid-template-columns: repeat(6, minmax(0, 1fr));
                gap: 11px;
                margin: 10px 0 14px;
            }}

            .dash-metric {{
                min-height: 92px;
                border-radius: 18px;
                border: 1px solid {border};
                background: {card_bg};
                display: grid;
                grid-template-columns: 42px 1fr;
                gap: 9px;
                align-items: center;
                padding: 13px;
                box-shadow: {shadow};
                transition: all .22s ease;
            }}

            .dash-metric:hover {{
                transform: translateY(-4px);
                box-shadow: 0 18px 38px rgba(37,99,235,.14);
            }}

            .dash-metric-icon {{
                font-size: 25px;
                line-height: 1;
            }}

            .dash-metric-title {{
                font-size: 10.5px;
                color: {text_3} !important;
                font-weight: 950;
                text-transform: uppercase;
                letter-spacing: .07em;
                line-height: 1.4;
            }}

            .dash-metric-value {{
                color: #60A5FA !important;
                font-size: 24px;
                font-weight: 1000;
                line-height: 1.15;
                margin-top: 5px;
            }}

            .dash-metric-sub {{
                margin-top: 2px;
                font-size: 11px;
                color: {text_3} !important;
                font-weight: 750;
            }}

            .dash-card-title {{
                color: {text_1} !important;
                font-size: 14px;
                font-weight: 1000;
                margin-bottom: 8px;
                letter-spacing: .02em;
            }}

            .dash-section-title {{
                font-size: 17px;
                font-weight: 1000;
                color: {text_1} !important;
                margin: 16px 0 8px 0;
            }}

            .dash-panel {{
                border-radius: 18px;
                border: 1px solid {border};
                background: {light_card_bg};
                color: {text_2} !important;
                padding: 14px 15px;
                box-shadow: {shadow};
                margin-bottom: 12px;
            }}

            .dash-panel-title {{
                font-size: 15px;
                font-weight: 1000;
                color: {text_1} !important;
                text-transform: uppercase;
                letter-spacing: .04em;
                margin-bottom: 10px;
            }}

            .dash-step {{
                display: grid;
                grid-template-columns: 25px 1fr;
                gap: 9px;
                margin: 10px 0;
            }}

            .dash-step-num {{
                width: 24px;
                height: 24px;
                border-radius: 999px;
                background: #2563EB;
                color: white !important;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: 1000;
            }}

            .dash-step-text {{
                font-size: 12px;
                line-height: 1.45;
                color: {text_2} !important;
                font-weight: 700;
            }}

            .dash-step-text b {{
                color: {text_1} !important;
                font-weight: 1000;
            }}

            .dash-bullet {{
                display: flex;
                gap: 8px;
                align-items: flex-start;
                font-size: 12.5px;
                color: {text_2} !important;
                font-weight: 800;
                line-height: 1.45;
                margin: 8px 0;
            }}

            .dash-bullet span:first-child {{
                color: #34D399 !important;
                font-weight: 1000;
            }}

            .dash-mini-summary {{
                margin-top: 8px;
                border-radius: 14px;
                border: 1px solid {border};
                background: {card_bg};
                padding: 10px 12px;
                color: {text_2} !important;
            }}

            .dash-mini-title {{
                color: {text_1} !important;
                font-size: 12.2px;
                font-weight: 1000;
                letter-spacing: .04em;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}

            .dash-mini-row {{
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 8px;
                color: {text_2} !important;
                font-size: 11.4px;
                font-weight: 750;
                line-height: 1.35;
                padding: 3px 0;
                border-bottom: 1px solid rgba(148,163,184,.16);
            }}

            .dash-mini-row:last-child {{
                border-bottom: 0;
            }}

            .dash-mini-value {{
                color: #34D399 !important;
                font-weight: 950;
                text-align: right;
            }}

            div[data-testid="stButton"] > button {{
                border-radius: 15px !important;
                min-height: 43px !important;
                font-weight: 850 !important;
                border: 1px solid rgba(34, 211, 238, .28) !important;
                background: linear-gradient(135deg, #2563EB, #7C3AED, #0891B2) !important;
                color: #FFFFFF !important;
                transition: all .22s ease !important;
            }}

            div[data-testid="stButton"] > button:hover {{
                transform: translateY(-3px);
                box-shadow: 0 0 28px rgba(34, 211, 238, .18) !important;
                border-color: rgba(34, 211, 238, .55) !important;
            }}

            div[data-testid="stButton"] > button * {{
                color: #FFFFFF !important;
            }}

            div[data-testid="stDataFrame"] {{
                border-radius: 14px !important;
                overflow: hidden !important;
                border: 1px solid {border} !important;
            }}

            div[data-testid="stPlotlyChart"] {{
                width: 100% !important;
                margin-top: 0 !important;
                margin-bottom: 0 !important;
            }}


            /* FINAL DARK READABILITY OVERRIDE */
            .dash-title-card,
            .dash-benefit-card,
            .dash-metric,
            .dash-panel,
            .dash-mini-summary,
            div[data-testid="stVerticalBlockBorderWrapper"] {{
                background: rgba(15, 23, 42, 0.94) !important;
                border-color: rgba(96, 165, 250, 0.34) !important;
                color: #E2E8F0 !important;
            }}

            .dash-title,
            .dash-benefit-title,
            .dash-card-title,
            .dash-section-title,
            .dash-panel-title,
            .dash-mini-title,
            section.main h1,
            section.main h2,
            section.main h3,
            section.main h4 {{
                color: #F8FAFC !important;
            }}

            .dash-desc,
            .dash-benefit-item,
            .dash-step-text,
            .dash-bullet,
            .dash-mini-row,
            .dash-metric-title,
            .dash-metric-sub,
            section.main p,
            section.main li,
            section.main span,
            section.main div[data-testid="stMarkdownContainer"] * {{
                color: #E2E8F0 !important;
                opacity: 1 !important;
            }}

            .dash-metric-value,
            .dash-mini-value {{
                color: #60A5FA !important;
                opacity: 1 !important;
            }}

            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {{
                background: rgba(15, 23, 42, 0.94) !important;
                color: #F8FAFC !important;
            }}

            @media (max-width: 1200px) {{
                .dash-top {{
                    grid-template-columns: 1fr;
                }}
                .dash-metric-grid {{
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                }}
            }}

            @media (max-width: 800px) {{
                .dash-metric-grid {{
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _metric_card(icon, title, value, subtext):
    return (
        f'<div class="dash-metric">'
        f'<div class="dash-metric-icon">{icon}</div>'
        f'<div>'
        f'<div class="dash-metric-title">{title}</div>'
        f'<div class="dash-metric-value">{value}</div>'
        f'<div class="dash-metric-sub">{subtext}</div>'
        f'</div>'
        f'</div>'
    )


def _bullet(text):
    return f'<div class="dash-bullet"><span>✓</span><div>{text}</div></div>'


def _top_missing_columns(df, limit=6):
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False).head(limit)
    if missing.empty:
        return pd.DataFrame({"Column": ["No Missing"], "Missing": [0]})
    return pd.DataFrame({"Column": missing.index.astype(str), "Missing": missing.values})


def _data_type_donut(df, numeric_cols, categorical_cols, date_cols):
    num_count = len([c for c in numeric_cols if c in df.columns])
    cat_count = len([c for c in categorical_cols if c in df.columns])
    date_count = len([c for c in (date_cols or []) if c in df.columns])
    other_count = max(0, df.shape[1] - num_count - cat_count - date_count)

    type_df = pd.DataFrame(
        {
            "Type": ["Numeric", "Categorical", "Date", "Other"],
            "Count": [num_count, cat_count, date_count, other_count],
        }
    )
    type_df = type_df[type_df["Count"] > 0]

    if type_df.empty:
        return None

    fig = px.pie(type_df, names="Type", values="Count", hole=0.55)
    return _style_plot(fig, height=265, title="Data Type Composition", color_index=0)


def _missing_overview_chart(df):
    missing_df = _top_missing_columns(df, limit=6)
    fig = px.bar(
        missing_df,
        x="Missing",
        y="Column",
        orientation="h",
        labels={"Column": "Column", "Missing": "Missing"},
    )
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(automargin=True)
    fig = _style_plot(fig, height=265, title="Missing Value Overview", color_index=1)
    fig.update_layout(margin=dict(l=82, r=26, t=48, b=38), showlegend=False)
    return fig


def _correlation_preview(df, numeric_cols):
    valid_numeric_cols = [c for c in numeric_cols if c in df.columns]
    if len(valid_numeric_cols) < 2:
        return None

    corr = df[valid_numeric_cols].corr(numeric_only=True)
    fig = px.imshow(corr, text_auto=".2f", aspect="auto")
    return _style_plot(fig, height=265, title="Correlation Heatmap", color_index=2)


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
        fig = px.bar(
            x=cat_count.index.astype(str),
            y=cat_count.values,
            labels={"x": selected_cat, "y": "Count"},
        )
        return _style_plot(fig, height=265, title=f"Top Categories of {selected_cat}", color_index=1)
    return None


def _card_header(title):
    st.markdown(f'<div class="dash-card-title">{title}</div>', unsafe_allow_html=True)


def render_main_feature_menu():
    st.markdown('<div class="dash-section-title">🚀 Main Feature Menu</div>', unsafe_allow_html=True)

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
    get_health_label,
):
    _inject_dashboard_css()

    total_rows = df.shape[0]
    total_cols = df.shape[1]
    total_missing = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    numeric_count = len(numeric_cols)
    categorical_count = len(categorical_cols)
    date_count = len(date_cols)

    health_score = calculate_health_score(df)
    health_label = get_health_label(health_score)

    if numeric_count > categorical_count:
        dominant_type = "variabel numerik paling dominan"
    elif categorical_count > numeric_count:
        dominant_type = "variabel kategorikal paling dominan"
    else:
        dominant_type = "komposisi numerik dan kategorikal cukup seimbang"

    fig_type = _data_type_donut(df, numeric_cols, categorical_cols, date_cols)
    fig_missing = _missing_overview_chart(df)
    fig_corr = _correlation_preview(df, numeric_cols)
    fig_hist = _main_numeric_distribution(df, numeric_cols)
    fig_cat = _main_categorical_bar(df, categorical_cols)

    raw_preview = df.head(7)
    alert_df = pd.DataFrame(
        {
            "Indicator": [
                "Missing Cells",
                "Duplicate Rows",
                "Health Score",
                "Numeric Columns",
                "Categorical Columns",
            ],
            "Value": [
                total_missing,
                duplicate_rows,
                f"{health_score}/100",
                numeric_count,
                categorical_count,
            ],
            "Status": [
                "Check" if total_missing else "Good",
                "Check" if duplicate_rows else "Good",
                health_label,
                "Available" if numeric_count else "None",
                "Available" if categorical_count else "None",
            ],
        }
    )

    st.markdown(
        f"""
        <div class="dash-top">
            <div class="dash-title-card">
                <div class="dash-title">EDA DASHBOARD</div>
                <div class="dash-desc">
                    Dashboard analitik otomatis untuk membaca dataset, melihat statistik deskriptif,
                    memantau kualitas data, menampilkan visualisasi, dan menghasilkan insight awal.
                </div>
            </div>
            <div class="dash-benefit-card">
                <div class="dash-benefit-title">Benefits</div>
                <div class="dash-benefit-item"><span>✓</span><div>Memantau kualitas dataset secara real time</div></div>
                <div class="dash-benefit-item"><span>✓</span><div>Mengidentifikasi missing value dan duplicate rows</div></div>
                <div class="dash-benefit-item"><span>✓</span><div>Membantu analisis numerik, kategorikal, korelasi, dan insight</div></div>
                <div class="dash-benefit-item"><span>✓</span><div>Mempercepat proses eksplorasi data sebelum modeling/reporting</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpi_html = (
        '<div class="dash-metric-grid">'
        + _metric_card("📄", "Total Rows", f"{total_rows:,}", "jumlah baris dataset")
        + _metric_card("🧱", "Total Columns", f"{total_cols}", "jumlah kolom dataset")
        + _metric_card("🔢", "Numerical", f"{numeric_count}", "variabel numerik")
        + _metric_card("🏷️", "Categorical", f"{categorical_count}", "variabel kategorikal")
        + _metric_card("⚠️", "Missing Cells", f"{total_missing:,}", "sel kosong terdeteksi")
        + _metric_card("🔁", "Duplicate Rows", f"{duplicate_rows:,}", "baris duplikat")
        + "</div>"
    )
    st.markdown(kpi_html, unsafe_allow_html=True)

    main_area, side_area = st.columns([4.35, 1.05], gap="small")

    with main_area:
        v1, v2, v3 = st.columns(3, gap="small")

        with v1:
            with _safe_card_container(border=True):
                _card_header("🧩 Data Type Composition")
                if fig_type is not None:
                    st.plotly_chart(fig_type, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.info("Tipe data belum tersedia.")

        with v2:
            with _safe_card_container(border=True):
                _card_header("⚠️ Missing Value Overview")
                st.plotly_chart(fig_missing, use_container_width=True, config=PLOT_CONFIG)

        with v3:
            with _safe_card_container(border=True):
                _card_header("🔗 Correlation Heatmap")
                if fig_corr is not None:
                    st.plotly_chart(fig_corr, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.info("Correlation membutuhkan minimal 2 variabel numerik.")

        t1, t2 = st.columns([1.55, .95], gap="small")

        with t1:
            with _safe_card_container(border=True):
                _card_header("Top Dataset Preview")
                st.dataframe(
                    raw_preview,
                    use_container_width=True,
                    height=_table_dynamic_height(raw_preview, min_height=235, max_height=275, row_height=30),
                )

                st.markdown(
                    f"""
                    <div class="dash-mini-summary">
                        <div class="dash-mini-title">🧾 Dataset Summary</div>
                        <div class="dash-mini-row"><span>File Type</span><span class="dash-mini-value">{str(file_ext).upper()}</span></div>
                        <div class="dash-mini-row"><span>Dataset Size</span><span class="dash-mini-value">{_safe_file_size(file_size)}</span></div>
                        <div class="dash-mini-row"><span>Active Columns</span><span class="dash-mini-value">{total_cols}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with t2:
            with _safe_card_container(border=True):
                _card_header("Low Quality Alert")
                st.dataframe(
                    alert_df,
                    use_container_width=True,
                    height=_table_dynamic_height(alert_df, min_height=220, max_height=240, row_height=32),
                )

                st.markdown(
                    f"""
                    <div class="dash-mini-summary">
                        <div class="dash-mini-title">📌 Data Quality Summary</div>
                        <div class="dash-mini-row"><span>Health Status</span><span class="dash-mini-value">{health_label}</span></div>
                        <div class="dash-mini-row"><span>Missing Check</span><span class="dash-mini-value">{"Perlu dicek" if total_missing else "Aman"}</span></div>
                        <div class="dash-mini-row"><span>Duplicate Check</span><span class="dash-mini-value">{"Perlu dicek" if duplicate_rows else "Aman"}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        b1, b2 = st.columns(2, gap="small")

        with b1:
            with _safe_card_container(border=True):
                _card_header("Numerical Distribution")
                if fig_hist is not None:
                    st.plotly_chart(fig_hist, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.info("Tidak ada variabel numerik.")

        with b2:
            with _safe_card_container(border=True):
                _card_header("Categorical Ranking")
                if fig_cat is not None:
                    st.plotly_chart(fig_cat, use_container_width=True, config=PLOT_CONFIG)
                else:
                    st.info("Tidak ada variabel kategorikal.")

        render_main_feature_menu()

    with side_area:
        st.markdown(
            f"""
            <div class="dash-panel">
                <div class="dash-panel-title">⚙️ How It Works</div>
                <div class="dash-step"><div class="dash-step-num">1</div><div class="dash-step-text"><b>Data Input</b><br>Upload CSV, XLSX, atau TXT melalui menu Data Management.</div></div>
                <div class="dash-step"><div class="dash-step-num">2</div><div class="dash-step-text"><b>Dashboard Updates</b><br>Ringkasan baris, kolom, missing, duplicate, dan tipe data otomatis diperbarui.</div></div>
                <div class="dash-step"><div class="dash-step-num">3</div><div class="dash-step-text"><b>Key Metrics</b><br>Lihat KPI, statistik, visualisasi, dan alert kualitas data.</div></div>
                <div class="dash-step"><div class="dash-step-num">4</div><div class="dash-step-text"><b>Analyze & Act</b><br>Lanjutkan ke visualization, insight generator, atau reporting.</div></div>
            </div>
            <div class="dash-panel">
                <div class="dash-panel-title">🔍 Key Insights</div>
                {_bullet(f"Dataset aktif: {_truncate_text(file_name, 28)}")}
                {_bullet(f"{dominant_type}.")}
                {_bullet(f"Health score dataset adalah {health_score}/100.")}
                {_bullet(f"Missing cells: {total_missing:,}.")}
                {_bullet(f"Duplicate rows: {duplicate_rows:,}.")}
            </div>
            <div class="dash-panel">
                <div class="dash-panel-title">📄 Reporting</div>
                {_bullet("PDF report tersedia pada menu Reporting System.")}
                {_bullet("HTML dashboard dapat diunduh untuk dokumentasi.")}
                {_bullet("Excel dan CSV dapat diekspor untuk analisis lanjutan.")}
            </div>
            """,
            unsafe_allow_html=True,
        )
