import os
import textwrap
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PASTEL_COLORS = [
    "#F8A5C2",  # pastel pink
    "#85C1E9",  # pastel blue
    "#82E0AA",  # pastel green
    "#D7BDE2",  # pastel lilac
    "#F9E79F",  # pastel yellow
    "#AED6F1",  # soft sky
    "#A3E4D7",  # soft mint
]

PASTEL_SINGLE = {
    "pink": "#F8A5C2",
    "blue": "#85C1E9",
    "green": "#82E0AA",
    "purple": "#D7BDE2",
    "yellow": "#F9E79F"
}

PASTEL_HEATMAP = [
    [0.00, "#F8A5C2"],  # pink
    [0.50, "#85C1E9"],  # blue
    [1.00, "#82E0AA"],  # green
]

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True
}


def _safe_trace_update(trace, **kwargs):
    """Update trace tanpa membuat error kalau tipe chart tidak mendukung properti tertentu."""
    try:
        trace.update(**kwargs)
    except Exception:
        pass


def _clean_plot_text(value):
    """Bersihkan teks judul/label agar lebih enak dibaca di chart."""
    if value is None:
        return ""

    text = str(value)
    text = text.replace("<br>", " ")
    text = text.replace("<br />", " ")
    text = text.replace("_", " ")
    text = " ".join(text.split())
    return text


def _short_plot_label(value, max_len=24):
    """
    Memendekkan label axis yang terlalu panjang.
    Contoh: Performance_Score -> Performance Score
    """
    text = _clean_plot_text(value)

    if len(text) <= max_len:
        return text

    return text[:max_len - 3].rstrip() + "..."


def _wrap_plot_title(value, width=30):
    """
    Membungkus judul chart agar tidak terpotong di card 2 kolom.
    Plotly mendukung <br> untuk judul multi-baris.
    """
    text = _clean_plot_text(value)

    if not text:
        return " "

    wrapped = textwrap.wrap(text, width=width, break_long_words=False)

    if not wrapped:
        return text

    # Batasi maksimal 2 baris agar visual tetap rapi.
    if len(wrapped) > 2:
        wrapped = wrapped[:2]
        wrapped[-1] = _short_plot_label(wrapped[-1], 30)

    return "<br>".join(wrapped)


def _apply_title_and_axis_safety(fig):
    """
    Perapian global:
    - judul panjang turun baris
    - axis title tidak terlalu panjang
    - margin otomatis agar label tidak kepotong
    """
    if fig is None:
        return fig

    try:
        current_title = fig.layout.title.text
    except Exception:
        current_title = ""

    fig.update_layout(
        title=dict(
            text=_wrap_plot_title(current_title, width=30),
            x=0.5,
            xanchor="center",
            yanchor="top",
            font=dict(size=16, color="#FFFFFF"),
            pad=dict(t=8, b=8)
        ),
        margin=dict(l=55, r=42, t=92, b=68)
    )

    def _fix_xaxis(axis):
        try:
            if axis.title and axis.title.text:
                axis.title.text = _short_plot_label(axis.title.text, max_len=26)
        except Exception:
            pass

        axis.update(
            automargin=True,
            title_standoff=12,
            tickfont=dict(color="#DFF6FF", size=11),
        )

    def _fix_yaxis(axis):
        try:
            if axis.title and axis.title.text:
                axis.title.text = _short_plot_label(axis.title.text, max_len=26)
        except Exception:
            pass

        axis.update(
            automargin=True,
            title_standoff=12,
            tickfont=dict(color="#DFF6FF", size=11),
        )

    try:
        fig.for_each_xaxis(_fix_xaxis)
        fig.for_each_yaxis(_fix_yaxis)
    except Exception:
        pass

    return fig



def _wide_plotly_config():
    cfg = dict(PLOTLY_CONFIG) if isinstance(PLOTLY_CONFIG, dict) else {}
    cfg["responsive"] = True
    cfg["displaylogo"] = False
    return cfg

