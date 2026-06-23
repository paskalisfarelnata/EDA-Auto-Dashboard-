
import os
import re
import io
import streamlit as st
import pandas as pd
import numpy as np

from backend.preprocessing import cleaning_summary, remove_duplicates
from backend.table_utils import show_table


# =====================================================
# ADVANCED DATA CLEANING PAGE - DARK PERMANENT
# =====================================================

def _safe_container(border=True):
    try:
        return st.container(border=border)
    except TypeError:
        return st.container()


def _safe_file_base(file_name):
    if not file_name:
        return "dataset"
    base = os.path.splitext(str(file_name))[0].lower()
    base = re.sub(r"[^a-zA-Z0-9_]+", "_", base)
    base = re.sub(r"_+", "_", base).strip("_")
    return base or "dataset"


def _safe_to_excel_bytes(df, summary_df=None, log_df=None):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Cleaned Data")
        if summary_df is not None:
            summary_df.to_excel(writer, index=False, sheet_name="Cleaning Summary")
        if log_df is not None:
            log_df.to_excel(writer, index=False, sheet_name="Cleaning Log")
    return output.getvalue()


def _detect_outlier_count(df, numeric_cols):
    total = 0
    detail = []
    for col in numeric_cols:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        valid = s.dropna()
        if valid.empty:
            continue

        q1 = valid.quantile(0.25)
        q3 = valid.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0 or pd.isna(iqr):
            count = 0
        else:
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            count = int(((s < lower) | (s > upper)).sum())

        total += count
        detail.append({
            "Column": col,
            "Outlier Count": count
        })

    return total, pd.DataFrame(detail)


def _fill_missing_values(df, numeric_cols, categorical_cols, method):
    clean_df = df.copy()
    log = []

    missing_before = int(clean_df.isna().sum().sum())

    if method == "Drop Missing Rows":
        rows_before = len(clean_df)
        clean_df = clean_df.dropna()
        log.append({
            "Action": "Missing Value Handling",
            "Method": "Drop Missing Rows",
            "Result": f"{rows_before - len(clean_df)} rows removed"
        })

    else:
        for col in clean_df.columns:
            missing_count = int(clean_df[col].isna().sum())
            if missing_count == 0:
                continue

            if col in numeric_cols:
                numeric_series = pd.to_numeric(clean_df[col], errors="coerce")

                if method == "Fill Mean":
                    fill_value = numeric_series.mean()
                elif method == "Fill Median":
                    fill_value = numeric_series.median()
                else:
                    fill_value = numeric_series.median()

                if pd.isna(fill_value):
                    fill_value = 0

                clean_df[col] = numeric_series.fillna(fill_value)
                log.append({
                    "Action": "Missing Value Handling",
                    "Method": method,
                    "Result": f"{missing_count} missing values filled in {col}"
                })

            else:
                mode_value = clean_df[col].mode(dropna=True)
                fill_value = mode_value.iloc[0] if not mode_value.empty else "Unknown"
                clean_df[col] = clean_df[col].fillna(fill_value)
                log.append({
                    "Action": "Missing Value Handling",
                    "Method": "Fill Mode",
                    "Result": f"{missing_count} missing values filled in {col}"
                })

    missing_after = int(clean_df.isna().sum().sum())
    return clean_df, missing_before, missing_after, log


def _remove_duplicate_rows(df):
    before = int(df.duplicated().sum())
    try:
        clean_df = remove_duplicates(df)
    except Exception:
        clean_df = df.drop_duplicates()
    after = int(clean_df.duplicated().sum())

    log = [{
        "Action": "Duplicate Removal",
        "Method": "Drop Duplicates",
        "Result": f"{before - after} duplicate rows removed"
    }]
    return clean_df, before, after, log


