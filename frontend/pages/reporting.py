import os
import re
import pandas as pd
import streamlit as st

from backend.export_report import export_pdf, export_html, export_excel, export_csv


# =========================================================
# HELPER
# =========================================================

def make_output_base_name(file_name):
    if not file_name:
        return "dataset"

    base_name = os.path.splitext(str(file_name))[0]
    base_name = base_name.lower()
    base_name = re.sub(r"[^a-zA-Z0-9_]+", "_", base_name)
    base_name = re.sub(r"_+", "_", base_name)

    return base_name.strip("_") or "dataset"


def normalize_insights(insights):
    if insights is None:
        return ["Insight otomatis belum tersedia."]

    if isinstance(insights, pd.DataFrame):
        if insights.empty:
            return ["Insight otomatis belum tersedia."]

        result = []
        for _, row in insights.iterrows():
            text = " | ".join([str(v) for v in row.values if pd.notna(v)])
            if text.strip():
                result.append(text)

        return result if result else ["Insight otomatis belum tersedia."]

    if isinstance(insights, pd.Series):
        result = [str(v) for v in insights.dropna().tolist()]
        return result if result else ["Insight otomatis belum tersedia."]

    if isinstance(insights, (list, tuple)):
        result = [str(v) for v in insights if v is not None and str(v).strip()]
        return result if result else ["Insight otomatis belum tersedia."]

    if isinstance(insights, str):
        return [insights] if insights.strip() else ["Insight otomatis belum tersedia."]

    return [str(insights)]


def dataset_available(df):
    return isinstance(df, pd.DataFrame) and not df.empty


def ensure_output_folder(folder_path):
    os.makedirs(folder_path, exist_ok=True)