def apply_pastel_theme(fig, color_index=0):
    """
    Tema pastel global untuk semua chart Plotly:
    - background tidak putih
    - warna chart pastel pink/biru/hijau/lilac/kuning
    - judul panjang otomatis dibungkus agar tidak terpotong
    - axis dan label tetap terbaca di dark dashboard
    """
    if fig is None:
        return fig

    palette = PASTEL_COLORS
    base_color = palette[color_index % len(palette)]

    fig.update_layout(
        template="plotly_dark",
        colorway=palette,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        font=dict(
            family="Arial, sans-serif",
            color="#EAF6FF",
            size=13
        ),
        title_font=dict(
            size=16,
            color="#FFFFFF"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#EAF6FF", size=11)
        ),
        margin=dict(l=55, r=42, t=92, b=68)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.10)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.18)",
        tickfont=dict(color="#DFF6FF", size=11),
        title_font=dict(color="#EAF6FF", size=12),
        automargin=True,
        title_standoff=12
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.10)",
        zeroline=False,
        linecolor="rgba(255,255,255,0.18)",
        tickfont=dict(color="#DFF6FF", size=11),
        title_font=dict(color="#EAF6FF", size=12),
        automargin=True,
        title_standoff=12
    )

    # Ubah warna semua trace sesuai jenis chart
    for idx, trace in enumerate(fig.data):
        color = palette[(color_index + idx) % len(palette)]
        trace_type = getattr(trace, "type", "")

        if trace_type in ["histogram", "bar"]:
            _safe_trace_update(
                trace,
                marker=dict(
                    color=color,
                    line=dict(color="rgba(255,255,255,0.35)", width=1)
                )
            )

        elif trace_type in ["box", "violin"]:
            _safe_trace_update(trace, marker=dict(color=color))
            _safe_trace_update(trace, line=dict(color=color))
            _safe_trace_update(trace, fillcolor=color)

        elif trace_type in ["scatter", "scattergl"]:
            mode = getattr(trace, "mode", "") or ""
            if "lines" in mode:
                _safe_trace_update(
                    trace,
                    line=dict(color=color, width=3),
                    marker=dict(color=color, size=7, opacity=0.82)
                )
            else:
                _safe_trace_update(
                    trace,
                    marker=dict(
                        color=color,
                        size=8,
                        opacity=0.78,
                        line=dict(color="rgba(255,255,255,0.45)", width=1)
                    )
                )

        elif trace_type == "pie":
            _safe_trace_update(
                trace,
                marker=dict(
                    colors=palette,
                    line=dict(color="#0f172a", width=2)
                ),
                textfont=dict(color="#ffffff")
            )

        elif trace_type == "heatmap":
            _safe_trace_update(trace, colorscale=PASTEL_HEATMAP)

        elif trace_type == "splom":
            _safe_trace_update(
                trace,
                marker=dict(
                    color=base_color,
                    size=6,
                    opacity=0.70,
                    line=dict(color="rgba(255,255,255,0.35)", width=0.5)
                )
            )

    fig = _apply_title_and_axis_safety(fig)

    return fig


def apply_pastel_to_figures(*figs):
    """Shortcut supaya tidak perlu menulis apply_pastel_theme berkali-kali."""
    return tuple(apply_pastel_theme(fig, i) for i, fig in enumerate(figs))


def compact_categorical_chart_space(*figs):
    """
    Merapikan ruang kosong pada visual kategorikal.
    Khususnya pie chart dibuat lebih compact agar tidak menyisakan
    area putih besar sebelum kotak interpretasi.
    """
    fixed = []

    for fig in figs:
        if fig is None:
            fixed.append(fig)
            continue

        trace_types = [getattr(trace, "type", "") for trace in fig.data]
        has_pie = "pie" in trace_types
        has_bar = "bar" in trace_types

        if has_pie:
            fig.update_layout(
                height=365,
                margin=dict(l=18, r=18, t=72, b=22),
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=11, color="#EAF6FF")
                )
            )

            for trace in fig.data:
                if getattr(trace, "type", "") == "pie":
                    _safe_trace_update(
                        trace,
                        domain=dict(x=[0.04, 0.96], y=[0.15, 0.92]),
                        textposition="inside",
                        textfont=dict(size=11, color="#FFFFFF")
                    )

        elif has_bar:
            fig.update_layout(
                height=365,
                margin=dict(l=55, r=35, t=78, b=72)
            )
            fig.update_xaxes(automargin=True, tickangle=-25)
            fig.update_yaxes(automargin=True)

        else:
            fig.update_layout(
                height=375,
                margin=dict(l=55, r=42, t=82, b=62)
            )

        fixed.append(fig)

    return tuple(fixed)