def _remove_outliers_iqr(df, numeric_cols):
    clean_df = df.copy()
    before_total, before_detail = _detect_outlier_count(clean_df, numeric_cols)

    if before_total == 0:
        log = [{
            "Action": "Outlier Handling",
            "Method": "IQR Method",
            "Result": "No outlier detected"
        }]
        return clean_df, before_total, 0, before_detail, before_detail, log

    mask_keep = pd.Series(True, index=clean_df.index)

    for col in numeric_cols:
        if col not in clean_df.columns:
            continue

        s = pd.to_numeric(clean_df[col], errors="coerce")
        valid = s.dropna()
        if valid.empty:
            continue

        q1 = valid.quantile(0.25)
        q3 = valid.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0 or pd.isna(iqr):
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        # Missing value tetap dipertahankan, outlier saja yang dibuang
        col_keep = s.isna() | ((s >= lower) & (s <= upper))
        mask_keep = mask_keep & col_keep

    rows_before = len(clean_df)
    clean_df = clean_df[mask_keep].copy()
    after_total, after_detail = _detect_outlier_count(clean_df, numeric_cols)

    log = [{
        "Action": "Outlier Handling",
        "Method": "IQR Method",
        "Result": f"{rows_before - len(clean_df)} rows removed based on outlier rule"
    }]
    return clean_df, before_total, after_total, before_detail, after_detail, log


