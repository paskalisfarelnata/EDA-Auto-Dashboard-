import os
import streamlit as st
import pandas as pd

from backend.data_loader import load_data


# =====================================================
# UPLOAD PAGE THEME - FINAL FIX
# Catatan:
# CSS sengaja TIDAK memakai f-string supaya tidak muncul error:
# NameError: name 'color' is not defined
# =====================================================
def inject_upload_page_css():
    st.markdown(
        """
        <style>
            .upload-page {
                display: flex !important;
                flex-direction: column !important;
                gap: 16px !important;
            }

            .upload-hero {
                background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 52%, #7c3aed 100%) !important;
                color: #ffffff !important;
                padding: 16px 20px !important;
                border-radius: 22px !important;
                box-shadow: 0 14px 34px rgba(37,99,235,0.24) !important;
                margin-bottom: 18px !important;
            }

            .upload-hero-title {
                color: #ffffff !important;
                font-size: 24px !important;
                font-weight: 1000 !important;
                margin-bottom: 4px !important;
            }

            .upload-hero-subtitle {
                color: #dbeafe !important;
                font-size: 13px !important;
                font-weight: 650 !important;
                line-height: 1.5 !important;
            }

            .upload-card {
                background: rgba(15, 23, 42, 0.92) !important;
                border: 1px solid rgba(96, 165, 250, 0.34) !important;
                border-radius: 20px !important;
                padding: 18px 20px !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.35) !important;
                color: #e2e8f0 !important;
                margin-bottom: 16px !important;
                min-height: 0 !important;
            }

            .upload-card-title {
                font-size: 16px !important;
                font-weight: 1000 !important;
                color: #f8fafc !important;
                margin-bottom: 8px !important;
            }

            .upload-desc {
                font-size: 13px !important;
                line-height: 1.65 !important;
                color: #e2e8f0 !important;
                font-weight: 650 !important;
            }

            .upload-guide-box {
                background: rgba(15, 23, 42, 0.92) !important;
                border: 1px solid rgba(96, 165, 250, 0.34) !important;
                border-left: 6px solid #06b6d4 !important;
                border-radius: 20px !important;
                padding: 18px 20px !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.35) !important;
                color: #e2e8f0 !important;
                margin-bottom: 16px !important;
            }

            .upload-guide-title {
                color: #f8fafc !important;
                font-size: 16px !important;
                font-weight: 1000 !important;
                margin-bottom: 10px !important;
            }

            .upload-guide-item {
                color: #e2e8f0 !important;
                display: flex !important;
                gap: 9px !important;
                align-items: flex-start !important;
                font-size: 12.5px !important;
                font-weight: 700 !important;
                line-height: 1.5 !important;
                margin: 8px 0 !important;
            }

            .upload-guide-item span:first-child {
                color: #34d399 !important;
                font-weight: 1000 !important;
            }

            .upload-kpi {
                background: rgba(15, 23, 42, 0.88) !important;
                border: 1px solid rgba(96, 165, 250, 0.34) !important;
                border-radius: 18px !important;
                padding: 14px 15px !important;
                min-height: 106px !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.35) !important;
                color: #e2e8f0 !important;
                margin-bottom: 12px !important;
            }

            .upload-kpi-icon {
                font-size: 21px !important;
                margin-bottom: 5px !important;
            }

            .upload-kpi-label {
                font-size: 12px !important;
                font-weight: 900 !important;
                color: #cbd5e1 !important;
            }

            .upload-kpi-value {
                font-size: 26px !important;
                font-weight: 1000 !important;
                color: #f8fafc !important;
                margin-top: 3px !important;
                line-height: 1.15 !important;
                word-break: break-word !important;
            }

            .upload-success-box {
                background: rgba(20,83,45,0.34) !important;
                border: 1px solid rgba(34,197,94,0.28) !important;
                border-left: 6px solid #22c55e !important;
                border-radius: 18px !important;
                padding: 13px 15px !important;
                font-size: 13px !important;
                font-weight: 750 !important;
                color: #bbf7d0 !important;
                margin: 16px 0 !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.35) !important;
            }

            .upload-success-box * {
                color: #bbf7d0 !important;
            }

            .upload-path {
                font-size: 12px !important;
                color: #e2e8f0 !important;
                background: rgba(15, 23, 42, 0.92) !important;
                padding: 9px 11px !important;
                border-radius: 13px !important;
                margin-top: 12px !important;
                margin-bottom: 16px !important;
                border: 1px dashed rgba(96, 165, 250, 0.34) !important;
                word-break: break-all !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.35) !important;
            }

            [data-testid="stFileUploader"] {
                background: rgba(15, 23, 42, 0.92) !important;
                border: 1px dashed rgba(96, 165, 250, 0.34) !important;
                border-radius: 20px !important;
                padding: 16px !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.35) !important;
                margin-bottom: 16px !important;
            }

            [data-testid="stFileUploader"] * {
                color: #e2e8f0 !important;
            }

            [data-testid="stFileUploaderDropzone"] {
                background: rgba(15, 23, 42, 0.88) !important;
                border: 1px dashed rgba(96, 165, 250, 0.34) !important;
                border-radius: 18px !important;
                padding: 22px !important;
            }

            [data-testid="stFileUploaderDropzone"] * {
                color: #e2e8f0 !important;
            }

            [data-testid="stFileUploader"] label,
            [data-testid="stFileUploader"] label *,
            [data-testid="stFileUploaderDropzone"] button,
            [data-testid="stFileUploaderDropzone"] button * {
                color: #ffffff !important;
            }

            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                border-radius: 15px !important;
                overflow: hidden !important;
                border: 1px solid rgba(96, 165, 250, 0.34) !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.35) !important;
                margin-top: 10px !important;
            }

            div[data-testid="stButton"] > button,
            div[data-testid="stButton"] > button * {
                color: #ffffff !important;
            }

            .section-title,
            .section-title * {
                color: #ffffff !important;
            }

            [data-testid="stMarkdownContainer"] *,
            .stMarkdown * {
                color: #e2e8f0 !important;
            }

            div[data-testid="stHorizontalBlock"] {
                gap: 1rem !important;
            }

            div[data-testid="stVerticalBlock"] {
                gap: .85rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


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


def show_upload_page():
    inject_upload_page_css()

    st.markdown(
        '<div class="section-title">📁 Upload Data</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="upload-hero">
            <div class="upload-hero-title">📤 Upload Dataset Center</div>
            <div class="upload-hero-subtitle">
                Pilih dataset yang akan dianalisis. Setelah upload berhasil, sistem akan membaca data,
                menyimpan file, mendeteksi format, dan menyiapkan dashboard otomatis.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    upload_col, guide_col = st.columns([1.35, 1], gap="medium")

    with upload_col:
        st.markdown(
            """
            <div class="upload-card">
                <div class="upload-card-title">📤 Upload File Area</div>
                <div class="upload-desc">
                    Pilih dataset CSV, XLSX, atau TXT. Pastikan file memiliki nama kolom yang jelas supaya
                    proses EDA, statistik, visualisasi, insight, dan reporting berjalan rapi.
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

    with guide_col:
        st.markdown(
            """
            <div class="upload-guide-box">
                <div class="upload-guide-title">💡 Upload Guide</div>
                <div class="upload-guide-item"><span>✓</span><div>Format yang didukung: CSV, XLSX, dan TXT.</div></div>
                <div class="upload-guide-item"><span>✓</span><div>File otomatis disimpan ke folder <b>data/raw</b>.</div></div>
                <div class="upload-guide-item"><span>✓</span><div>Setelah upload, dashboard akan membaca rows, columns, format, dan ukuran file.</div></div>
                <div class="upload-guide-item"><span>✓</span><div>Lanjutkan ke Dashboard, Dataset Information, atau Data Cleaning.</div></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if uploaded_file is not None:
        try:
            os.makedirs("data/raw", exist_ok=True)

            save_path = os.path.join("data", "raw", uploaded_file.name)

            with open(save_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

            uploaded_file.seek(0)

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
                ("💾", "File Size", _safe_file_size(uploaded_file.size))
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

            st.dataframe(df.head(10), use_container_width=True, height=300)

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