def inject_visual_text_readability_css():
    """
    Memperjelas semua tulisan pada halaman visualisasi:
    interpretasi grafik, ringkasan, subheader, paragraf, list, dan teks markdown.
    """
    st.markdown(
        """
        <style>
            /* =====================================================
               VISUALIZATION TEXT READABILITY FINAL
               Membuat semua tulisan pada halaman visualisasi tidak samar.
               ===================================================== */

            section.main div[data-testid="stMarkdownContainer"],
            section.main div[data-testid="stMarkdownContainer"] p,
            section.main div[data-testid="stMarkdownContainer"] li,
            section.main div[data-testid="stMarkdownContainer"] span,
            section.main div[data-testid="stMarkdownContainer"] div {
                color: #EAF6FF !important;
                opacity: 1 !important;
                filter: none !important;
                text-shadow: none !important;
            }

            section.main div[data-testid="stMarkdownContainer"] h1,
            section.main div[data-testid="stMarkdownContainer"] h2,
            section.main div[data-testid="stMarkdownContainer"] h3,
            section.main div[data-testid="stMarkdownContainer"] h4,
            section.main div[data-testid="stMarkdownContainer"] strong,
            section.main div[data-testid="stMarkdownContainer"] b {
                color: #FFFFFF !important;
                opacity: 1 !important;
                font-weight: 900 !important;
                text-shadow: 0 0 10px rgba(103, 232, 249, .18) !important;
            }

            .section-title,
            .section-title *,
            .subsection-title,
            .subsection-title * {
                color: #67E8F9 !important;
                opacity: 1 !important;
                font-weight: 1000 !important;
                text-shadow: 0 0 16px rgba(103, 232, 249, .28) !important;
            }

            /* Box interpretasi dari backend chart_interpretation */
            .interpretation-box,
            .interpretation-box *,
            .interpretation-card,
            .interpretation-card *,
            .insight-box,
            .insight-box *,
            .summary-box,
            .summary-box *,
            .analysis-box,
            .analysis-box *,
            .interpretasi-box,
            .interpretasi-box * {
                color: #EAF6FF !important;
                opacity: 1 !important;
                filter: none !important;
            }

            .interpretation-box,
            .interpretation-card,
            .insight-box,
            .summary-box,
            .analysis-box,
            .interpretasi-box {
                background:
                    linear-gradient(135deg, rgba(15, 23, 42, .96), rgba(17, 24, 39, .94)) !important;
                border: 1px solid rgba(103, 232, 249, .22) !important;
                box-shadow: 0 14px 34px rgba(0, 0, 0, .22) !important;
            }

            /* Paragraf ringkasan yang biasanya tampak samar */
            section.main p,
            section.main li {
                color: #DFF6FF !important;
                opacity: 1 !important;
            }

            section.main small,
            section.main .caption,
            section.main [data-testid="stCaptionContainer"] {
                color: #CDEFFF !important;
                opacity: 1 !important;
            }

            /* Streamlit subheader bawaan */
            section.main h1,
            section.main h2,
            section.main h3,
            section.main h4 {
                color: #FFFFFF !important;
                opacity: 1 !important;
            }

            /* Info, warning, success text */
            section.main div[data-testid="stAlert"] *,
            section.main div[data-testid="stInfo"] *,
            section.main div[data-testid="stWarning"] *,
            section.main div[data-testid="stSuccess"] * {
                color: #F8FAFC !important;
                opacity: 1 !important;
            }

            /* Selectbox/button label tetap jelas */
            section.main label,
            section.main label *,
            section.main div[data-baseweb="select"] *,
            section.main button * {
                opacity: 1 !important;
            }
        
            /* =====================================================
               VISUALIZATION FULL WIDTH FINAL
               Menghilangkan ruang kosong kiri-kanan pada semua halaman
               visualisasi agar konten melebar rapi mengikuti layar.
               ===================================================== */

            .main .block-container,
            section.main .block-container,
            div[data-testid="stMainBlockContainer"],
            div[data-testid="stAppViewContainer"] .block-container {
                width: 100% !important;
                max-width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 0.8rem !important;
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
                align-items: stretch !important;
            }

            section.main div[data-testid="column"] {
                width: 100% !important;
                min-width: 0 !important;
                box-sizing: border-box !important;
            }

            /* Header/judul halaman visualisasi dibuat full dan tidak terpusat sempit */
            section.main .section-title,
            section.main .section-title *,
            section.main .subsection-title,
            section.main .subsection-title * {
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }

            /* Selectbox dan uploader area dibuat mengikuti lebar halaman */
            section.main div[data-testid="stSelectbox"],
            section.main div[data-testid="stSelectbox"] > div,
            section.main div[data-baseweb="select"],
            section.main div[data-testid="stFileUploader"],
            section.main div[data-testid="stFileUploader"] > div {
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }

            /* Plotly chart memenuhi area kolomnya */
            section.main div[data-testid="stPlotlyChart"],
            section.main div[data-testid="stPlotlyChart"] > div,
            section.main div[data-testid="stPlotlyChart"] .js-plotly-plot,
            section.main div[data-testid="stPlotlyChart"] .plot-container,
            section.main div[data-testid="stPlotlyChart"] .svg-container {
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }

            /* Card interpretasi dan ringkasan visual memenuhi lebar */
            section.main .interpretation-box,
            section.main .interpretation-card,
            section.main .insight-box,
            section.main .summary-box,
            section.main .analysis-box,
            section.main .interpretasi-box {
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
            }

            /* Jarak antar elemen dibuat lebih padat dan rapi */
            section.main div[data-testid="stButton"] {
                margin-top: 0.35rem !important;
                margin-bottom: 0.45rem !important;
            }

            section.main hr {
                margin-top: 0.65rem !important;
                margin-bottom: 0.65rem !important;
            }

</style>
        """,
        unsafe_allow_html=True
    )


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