# =========================================================
# REPORTING PAGE DARK THEME
# =========================================================
def inject_reporting_page_css():
    st.markdown(
        """
        <style>
            .report-card {
                background: linear-gradient(135deg, rgba(15, 23, 42, .96), rgba(17, 24, 39, .94)) !important;
                border: 1px solid rgba(103, 232, 249, .22) !important;
                border-radius: 20px !important;
                padding: 18px 20px !important;
                box-shadow: 0 16px 38px rgba(0, 0, 0, .28) !important;
                margin-bottom: 16px !important;
                color: #EAF6FF !important;
            }
            .report-card-title {
                color: #FFFFFF !important;
                font-size: 17px !important;
                font-weight: 1000 !important;
                margin-bottom: 8px !important;
            }
            .report-card-desc {
                color: #DFF6FF !important;
                font-size: 13px !important;
                line-height: 1.65 !important;
                font-weight: 650 !important;
            }
            .report-format-box {
                background: rgba(15, 23, 42, .92) !important;
                border: 1px solid rgba(96, 165, 250, .28) !important;
                border-left: 6px solid #38BDF8 !important;
                border-radius: 18px !important;
                padding: 14px 16px !important;
                margin-bottom: 14px !important;
                color: #EAF6FF !important;
                box-shadow: 0 12px 30px rgba(0, 0, 0, .22) !important;
            }
            .report-format-box * { color: #EAF6FF !important; }
            section.main div[data-testid="stMarkdownContainer"],
            section.main div[data-testid="stMarkdownContainer"] *,
            section.main p,
            section.main li,
            section.main label,
            section.main span {
                color: #EAF6FF !important;
                opacity: 1 !important;
            }
            section.main h1, section.main h2, section.main h3, section.main h4,
            .section-title, .section-title * {
                color: #FFFFFF !important;
                opacity: 1 !important;
            }
            div[data-testid="stAlert"] *,
            div[data-testid="stInfo"] *,
            div[data-testid="stWarning"] *,
            div[data-testid="stSuccess"] * {
                color: #F8FAFC !important;
                opacity: 1 !important;
            }
            div[data-testid="stButton"] > button,
            div[data-testid="stButton"] > button *,
            div[data-testid="stDownloadButton"] > button,
            div[data-testid="stDownloadButton"] > button * {
                color: #FFFFFF !important;
                font-weight: 900 !important;
            }
            code, pre {
                color: #EAF6FF !important;
                background: rgba(15,23,42,.96) !important;
                border: 1px solid rgba(103,232,249,.18) !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# PDF REPORT PAGE
# =========================================================

def show_download_pdf_page(
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
    inject_reporting_page_css()
    st.markdown(
        '<div class="section-title">📄 Download Report PDF</div>',
        unsafe_allow_html=True
    )

    st.info("Klik tombol di bawah untuk membuat dan mengunduh report PDF.")

    if not dataset_available(df):
        st.warning("Dataset belum tersedia. Silakan upload dataset terlebih dahulu.")
        return

    output_base = make_output_base_name(file_name)
    pdf_filename = f"auto_eda_{output_base}_report.pdf"

    if st.button("📄 Generate PDF Report", use_container_width=True):
        try:
            clean_insights = normalize_insights(insights)

            pdf_data = export_pdf(
                clean_insights,
                df,
                num_stats,
                cat_stats
            )

            ensure_output_folder("outputs/reports")
            pdf_path = os.path.join("outputs", "reports", pdf_filename)

            with open(pdf_path, "wb") as file:
                file.write(pdf_data)

            st.success(f"PDF berhasil dibuat: {pdf_filename}")

            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_data,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )

            st.toast("PDF berhasil dibuat dan siap diunduh", icon="✅")

        except Exception as e:
            st.error("PDF report belum bisa dibuat.")
            st.code(str(e))
            st.toast("PDF gagal dibuat", icon="❌")


# =========================================================
# HTML REPORT PAGE
# =========================================================

def show_download_html_page(
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
    inject_reporting_page_css()
    st.markdown(
        '<div class="section-title">🌐 Download HTML Dashboard</div>',
        unsafe_allow_html=True
    )

    st.info("Klik tombol di bawah untuk membuat dan mengunduh report HTML.")

    if not dataset_available(df):
        st.warning("Dataset belum tersedia. Silakan upload dataset terlebih dahulu.")
        return

    output_base = make_output_base_name(file_name)
    html_filename = f"auto_eda_{output_base}_dashboard.html"

    if st.button("🌐 Generate HTML Report", use_container_width=True):
        try:
            clean_insights = normalize_insights(insights)

            html_data = export_html(
                clean_insights,
                df,
                num_stats,
                cat_stats
            )

            ensure_output_folder("outputs/reports")
            html_path = os.path.join("outputs", "reports", html_filename)

            with open(html_path, "w", encoding="utf-8") as file:
                file.write(html_data)

            st.success(f"HTML berhasil dibuat: {html_filename}")

            st.download_button(
                label="⬇️ Download HTML",
                data=html_data,
                file_name=html_filename,
                mime="text/html",
                use_container_width=True
            )

            st.toast("HTML berhasil dibuat dan siap diunduh", icon="✅")

        except Exception as e:
            st.error("HTML report belum bisa dibuat.")
            st.code(str(e))
            st.toast("HTML gagal dibuat", icon="❌")


# =========================================================
# EXCEL / CSV EXPORT PAGE
# =========================================================

def show_export_excel_csv_page(
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
    inject_reporting_page_css()
    st.markdown(
        '<div class="section-title">📊 Export Result to Excel / CSV</div>',
        unsafe_allow_html=True
    )

    if not dataset_available(df):
        st.warning("Dataset belum tersedia. Silakan upload dataset terlebih dahulu.")
        return

    output_base = make_output_base_name(file_name)

    csv_filename = f"auto_eda_{output_base}_result.csv"
    excel_filename = f"auto_eda_{output_base}_result.xlsx"

    col1, col2 = st.columns(2)

    with col1:
        try:
            csv_data = export_csv(df)

            ensure_output_folder("outputs/exported_files")
            csv_path = os.path.join("outputs", "exported_files", csv_filename)

            with open(csv_path, "wb") as file:
                file.write(csv_data)

            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
                use_container_width=True
            )

        except Exception as e:
            st.error("CSV gagal dibuat.")
            st.code(str(e))

    with col2:
        try:
            clean_insights = normalize_insights(insights)

            excel_data = export_excel(
                df,
                num_stats,
                cat_stats,
                clean_insights
            )

            ensure_output_folder("outputs/exported_files")
            excel_path = os.path.join("outputs", "exported_files", excel_filename)

            with open(excel_path, "wb") as file:
                file.write(excel_data)

            st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name=excel_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        except Exception as e:
            st.error("Excel gagal dibuat.")
            st.code(str(e))
