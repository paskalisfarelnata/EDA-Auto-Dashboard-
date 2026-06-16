import streamlit as st


# =========================
# MANUAL THEME CONTROL
# =========================
def apply_manual_theme_css():
    """
    Dark mode manual dari sidebar.
    Ini dipakai karena tombol Theme bawaan Streamlit kadang tidak terbaca oleh CSS
    dan AgGrid memiliki style sendiri.
    """
    if not st.session_state.get("manual_dark_mode", False):
        return

    st.markdown(
        """
        <style>
            html, body, .stApp, .main,
            [data-testid="stAppViewContainer"],
            [data-testid="stMain"] {
                background:
                    radial-gradient(ellipse 52% 30% at 4% 4%, rgba(52,217,240,0.11) 0%, transparent 58%),
                    radial-gradient(ellipse 44% 26% at 96% 10%, rgba(124,110,240,0.12) 0%, transparent 54%),
                    linear-gradient(148deg, #01060f 0%, #030d1e 45%, #050c1c 72%, #01060f 100%) !important;
                color: #f8fafc !important;
            }

            .stApp,
            .stApp p,
            .stApp span,
            .stApp label,
            .stApp li,
            .stApp div,
            .stMarkdown,
            .stMarkdown p,
            .stMarkdown span,
            .stMarkdown li,
            [data-testid="stMarkdownContainer"],
            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMarkdownContainer"] span,
            [data-testid="stMarkdownContainer"] li {
                color: #e2e8f0 !important;
            }

            .stApp h1,
            .stApp h2,
            .stApp h3,
            .stApp h4,
            .stApp h5,
            .stApp h6,
            .stMarkdown h1,
            .stMarkdown h2,
            .stMarkdown h3,
            .stMarkdown h4,
            .stMarkdown h5,
            .stMarkdown h6 {
                color: #f8fafc !important;
            }

            [data-testid="stSidebar"],
            [data-testid="stSidebarContent"] {
                background: linear-gradient(180deg, #020b1a 0%, #031226 100%) !important;
                color: #f8fafc !important;
            }

            [data-testid="stSidebar"] *,
            [data-testid="stSidebarContent"] * {
                color: #e2e8f0 !important;
            }

            .section-title {
                background: linear-gradient(112deg, rgba(52,217,240,0.18), rgba(124,110,240,0.18), rgba(195,110,245,0.18)) !important;
                border: 1px solid rgba(52,217,240,0.30) !important;
                color: #f8fafc !important;
                text-shadow: 0 0 18px rgba(52,217,240,0.40) !important;
            }

            .info-card,
            .insight-box,
            .health-card,
            .quick-card,
            .widget-card,
            .landing-card,
            .login-card,
            .member-card,
            .identity-box,
            .identity-item,
            .sidebar-user-box,
            .compact-card,
            .compact-kpi,
            .compact-note,
            .upload-card,
            .upload-kpi,
            .upload-success-box,
            .upload-path,
            .clean-card,
            .clean-kpi,
            .clean-status-box,
            .clean-action-box,
            .clean-note,
            .clean-path,
            .empty-alert,
            .empty-kpi,
            .empty-feature-card,
            .empty-footer-note {
                background: rgba(15, 23, 42, 0.92) !important;
                border-color: rgba(96, 165, 250, 0.32) !important;
                color: #f8fafc !important;
                box-shadow:
                    0 18px 48px rgba(0,0,0,0.55),
                    0 0 34px rgba(52,217,240,0.10) !important;
            }

            .landing-card::after,
            .login-card::after {
                background: linear-gradient(148deg, #030d1e 0%, #031226 100%) !important;
            }

            .project-title,
            .login-title {
                background: linear-gradient(128deg, #34d9f0 0%, #8b5cf6 40%, #3dffd0 75%, #f8fafc 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                background-clip: text !important;
            }

            .compact-card-title,
            .upload-card-title,
            .clean-card-title,
            .empty-feature-title,
            .empty-section-title,
            .identity-value,
            .sidebar-user-name,
            .member-name,
            .compact-kpi-value,
            .upload-kpi-value,
            .clean-kpi-value,
            .empty-kpi-value {
                color: #f8fafc !important;
                -webkit-text-fill-color: initial !important;
            }

            .project-subtitle,
            .login-subtitle,
            .member-nim,
            .identity-label,
            .sidebar-user-label,
            .compact-label,
            .compact-insight,
            .upload-desc,
            .clean-desc,
            .clean-kpi-label,
            .upload-kpi-label,
            .small-note,
            .empty-subtitle,
            .empty-feature-text,
            .empty-step-text,
            .empty-kpi-label {
                color: #e2e8f0 !important;
            }

            .interpretation-content,
            .interpretation-content *,
            .interpretation-list-box,
            .interpretation-list-box *,
            .insight-box,
            .insight-box * {
                color: #f1f5f9 !important;
            }

            .interpretation-content b,
            .interpretation-content strong,
            .insight-box b,
            .insight-box strong {
                color: #ffffff !important;
                font-weight: 800 !important;
            }

            input,
            textarea,
            select,
            .stTextInput input,
            .stTextArea textarea,
            [data-baseweb="input"],
            [data-baseweb="select"],
            [data-baseweb="textarea"] {
                background: rgba(15,23,42,0.96) !important;
                border-color: rgba(96,165,250,0.42) !important;
                color: #f8fafc !important;
            }

            input::placeholder,
            textarea::placeholder {
                color: #94a3b8 !important;
            }

            .stSelectbox div,
            .stSelectbox span,
            .stTextInput div,
            .stTextInput span {
                color: #e2e8f0 !important;
            }

            [data-testid="stMetric"],
            [data-testid="stMetric"] *,
            [data-testid="stMetricLabel"],
            [data-testid="stMetricValue"] {
                color: #f8fafc !important;
            }

            [data-testid="stAlert"],
            [data-testid="stAlert"] *,
            .stAlert,
            .stAlert * {
                color: #f8fafc !important;
            }

            .stButton > button {
                background: linear-gradient(112deg, rgba(52,217,240,0.18), rgba(124,110,240,0.22), rgba(195,110,245,0.18)) !important;
                border: 1px solid rgba(52,217,240,0.42) !important;
                color: #f8fafc !important;
                text-shadow: 0 0 18px rgba(52,217,240,0.45) !important;
            }

            .stButton > button * {
                color: #f8fafc !important;
            }

            /* AgGrid dark force */
            .ag-theme-streamlit,
            .ag-root-wrapper,
            .ag-root,
            .ag-body-viewport,
            .ag-center-cols-container,
            .ag-center-cols-viewport {
                background: #0f172a !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.32) !important;
            }

            .ag-header,
            .ag-header-row,
            .ag-paging-panel {
                background: #020617 !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.32) !important;
            }

            .ag-header-cell,
            .ag-header-cell-label,
            .ag-header-cell-text {
                color: #ffffff !important;
                background: #020617 !important;
                font-weight: 900 !important;
            }

            .ag-row,
            .ag-row-odd,
            .ag-row-even {
                background: #0f172a !important;
                color: #e2e8f0 !important;
            }

            .ag-cell,
            .ag-cell-value {
                color: #e2e8f0 !important;
                background: transparent !important;
                border-color: rgba(148,163,184,0.18) !important;
            }

            .ag-row-hover,
            .ag-row:hover {
                background: #1e3a8a !important;
            }

            .ag-paging-panel *,
            .ag-paging-button,
            .ag-icon {
                color: #f8fafc !important;
            }

            .clean-table-label {
                color: #f8fafc !important;
            }

            a,
            a:visited {
                color: #67e8f9 !important;
            }


            /* FINAL SIDEBAR EXPANDER DARK FIX */
            [data-testid="stSidebar"] details,
            [data-testid="stSidebar"] summary,
            [data-testid="stSidebar"] [data-testid="stExpander"],
            [data-testid="stSidebar"] .streamlit-expanderHeader,
            [data-testid="stSidebar"] div[role="button"] {
                background: rgba(2, 11, 26, 0.92) !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.22) !important;
            }

            [data-testid="stSidebar"] details[open] summary,
            [data-testid="stSidebar"] summary:hover,
            [data-testid="stSidebar"] div[role="button"]:hover {
                background: rgba(15, 23, 42, 0.96) !important;
                color: #f8fafc !important;
            }

            [data-testid="stSidebar"] details *,
            [data-testid="stSidebar"] summary *,
            [data-testid="stSidebar"] [data-testid="stExpander"] *,
            [data-testid="stSidebar"] .streamlit-expanderHeader * {
                color: #f8fafc !important;
            }

            /* Toggle fixed dark text */
            .theme-fixed-toggle-disabled [data-testid="stToggle"] label,
            .theme-fixed-toggle-disabled [data-testid="stToggle"] p,
            .theme-fixed-toggle-disabled [data-testid="stToggle"] span {
                color: #f8fafc !important;
            }

            /* Jika ada kotak putih Streamlit lain */
            [data-testid="stSidebar"] > div,
            [data-testid="stSidebar"] section {
                background: transparent !important;
            }



            /* FINAL ALL COMPONENT DARK FIX — UPLOAD TOOLTIP REPORT */
            [data-testid="stFileUploader"],
            [data-testid="stFileUploader"] *,
            [data-testid="stFileUploaderDropzone"],
            [data-testid="stFileUploaderDropzone"] *,
            section[data-testid="stFileUploaderDropzone"],
            section[data-testid="stFileUploaderDropzone"] * {
                background: rgba(15,23,42,0.92) !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.34) !important;
            }

            [data-testid="stFileUploader"] button,
            [data-testid="stFileUploaderDropzone"] button {
                background: rgba(30,41,59,0.96) !important;
                color: #f8fafc !important;
                border: 1px solid rgba(96,165,250,0.36) !important;
            }

            [data-testid="stFileUploader"] small,
            [data-testid="stFileUploader"] span,
            [data-testid="stFileUploader"] p {
                color: #e2e8f0 !important;
            }

            /* Toast / notification */
            [data-testid="stToast"],
            [data-testid="stToast"] *,
            div[data-testid="stNotification"],
            div[data-testid="stNotification"] *,
            [data-testid="stStatusWidget"],
            [data-testid="stStatusWidget"] * {
                background: rgba(15,23,42,0.96) !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.30) !important;
            }

            /* Tooltip */
            [data-baseweb="tooltip"],
            [data-baseweb="tooltip"] *,
            div[role="tooltip"],
            div[role="tooltip"] * {
                background: #020617 !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.30) !important;
            }

            /* Download/report/export cards and buttons */
            .report-card,
            .download-card,
            .export-card,
            .pdf-card,
            .html-card,
            .excel-card,
            .csv-card,
            .report-box,
            .download-box,
            .export-box {
                background: rgba(15,23,42,0.92) !important;
                border: 1px solid rgba(96,165,250,0.32) !important;
                color: #f8fafc !important;
                box-shadow: 0 18px 48px rgba(0,0,0,0.45) !important;
            }

            .report-card *,
            .download-card *,
            .export-card *,
            .pdf-card *,
            .html-card *,
            .excel-card *,
            .csv-card *,
            .report-box *,
            .download-box *,
            .export-box * {
                color: #f8fafc !important;
            }

            [data-testid="stDownloadButton"] button,
            [data-testid="stDownloadButton"] button * {
                background: linear-gradient(112deg, rgba(52,217,240,0.18), rgba(124,110,240,0.22), rgba(195,110,245,0.18)) !important;
                border: 1px solid rgba(52,217,240,0.42) !important;
                color: #f8fafc !important;
            }

            /* AgGrid footer/page size stronger */
            .ag-paging-panel,
            .ag-paging-panel *,
            .ag-paging-row-summary-panel,
            .ag-paging-page-summary-panel,
            .ag-paging-page-size,
            .ag-paging-page-size *,
            .ag-picker-field,
            .ag-picker-field *,
            .ag-select,
            .ag-select *,
            .ag-list,
            .ag-list * {
                background: #020617 !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.32) !important;
            }

            .ag-wrapper,
            .ag-picker-field-wrapper {
                background: #0f172a !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.32) !important;
            }

            .ag-icon {
                color: #f8fafc !important;
                fill: #f8fafc !important;
            }

            /* Expander active white fix */
            [data-testid="stSidebar"] details[open] > summary,
            [data-testid="stSidebar"] details[open] > summary *,
            [data-testid="stSidebar"] [aria-expanded="true"],
            [data-testid="stSidebar"] [aria-expanded="true"] * {
                background: rgba(15,23,42,0.96) !important;
                color: #f8fafc !important;
            }

            /* FINAL SAFE SIDEBAR TOGGLE DARK FIX */
            .theme-sidebar-box {
                background: rgba(15,23,42,0.92) !important;
                border: 1px solid rgba(96,165,250,0.30) !important;
                border-radius: 16px !important;
                padding: 10px 12px !important;
                margin: 8px 0 8px 0 !important;
                box-shadow: 0 10px 24px rgba(0,0,0,0.25) !important;
            }

            .theme-sidebar-label {
                color: #f8fafc !important;
                font-weight: 850 !important;
                font-size: 12.5px !important;
                letter-spacing: 0.3px !important;
            }

            [data-testid="stSidebar"] div[data-testid="stToggle"] {
                background: rgba(15,23,42,0.74) !important;
                border: 1px solid rgba(96,165,250,0.26) !important;
                border-radius: 16px !important;
                padding: 8px 10px !important;
                margin-bottom: 14px !important;
                cursor: pointer !important;
            }

            [data-testid="stSidebar"] div[data-testid="stToggle"] label,
            [data-testid="stSidebar"] div[data-testid="stToggle"] p,
            [data-testid="stSidebar"] div[data-testid="stToggle"] span {
                color: #f8fafc !important;
                font-weight: 800 !important;
                cursor: pointer !important;
                white-space: nowrap !important;
            }

            [data-testid="stSidebar"] div[data-testid="stToggle"] div {
                cursor: pointer !important;
            }

            [data-testid="stSidebar"] details,
            [data-testid="stSidebar"] summary,
            [data-testid="stSidebar"] [data-testid="stExpander"],
            [data-testid="stSidebar"] .streamlit-expanderHeader,
            [data-testid="stSidebar"] div[role="button"] {
                background: rgba(2, 11, 26, 0.92) !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.22) !important;
            }

            [data-testid="stSidebar"] details *,
            [data-testid="stSidebar"] summary *,
            [data-testid="stSidebar"] [data-testid="stExpander"] *,
            [data-testid="stSidebar"] .streamlit-expanderHeader * {
                color: #f8fafc !important;
            }

            /* EXTRA STREAMLIT WIDGET DARK FIX */
            [data-testid="stSelectbox"],
            [data-testid="stSelectbox"] *,
            [data-baseweb="select"],
            [data-baseweb="select"] *,
            [data-baseweb="popover"],
            [data-baseweb="popover"] *,
            [role="listbox"],
            [role="listbox"] *,
            [role="option"],
            [role="option"] * {
                color: #f8fafc !important;
            }

            [data-baseweb="select"] > div,
            [data-baseweb="popover"],
            [role="listbox"] {
                background: rgba(15,23,42,0.96) !important;
                border-color: rgba(96,165,250,0.42) !important;
            }

            /* Toggle tetap kelihatan di mode gelap */
            div[data-testid="stToggle"] label,
            div[data-testid="stToggle"] span,
            div[data-testid="stToggle"] p {
                color: #f8fafc !important;
            }

            /* Plotly and chart containers */
            .stPlotlyChart,
            .stPlotlyChart > div,
            .js-plotly-plot,
            .plot-container,
            .svg-container {
                background: #020617 !important;
                color: #f8fafc !important;
            }

            .stPlotlyChart svg,
            .stPlotlyChart g,
            .stPlotlyChart text {
                color: #e2e8f0 !important;
                fill: #e2e8f0 !important;
            }

            .stPlotlyChart .modebar,
            .stPlotlyChart .modebar-group {
                background: rgba(15,23,42,0.65) !important;
            }

            .stPlotlyChart .modebar-btn path {
                fill: #e2e8f0 !important;
            }

            /* Selectbox/dropdown agar tidak putih menyilaukan */
            [data-baseweb="select"] > div,
            [data-baseweb="popover"],
            [data-baseweb="menu"],
            [role="listbox"],
            [role="option"] {
                background: rgba(15,23,42,0.96) !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,0.40) !important;
            }

            [data-baseweb="select"] span,
            [data-baseweb="popover"] span,
            [data-baseweb="menu"] span,
            [role="listbox"] *,
            [role="option"] * {
                color: #f8fafc !important;
            }

            /* White containers fallback */
            iframe,
            .element-container {
                color: #e2e8f0 !important;
            }

        </style>
        """,
        unsafe_allow_html=True
    )