def show_numerical_visualization_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    inject_visual_text_readability_css()
    st.markdown('<div class="section-title">📈 Numerical Visualization</div>', unsafe_allow_html=True)

    if numeric_cols:
        selected_num = st.selectbox("Pilih Variabel Numerik", numeric_cols)

        fig_hist = viz.histogram(df, selected_num)
        fig_box = viz.boxplot(df, selected_num)
        fig_density = viz.density_plot(df, selected_num)
        fig_qq = viz.qq_plot(df, selected_num)
        fig_violin = viz.violin_plot(df, selected_num)

        fig_hist, fig_box, fig_density, fig_qq, fig_violin = apply_pastel_to_figures(
            fig_hist,
            fig_box,
            fig_density,
            fig_qq,
            fig_violin
        )

        if st.button("💾 Save Visualization", key="save_numerical"):
            try:
                figures = {
                    f"histogram_{selected_num}": fig_hist,
                    f"boxplot_{selected_num}": fig_box,
                    f"density_{selected_num}": fig_density,
                    f"qqplot_{selected_num}": fig_qq,
                    f"violin_{selected_num}": fig_violin
                }

                save_visualizations(
                    figures,
                    "outputs/charts/numerical"
                )

                st.toast("Semua visualisasi Numerical berhasil disimpan (PNG + HTML)", icon="✅")

            except Exception:
                st.toast("Gagal menyimpan visualisasi Numerical", icon="❌")

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                fig_hist,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_histogram(df, selected_num), unsafe_allow_html=True)

        with col2:
            st.plotly_chart(
                fig_box,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                "responsive": True
            }
        )
            st.markdown(interpret_boxplot(df, selected_num), unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            st.plotly_chart(
                fig_density,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_density(df, selected_num), unsafe_allow_html=True)

        with col4:
            st.plotly_chart(
                fig_qq,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_qq_plot(df, selected_num), unsafe_allow_html=True)

        st.plotly_chart(
            fig_violin,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
        }
    )
        st.markdown(interpret_violin(df, selected_num), unsafe_allow_html=True)

        render_summary_interpretation(
            "Ringkasan Numerical Analysis",
            summary_numerical_interpretation(df, selected_num),
            "Ringkasan gabungan dari histogram, boxplot, density plot, QQ plot, dan violin plot."
        )

    else:
        st.warning("Tidak ada variabel numerik.")