def _clean_string_columns(df, categorical_cols):
    clean_df = df.copy()
    changed_values = 0

    for col in categorical_cols:
        if col not in clean_df.columns:
            continue

        before = clean_df[col].astype(str)
        after = (
            before
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

        changed_values += int((before != after).sum())
        clean_df[col] = after

    log = [{
        "Action": "String Cleaning",
        "Method": "Trim Spaces + Normalize Spaces",
        "Result": f"{changed_values} text values standardized"
    }]

    return clean_df, changed_values, log


def _correct_data_types(df):
    clean_df = df.copy()
    changes = []

    for col in clean_df.columns:
        before_type = str(clean_df[col].dtype)

        if before_type == "object":
            # coba convert numeric
            raw = clean_df[col].astype(str).str.strip()
            numeric_candidate = (
                raw
                .str.replace("Rp", "", regex=False)
                .str.replace("IDR", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace("%", "", regex=False)
            )
            numeric_candidate = numeric_candidate.str.replace(".", "", regex=False)
            numeric_candidate = numeric_candidate.str.replace(",", ".", regex=False)
            numeric_series = pd.to_numeric(numeric_candidate, errors="coerce")

            numeric_valid_ratio = numeric_series.notna().mean()

            # coba convert datetime
            datetime_series = pd.to_datetime(clean_df[col], errors="coerce")
            datetime_valid_ratio = datetime_series.notna().mean()

            if numeric_valid_ratio >= 0.80:
                clean_df[col] = numeric_series
            elif datetime_valid_ratio >= 0.80:
                clean_df[col] = datetime_series

        after_type = str(clean_df[col].dtype)
        if before_type != after_type:
            changes.append({
                "Column": col,
                "Before Type": before_type,
                "After Type": after_type
            })

    log = [{
        "Action": "Data Type Correction",
        "Method": "Auto Detect Numeric/Datetime",
        "Result": f"{len(changes)} columns converted"
    }]

    return clean_df, pd.DataFrame(changes), log


def _save_cleaned_file(df, file_name, cleaning_tag, summary_df=None, log_df=None):
    os.makedirs("data/processed", exist_ok=True)

    base = _safe_file_base(file_name)
    csv_name = f"cleaned_{cleaning_tag}_{base}.csv"
    xlsx_name = f"cleaned_{cleaning_tag}_{base}.xlsx"

    csv_path = os.path.join("data", "processed", csv_name)
    xlsx_path = os.path.join("data", "processed", xlsx_name)

    df.to_csv(csv_path, index=False)

    excel_bytes = _safe_to_excel_bytes(df, summary_df=summary_df, log_df=log_df)
    with open(xlsx_path, "wb") as f:
        f.write(excel_bytes)

    return csv_path, xlsx_path, csv_name, xlsx_name, excel_bytes


def _make_summary_table(before_df, after_df, numeric_cols):
    before_outlier, _ = _detect_outlier_count(before_df, numeric_cols)
    after_outlier, _ = _detect_outlier_count(after_df, numeric_cols)

    return pd.DataFrame({
        "Metric": [
            "Total Rows",
            "Total Columns",
            "Missing Values",
            "Duplicate Rows",
            "Outliers Detected"
        ],
        "Before": [
            before_df.shape[0],
            before_df.shape[1],
            int(before_df.isna().sum().sum()),
            int(before_df.duplicated().sum()),
            before_outlier
        ],
        "After": [
            after_df.shape[0],
            after_df.shape[1],
            int(after_df.isna().sum().sum()),
            int(after_df.duplicated().sum()),
            after_outlier
        ]
    })


def inject_cleaning_css():
    st.markdown(
        """
        <style>
            .clean-hero {
                background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 52%, #7c3aed 100%) !important;
                color: #ffffff !important;
                padding: 16px 20px !important;
                border-radius: 22px !important;
                box-shadow: 0 14px 34px rgba(37, 99, 235, 0.28) !important;
                margin-bottom: 18px !important;
                border: 1px solid rgba(147,197,253,.30) !important;
            }

            .clean-title {
                font-size: 24px !important;
                font-weight: 1000 !important;
                color: #ffffff !important;
                margin-bottom: 4px !important;
            }

            .clean-subtitle {
                font-size: 13px !important;
                color: #dbeafe !important;
                font-weight: 650 !important;
                line-height: 1.5 !important;
            }

            .clean-card,
            .clean-kpi,
            .clean-panel {
                background: rgba(15, 23, 42, 0.96) !important;
                border: 1px solid rgba(96,165,250,.34) !important;
                border-radius: 20px !important;
                box-shadow: 0 14px 34px rgba(0,0,0,.35) !important;
                color: #e2e8f0 !important;
                padding: 16px 18px !important;
                margin-bottom: 16px !important;
            }

            .clean-kpi {
                min-height: 112px !important;
                padding: 15px 16px !important;
            }

            .clean-kpi-icon {
                font-size: 22px !important;
                margin-bottom: 6px !important;
            }

            .clean-kpi-label {
                font-size: 12px !important;
                font-weight: 900 !important;
                color: #cbd5e1 !important;
            }

            .clean-kpi-value {
                font-size: 31px !important;
                font-weight: 1000 !important;
                color: #ffffff !important;
                margin-top: 3px !important;
                line-height: 1.1 !important;
            }

            .clean-card-title {
                font-size: 15.5px !important;
                font-weight: 1000 !important;
                color: #ffffff !important;
                margin-bottom: 10px !important;
            }

            .clean-desc {
                font-size: 13px !important;
                color: #e2e8f0 !important;
                line-height: 1.65 !important;
                font-weight: 650 !important;
            }

            .clean-note,
            .clean-path {
                background: rgba(37, 99, 235, 0.16) !important;
                color: #e2e8f0 !important;
                border-left: 5px solid #3b82f6 !important;
                border-radius: 13px !important;
                padding: 9px 12px !important;
                font-size: 12px !important;
                font-weight: 750 !important;
                margin-top: 12px !important;
            }

            .clean-method-badge {
                display: inline-block !important;
                padding: 5px 10px !important;
                border-radius: 999px !important;
                background: rgba(34,211,238,.13) !important;
                border: 1px solid rgba(34,211,238,.30) !important;
                color: #cffafe !important;
                font-weight: 900 !important;
                font-size: 12px !important;
                margin-right: 6px !important;
                margin-bottom: 6px !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"],
            div[data-testid="stFileUploader"],
            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                background: rgba(15, 23, 42, 0.96) !important;
                border-color: rgba(96,165,250,.34) !important;
                color: #f8fafc !important;
            }

            [data-testid="stMarkdownContainer"] *,
            .stMarkdown *,
            .clean-card *,
            .clean-panel *,
            .clean-kpi * {
                color: #e2e8f0 !important;
                opacity: 1 !important;
                filter: none !important;
            }

            .section-title,
            .section-title *,
            .clean-title,
            .clean-card-title,
            .clean-kpi-value,
            .stButton > button,
            .stButton > button *,
            div[data-testid="stButton"] > button,
            div[data-testid="stButton"] > button * {
                color: #ffffff !important;
            }

            label,
            label *,
            [data-testid="stCheckbox"] *,
            [data-testid="stRadio"] *,
            [data-baseweb="select"] * {
                color: #f8fafc !important;
            }

            .ag-theme-streamlit,
            .ag-root-wrapper,
            .ag-root,
            .ag-body,
            .ag-center-cols-container,
            .ag-row,
            .ag-row-even,
            .ag-row-odd {
                background: #0f172a !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,.34) !important;
            }

            .ag-header,
            .ag-header-row,
            .ag-header-cell,
            .ag-paging-panel {
                background: #1e293b !important;
                color: #f8fafc !important;
                border-color: rgba(96,165,250,.34) !important;
            }

            .ag-cell,
            .ag-cell-value,
            .ag-header-cell-text,
            .ag-paging-panel *,
            .ag-icon {
                color: #f8fafc !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def _show_kpi_cards(df, numeric_cols):
    missing_values = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    outlier_count, _ = _detect_outlier_count(df, numeric_cols)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("⚠️", "Missing Values", f"{missing_values:,}"),
        ("🔁", "Duplicate Rows", f"{duplicate_rows:,}"),
        ("📊", "Outliers", f"{outlier_count:,}"),
        ("🧱", "Total Columns", f"{df.shape[1]}"),
    ]

    for col, (icon, label, value) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(
                f"""
                <div class="clean-kpi">
                    <div class="clean-kpi-icon">{icon}</div>
                    <div class="clean-kpi-label">{label}</div>
                    <div class="clean-kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


def _run_selected_cleaning(
    original_df,
    file_name,
    selected_features,
    missing_method,
    numeric_cols,
    categorical_cols,
    smart=False
):
    before_df = original_df.copy()
    clean_df = original_df.copy()
    logs = []

    if smart:
        selected_features = [
            "Missing Value Handling",
            "Duplicate Removal",
            "Outlier Handling",
            "String Cleaning",
            "Data Type Correction"
        ]
        missing_method = "Fill Median"

    cleaning_tag_parts = []

    if "Missing Value Handling" in selected_features:
        clean_df, before, after, log = _fill_missing_values(
            clean_df, numeric_cols, categorical_cols, missing_method
        )
        logs.extend(log)
        cleaning_tag_parts.append("missing")

    if "Duplicate Removal" in selected_features:
        clean_df, before, after, log = _remove_duplicate_rows(clean_df)
        logs.extend(log)
        cleaning_tag_parts.append("duplicate")

    if "Outlier Handling" in selected_features:
        clean_df, before, after, before_detail, after_detail, log = _remove_outliers_iqr(
            clean_df, numeric_cols
        )
        logs.extend(log)
        cleaning_tag_parts.append("outlier")

    if "String Cleaning" in selected_features:
        clean_df, changed, log = _clean_string_columns(clean_df, categorical_cols)
        logs.extend(log)
        cleaning_tag_parts.append("string")

    if "Data Type Correction" in selected_features:
        clean_df, dtype_changes, log = _correct_data_types(clean_df)
        logs.extend(log)
        cleaning_tag_parts.append("dtype")

    if smart:
        cleaning_tag = "smart_all"
    elif cleaning_tag_parts:
        cleaning_tag = "_".join(cleaning_tag_parts)
    else:
        cleaning_tag = "none"

    summary_df = _make_summary_table(before_df, clean_df, numeric_cols)
    log_df = pd.DataFrame(logs) if logs else pd.DataFrame({
        "Action": ["No Cleaning"],
        "Method": ["-"],
        "Result": ["Tidak ada fitur cleaning yang dipilih."]
    })

    csv_path, xlsx_path, csv_name, xlsx_name, excel_bytes = _save_cleaned_file(
        clean_df,
        file_name,
        cleaning_tag,
        summary_df=summary_df,
        log_df=log_df
    )

    return {
        "clean_df": clean_df,
        "summary_df": summary_df,
        "log_df": log_df,
        "csv_path": csv_path,
        "xlsx_path": xlsx_path,
        "csv_name": csv_name,
        "xlsx_name": xlsx_name,
        "excel_bytes": excel_bytes,
        "cleaning_tag": cleaning_tag
    }


def _display_cleaning_result(result):
    clean_df = result["clean_df"]
    summary_df = result["summary_df"]
    log_df = result["log_df"]

    st.markdown('<div class="clean-card-title">📊 Before vs After Cleaning</div>', unsafe_allow_html=True)
    show_table(summary_df, key=f"cleaning_summary_{result['cleaning_tag']}", page_size=10, height=250)

    st.markdown('<div class="clean-card-title">📝 Cleaning Log</div>', unsafe_allow_html=True)
    show_table(log_df, key=f"cleaning_log_{result['cleaning_tag']}", page_size=10, height=250)

    st.markdown('<div class="clean-card-title">👀 Preview Cleaned Dataset</div>', unsafe_allow_html=True)
    show_table(clean_df.head(15), key=f"cleaned_preview_{result['cleaning_tag']}", page_size=15, height=330)

    st.markdown(
        f"""
        <div class="clean-path">
            📁 CSV saved: <b>{result['csv_path']}</b><br>
            📁 Excel saved: <b>{result['xlsx_path']}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    csv_data = clean_df.to_csv(index=False).encode("utf-8")

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "⬇️ Download Cleaned CSV",
            data=csv_data,
            file_name=result["csv_name"],
            mime="text/csv",
            use_container_width=True
        )
    with d2:
        st.download_button(
            "⬇️ Download Cleaned Excel",
            data=result["excel_bytes"],
            file_name=result["xlsx_name"],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def show_data_cleaning_page(
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
    inject_cleaning_css()

    st.markdown('<div class="section-title">🧹 Data Cleaning</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="clean-hero">
            <div class="clean-title">🧹 Advanced Data Cleaning Center</div>
            <div class="clean-subtitle">
                Pilih fitur cleaning satu per satu, jalankan beberapa fitur sekaligus,
                atau gunakan Smart Auto Cleaning untuk menghasilkan dataset final siap analisis.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    _show_kpi_cards(df, numeric_cols)

    left, right = st.columns([1.15, 1], gap="medium")

    with left:
        st.markdown(
            """
            <div class="clean-card">
                <div class="clean-card-title">🧩 Cleaning Method Selection</div>
                <div class="clean-desc">
                    Pilih fitur cleaning yang ingin dijalankan. Setiap proses akan menghasilkan output,
                    tabel before-after, preview data, notifikasi, dan file otomatis di folder <b>data/processed</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        selected_features = st.multiselect(
            "Pilih fitur cleaning",
            [
                "Missing Value Handling",
                "Duplicate Removal",
                "Outlier Handling",
                "String Cleaning",
                "Data Type Correction"
            ],
            default=["Missing Value Handling", "Duplicate Removal"]
        )

        missing_method = st.selectbox(
            "Metode Missing Value",
            ["Fill Median", "Fill Mean", "Fill Mode", "Drop Missing Rows"],
            index=0
        )

        badges = "".join(
            [f'<span class="clean-method-badge">{feature}</span>' for feature in selected_features]
        )
        if badges:
            st.markdown(badges, unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="clean-card">
                <div class="clean-card-title">🚀 Smart Auto Cleaning</div>
                <div class="clean-desc">
                    Fitur ini menjalankan semua proses cleaning otomatis:
                    missing value, duplicate rows, outlier IQR, string cleaning,
                    dan data type correction.
                </div>
                <div class="clean-note">
                    Rekomendasi default: Numeric → Median, Categorical → Mode, Outlier → IQR.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    b1, b2 = st.columns(2)

    with b1:
        run_selected = st.button("🧹 Run Selected Cleaning", use_container_width=True)

    with b2:
        run_smart = st.button("🚀 Smart Auto Cleaning", use_container_width=True)

    if run_selected:
        if not selected_features:
            st.warning("Pilih minimal satu fitur cleaning terlebih dahulu.")
            st.toast("Belum ada fitur cleaning yang dipilih", icon="⚠️")
        else:
            try:
                with st.spinner("Menjalankan selected cleaning..."):
                    result = _run_selected_cleaning(
                        df,
                        file_name,
                        selected_features,
                        missing_method,
                        numeric_cols,
                        categorical_cols,
                        smart=False
                    )

                st.session_state.df = result["clean_df"]
                st.session_state.last_cleaning_result = result

                st.success("Selected cleaning selesai.")
                st.toast("Selected cleaning berhasil dijalankan", icon="✅")
                st.toast(f"File tersimpan: {result['csv_name']}", icon="📁")

            except Exception as e:
                st.error("Selected cleaning gagal.")
                st.code(str(e))
                st.toast("Selected cleaning gagal", icon="❌")

    if run_smart:
        try:
            with st.spinner("Menjalankan Smart Auto Cleaning..."):
                result = _run_selected_cleaning(
                    df,
                    file_name,
                    selected_features=[],
                    missing_method="Fill Median",
                    numeric_cols=numeric_cols,
                    categorical_cols=categorical_cols,
                    smart=True
                )

            st.session_state.df = result["clean_df"]
            st.session_state.last_cleaning_result = result

            st.success("Smart Auto Cleaning selesai.")
            st.toast("Smart Auto Cleaning berhasil dijalankan", icon="✅")
            st.toast(f"File final tersimpan: {result['csv_name']}", icon="📁")

        except Exception as e:
            st.error("Smart Auto Cleaning gagal.")
            st.code(str(e))
            st.toast("Smart Auto Cleaning gagal", icon="❌")

    st.markdown('<div class="clean-card-title">📌 Current Data Quality Report</div>', unsafe_allow_html=True)

    summary_col, missing_col = st.columns([1, 1.25])

    with summary_col:
        with _safe_container(border=True):
            try:
                clean_summary = cleaning_summary(df)
            except Exception:
                clean_summary = pd.DataFrame({
                    "Item": ["Total Rows", "Total Columns", "Missing Values", "Duplicate Rows"],
                    "Value": [df.shape[0], df.shape[1], df.isna().sum().sum(), df.duplicated().sum()]
                })
            show_table(clean_summary, key="current_cleaning_summary", page_size=10, height=245)

    with missing_col:
        with _safe_container(border=True):
            missing_detail = pd.DataFrame({
                "Variable": df.columns,
                "Missing Count": df.isna().sum().values,
                "Missing Percentage (%)": (df.isna().mean() * 100).round(2).values
            }).sort_values("Missing Count", ascending=False)
            show_table(missing_detail, key="current_missing_detail", page_size=10, height=245)

    if "last_cleaning_result" in st.session_state:
        st.markdown('<div class="clean-card-title">✅ Last Cleaning Output</div>', unsafe_allow_html=True)
        _display_cleaning_result(st.session_state.last_cleaning_result)

    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()

    with nav2:
        if st.button("👀 Data Preview", use_container_width=True):
            st.session_state.page = "Data Preview"
            st.rerun()

    with nav3:
        if st.button("📊 Numerical Statistics", use_container_width=True):
            st.session_state.page = "Numerical Variables"
            st.rerun()