def get_aggrid_custom_css():
    """Custom CSS AgGrid agar tabel ikut Light/Dark toggle manual."""
    if st.session_state.get("manual_dark_mode", False):
        return {
            ".ag-root-wrapper": {
                "background-color": "#0f172a !important",
                "border-radius": "14px !important",
                "border": "1px solid rgba(96,165,250,0.32) !important",
                "box-shadow": "0 8px 26px rgba(0,0,0,0.40) !important"
            },
            ".ag-root": {
                "background-color": "#0f172a !important",
                "color": "#f8fafc !important"
            },
            ".ag-header": {
                "background-color": "#020617 !important",
                "color": "#f8fafc !important",
                "border-bottom": "1px solid rgba(96,165,250,0.32) !important"
            },
            ".ag-header-cell": {
                "background-color": "#020617 !important",
                "color": "#f8fafc !important"
            },
            ".ag-header-cell-label": {
                "font-size": "14px !important",
                "font-weight": "900 !important",
                "color": "#f8fafc !important"
            },
            ".ag-header-cell-text": {
                "color": "#ffffff !important",
                "font-weight": "900 !important"
            },
            ".ag-row": {
                "background-color": "#0f172a !important",
                "color": "#e2e8f0 !important"
            },
            ".ag-row-odd": {
                "background-color": "#111827 !important",
                "color": "#e2e8f0 !important"
            },
            ".ag-row-even": {
                "background-color": "#0f172a !important",
                "color": "#e2e8f0 !important"
            },
            ".ag-row-hover": {
                "background-color": "#1e3a8a !important"
            },
            ".ag-cell": {
                "font-size": "13.5px !important",
                "color": "#e2e8f0 !important",
                "border-bottom": "1px solid rgba(148,163,184,0.18) !important",
                "background-color": "transparent !important"
            },
            ".ag-cell-value": {
                "color": "#e2e8f0 !important"
            },
            ".ag-paging-panel": {
                "background-color": "#020617 !important",
                "color": "#e2e8f0 !important",
                "border-top": "1px solid rgba(96,165,250,0.32) !important"
            },
            ".ag-paging-panel *": {
                "color": "#e2e8f0 !important"
            },
            ".ag-picker-field": {
                "background-color": "#0f172a !important",
                "color": "#f8fafc !important",
                "border": "1px solid rgba(96,165,250,0.36) !important"
            },
            ".ag-picker-field-wrapper": {
                "background-color": "#0f172a !important",
                "color": "#f8fafc !important",
                "border": "1px solid rgba(96,165,250,0.36) !important"
            },
            ".ag-select": {
                "background-color": "#0f172a !important",
                "color": "#f8fafc !important"
            },
            ".ag-select *": {
                "background-color": "#0f172a !important",
                "color": "#f8fafc !important"
            },
            ".ag-list": {
                "background-color": "#0f172a !important",
                "color": "#f8fafc !important"
            },
            ".ag-list *": {
                "background-color": "#0f172a !important",
                "color": "#f8fafc !important"
            },

            ".ag-center-cols-viewport": {
                "background-color": "#0f172a !important",
                "overflow-x": "auto !important"
            }
        }

    return {
        ".ag-root-wrapper": {
            "border-radius": "14px !important",
            "border": "1px solid #dbeafe !important",
            "box-shadow": "0 6px 18px rgba(15, 23, 42, 0.06) !important"
        },
        ".ag-header": {
            "background-color": "#f8fafc !important"
        },
        ".ag-header-cell-label": {
            "font-size": "14px !important",
            "font-weight": "900 !important",
            "color": "#0f172a !important"
        },
        ".ag-cell": {
            "font-size": "13.5px !important",
            "color": "#1e293b !important"
        },
        ".ag-row-hover": {
            "background-color": "#eff6ff !important"
        },
        ".ag-center-cols-viewport": {
            "overflow-x": "auto !important"
        }
    }