def show_categorical_visualization_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    inject_visual_text_readability_css()
    st.markdown('<div class="section-title">📊 Categorical Visualization</div>', unsafe_allow_html=True)

    if categorical_cols:
        selected_cat = st.selectbox("Pilih Variabel Kategorik", categorical_cols)

        fig_bar = viz.bar_chart(df, selected_cat)
        fig_pie = viz.pie_chart(df, selected_cat)
        fig_count = viz.count_plot(df, selected_cat)
        fig_pareto = viz.pareto_chart(df, selected_cat)

        fig_bar, fig_pie, fig_count, fig_pareto = apply_pastel_to_figures(
            fig_bar,
            fig_pie,
            fig_count,
            fig_pareto
        )

        fig_bar, fig_pie, fig_count, fig_pareto = compact_categorical_chart_space(
            fig_bar,
            fig_pie,
            fig_count,
            fig_pareto
        )

        if st.button("💾 Save Visualization", key="save_categorical"):
            try:
                figures = {
                    f"bar_chart_{selected_cat}": fig_bar,
                    f"pie_chart_{selected_cat}": fig_pie,
                    f"count_plot_{selected_cat}": fig_count,
                    f"pareto_chart_{selected_cat}": fig_pareto
                }

                save_visualizations(
                    figures,
                    "outputs/charts/categorical"
                )

                st.toast("Semua visualisasi Categorical berhasil disimpan (PNG + HTML)", icon="✅")

            except Exception:
                st.toast("Gagal menyimpan visualisasi Categorical", icon="❌")

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                fig_bar,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_bar_chart(df, selected_cat), unsafe_allow_html=True)

        with col2:
            st.plotly_chart(
                fig_pie,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
                }
            )           
            st.markdown(interpret_pie_chart(df, selected_cat), unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            st.plotly_chart(
                fig_count,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
)
            st.markdown(interpret_count_plot(df, selected_cat), unsafe_allow_html=True)

        with col4:
            st.plotly_chart(
                fig_pareto,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
                }
            )
            st.markdown(interpret_pareto(df, selected_cat), unsafe_allow_html=True)

        render_summary_interpretation(
            "Ringkasan Categorical Analysis",
            summary_categorical_interpretation(df, selected_cat),
            "Ringkasan gabungan dari bar chart, pie chart, count plot, dan pareto chart."
        )

    else:
        st.warning("Tidak ada variabel kategorik.")




def show_bivariate_multivariate_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    inject_visual_text_readability_css()
    st.markdown('<div class="section-title">🔗 Bivariate & Multivariate Analysis</div>', unsafe_allow_html=True)

    def clean_money_number(series):
        cleaned = (
            series.astype(str)
            .str.replace("Rp", "", regex=False)
            .str.replace("rp", "", regex=False)
            .str.replace("IDR", "", regex=False)
            .str.replace("idr", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace("%", "", regex=False)
        )

        cleaned = cleaned.str.replace(".", "", regex=False)
        cleaned = cleaned.str.replace(",", ".", regex=False)

        return pd.to_numeric(cleaned, errors="coerce")

    def clean_numeric_dataframe(data, cols):
        temp = data.copy()

        valid_cols = []

        for col in cols:
            if col in temp.columns:
                temp[col] = clean_money_number(temp[col])

                if temp[col].notna().sum() >= 2:
                    valid_cols.append(col)

        return temp, valid_cols

    if len(numeric_cols) >= 2:
        clean_all_df, valid_numeric_cols = clean_numeric_dataframe(
            df,
            numeric_cols
        )

        if len(valid_numeric_cols) < 2:
            st.warning("⚠ Data numerik tidak cukup untuk Bivariate & Multivariate Analysis.")
            st.info(
                """
                Pastikan dataset memiliki minimal 2 kolom numerik yang valid.

                Contoh:
                • quantity
                • unit_price
                • gross_sales
                • shipping_cost
                • customer_rating
                """
            )
            st.stop()

        x_col = st.selectbox("X Variable", valid_numeric_cols)
        y_col = st.selectbox("Y Variable", valid_numeric_cols, index=1)

        clean_bivar_df = clean_all_df.dropna(subset=[x_col, y_col])

        if clean_bivar_df.empty or len(clean_bivar_df) < 2:
            st.warning("⚠ Data numerik tidak cukup untuk scatter/regression plot.")
            st.stop()

        fig_scatter = viz.scatter_plot(clean_bivar_df, x_col, y_col)
        fig_regression = viz.regression_plot(clean_bivar_df, x_col, y_col)
        fig_heatmap = viz.correlation_heatmap(clean_all_df, valid_numeric_cols)
        fig_pair = viz.pair_plot(clean_all_df, valid_numeric_cols)

        fig_scatter, fig_regression, fig_heatmap, fig_pair = apply_pastel_to_figures(
            fig_scatter,
            fig_regression,
            fig_heatmap,
            fig_pair
        )

        figures = {
            f"scatter_{x_col}_vs_{y_col}": fig_scatter,
            f"regression_{x_col}_vs_{y_col}": fig_regression,
            "correlation_heatmap": fig_heatmap,
            "pair_plot": fig_pair
        }

        if len(valid_numeric_cols) >= 3:
            size_col = st.selectbox("Bubble Size Variable", valid_numeric_cols, index=2)

            clean_bubble_df = clean_all_df.dropna(
                subset=[x_col, y_col, size_col]
            )

            fig_bubble = viz.bubble_chart(
                clean_bubble_df,
                x_col,
                y_col,
                size_col
            )
            fig_bubble = apply_pastel_theme(fig_bubble, 4)

            figures[f"bubble_{x_col}_{y_col}_size_{size_col}"] = fig_bubble

        else:
            size_col = None
            fig_bubble = None

        if st.button("💾 Save Visualization", key="save_bivariate"):
            try:
                save_visualizations(
                    figures,
                    "outputs/charts/bivariate"
                )

                st.toast("Semua visualisasi Bivariate berhasil disimpan (PNG + HTML)", icon="✅")

            except Exception:
                st.toast("Gagal menyimpan visualisasi Bivariate", icon="❌")

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                fig_scatter,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_scatter_plot(clean_bivar_df, x_col, y_col), unsafe_allow_html=True)

        with col2:
            st.plotly_chart(
                fig_regression,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_regression_plot(clean_bivar_df, x_col, y_col), unsafe_allow_html=True)

        st.subheader("Correlation Heatmap")
        st.plotly_chart(
            fig_heatmap,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )
        st.markdown(interpret_heatmap(clean_all_df, valid_numeric_cols), unsafe_allow_html=True)

        st.subheader("Pair Plot")
        st.plotly_chart(
            fig_pair,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )
        st.markdown(interpret_pair_plot(clean_all_df, valid_numeric_cols), unsafe_allow_html=True)

        if fig_bubble is not None:
            st.subheader("Bubble Chart")
            st.plotly_chart(
                fig_bubble,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
                }
            )
            st.markdown(interpret_bubble_chart(clean_bubble_df, x_col, y_col, size_col), unsafe_allow_html=True)
        else:
            st.info("Bubble Chart membutuhkan minimal 3 variabel numerik.")

    else:
        st.warning("Minimal harus ada 2 variabel numerik.")




def show_categorical_vs_numerical_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    inject_visual_text_readability_css()
    st.markdown('<div class="section-title">📌 Categorical vs Numerical Analysis</div>', unsafe_allow_html=True)

    if categorical_cols and numeric_cols:
        cat_col = st.selectbox("Categorical Variable", categorical_cols)
        num_col = st.selectbox("Numerical Variable", numeric_cols)

        fig_box_cat = viz.boxplot_by_category(df, cat_col, num_col)
        fig_violin_cat = viz.violin_by_category(df, cat_col, num_col)
        fig_grouped = viz.grouped_bar_chart(df, cat_col, num_col)
        fig_strip = viz.strip_plot(df, cat_col, num_col)

        fig_box_cat, fig_violin_cat, fig_grouped, fig_strip = apply_pastel_to_figures(
            fig_box_cat,
            fig_violin_cat,
            fig_grouped,
            fig_strip
        )

        fig_box_cat, fig_violin_cat, fig_grouped, fig_strip = compact_categorical_chart_space(
            fig_box_cat,
            fig_violin_cat,
            fig_grouped,
            fig_strip
        )

        if st.button("💾 Save Visualization", key="save_cat_num"):
            try:
                figures = {
                    f"boxplot_{num_col}_by_{cat_col}": fig_box_cat,
                    f"violin_{num_col}_by_{cat_col}": fig_violin_cat,
                    f"grouped_bar_{num_col}_by_{cat_col}": fig_grouped,
                    f"strip_plot_{num_col}_by_{cat_col}": fig_strip
                }

                save_visualizations(
                    figures,
                    "outputs/charts/categorical_numerical"
                )

                st.toast("Semua visualisasi Categorical vs Numerical berhasil disimpan (PNG + HTML)", icon="✅")

            except Exception:
                st.toast("Gagal menyimpan visualisasi Categorical vs Numerical", icon="❌")

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                fig_box_cat,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_boxplot_by_category(df, cat_col, num_col), unsafe_allow_html=True)

        with col2:
            st.plotly_chart(
                fig_violin_cat,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_violin_by_category(df, cat_col, num_col), unsafe_allow_html=True)

        col3, col4 = st.columns(2)

        with col3:
            st.plotly_chart(
                fig_grouped,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
            }
        )
            st.markdown(interpret_grouped_bar(df, cat_col, num_col), unsafe_allow_html=True)

        with col4:
            st.plotly_chart(
                fig_strip,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
                }
            )
            st.markdown(interpret_strip_plot(df, cat_col, num_col), unsafe_allow_html=True)

        st.markdown(interpret_category_numeric(df, cat_col, num_col), unsafe_allow_html=True)

    else:
        st.warning("Butuh variabel kategorik dan numerik.")