# =========================
# PLOTLY THEME SYNC
# =========================
def apply_plotly_manual_theme(fig):
    """
    Membuat semua grafik Plotly ikut Light/Dark Manual Mode.
    Ini penting karena grafik Plotly punya background dan font sendiri,
    sehingga tidak cukup hanya diubah lewat CSS.
    """
    if fig is None or not hasattr(fig, "update_layout"):
        return fig

    if st.session_state.get("manual_dark_mode", False):
        paper_bg = "#020617"
        plot_bg = "#020617"
        text_color = "#f8fafc"
        sub_text = "#cbd5e1"
        grid_color = "rgba(148, 163, 184, 0.24)"
        zero_color = "rgba(148, 163, 184, 0.38)"
    else:
        paper_bg = "#ffffff"
        plot_bg = "#ffffff"
        text_color = "#0f172a"
        sub_text = "#64748b"
        grid_color = "rgba(148, 163, 184, 0.28)"
        zero_color = "rgba(148, 163, 184, 0.45)"

    try:
        fig.update_layout(
            paper_bgcolor=paper_bg,
            plot_bgcolor=plot_bg,
            font=dict(color=text_color),
            title_font=dict(color=text_color),
            hoverlabel=dict(
                bgcolor="#0f172a" if st.session_state.get("manual_dark_mode", False) else "#ffffff",
                bordercolor="rgba(96,165,250,0.40)" if st.session_state.get("manual_dark_mode", False) else "rgba(37,99,235,0.25)",
                font=dict(
                    color="#f8fafc" if st.session_state.get("manual_dark_mode", False) else "#0f172a",
                    size=12
                )
            ),
            legend=dict(
                font=dict(color=text_color),
                bgcolor="rgba(0,0,0,0)"
            ),
            xaxis=dict(
                color=sub_text,
                title_font=dict(color=sub_text),
                tickfont=dict(color=sub_text),
                gridcolor=grid_color,
                zerolinecolor=zero_color,
                linecolor=grid_color
            ),
            yaxis=dict(
                color=sub_text,
                title_font=dict(color=sub_text),
                tickfont=dict(color=sub_text),
                gridcolor=grid_color,
                zerolinecolor=zero_color,
                linecolor=grid_color
            )
        )

        # Untuk figure dengan banyak axis/subplot
        fig.update_xaxes(
            color=sub_text,
            title_font=dict(color=sub_text),
            tickfont=dict(color=sub_text),
            gridcolor=grid_color,
            zerolinecolor=zero_color,
            linecolor=grid_color
        )
        fig.update_yaxes(
            color=sub_text,
            title_font=dict(color=sub_text),
            tickfont=dict(color=sub_text),
            gridcolor=grid_color,
            zerolinecolor=zero_color,
            linecolor=grid_color
        )
    except Exception:
        pass

    return fig


_original_plotly_chart = st.plotly_chart

def themed_plotly_chart(fig, *args, **kwargs):
    fig = apply_plotly_manual_theme(fig)
    return _original_plotly_chart(fig, *args, **kwargs)

st.plotly_chart = themed_plotly_chart