def show_time_series_page(df, file_name, file_ext, file_size, saved_file_path, numeric_cols, categorical_cols, date_cols, num_stats, cat_stats, insights, save_visualizations, render_summary_interpretation, calculate_health_score, get_health_label):
    inject_visual_text_readability_css()
    st.markdown('<div class="section-title">⏱️ Time Series Analytics</div>', unsafe_allow_html=True)

    if date_cols and numeric_cols:
        date_col = st.selectbox("Date Column", date_cols)
        value_col = st.selectbox("Value Column", numeric_cols)
        window = st.slider("Moving Average / Rolling Mean Window", 2, 30, 3)

        ts_check = ts.prepare_time_series_data(
            df,
            date_col,
            value_col
        )

        if ts_check.empty or len(ts_check) < 2:
            st.warning("⚠ Kolom yang dipilih belum memiliki data Date/Datetime yang valid.")
            st.info(
                """
                Time Series Analytics membutuhkan:
                • 1 kolom Date/Datetime valid, contoh: 2024-01-01
                • 1 kolom numerik, contoh: Sales, Revenue, Profit, atau total_bill

                Catatan:
                Kolom seperti day = Sun/Sat/Thur atau time = Lunch/Dinner
                termasuk kategori, bukan Date/Datetime.
                """
            )
            st.stop()

        fig_trend = ts.trend_line_chart(df, date_col, value_col)
        fig_time_series = ts.time_series_chart(df, date_col, value_col, window)

        fig_trend, fig_time_series = apply_pastel_to_figures(
            fig_trend,
            fig_time_series
        )

        if st.button("💾 Save Visualization", key="save_time_series"):
            try:
                figures = {
                    f"trend_line_{value_col}_by_{date_col}": fig_trend,
                    f"time_series_{value_col}_by_{date_col}": fig_time_series
                }

                save_visualizations(
                    figures,
                    "outputs/charts/time_series"
                )

                st.toast("Semua visualisasi Time Series berhasil disimpan (PNG + HTML)", icon="✅")

            except Exception:
                st.toast("Gagal menyimpan visualisasi Time Series", icon="❌")

        st.subheader("Trend Line")
        st.plotly_chart(
            fig_trend,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )

        st.subheader("Time Series Line Chart + Moving Average + Rolling Mean")
        st.plotly_chart(
            fig_time_series,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )

        render_summary_interpretation(
            "Ringkasan Time Series Analysis",
            summary_time_series_interpretation(df, date_col, value_col),
            "Ringkasan gabungan dari trend line, time series chart, moving average, dan rolling mean."
        )

    else:
        st.warning("⚠ No Date/Datetime column detected.")
        st.info(
            """
            Time Series Analytics hanya tersedia jika dataset memiliki
            variabel Date/Datetime dan variabel numerik.

            Fitur yang akan aktif:
            • Trend Line
            • Time Series Line Chart
            • Moving Average
            • Rolling Mean
            """
        )


