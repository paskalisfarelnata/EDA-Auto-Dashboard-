import streamlit as st
from contextlib import nullcontext
from st_aggrid import AgGrid, GridOptionsBuilder

try:
    from backend.theme import get_aggrid_custom_css
except Exception:
    def get_aggrid_custom_css():
        return {}


def _safe_table_container():
    """Container dengan border jika versi Streamlit mendukung."""
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def _calculate_grid_height(row_count, selected_page_size, requested_height=430):
    """
    Tinggi tabel otomatis mengikuti jumlah data.
    Jadi kalau data cuma 4 baris, area bawah tidak kosong panjang.
    Kalau data banyak, tetap dibatasi agar halaman tidak terlalu panjang.
    """
    try:
        row_count = int(row_count)
    except Exception:
        row_count = 0

    try:
        selected_page_size = int(selected_page_size)
    except Exception:
        selected_page_size = 10

    try:
        requested_height = int(requested_height)
    except Exception:
        requested_height = 430

    visible_rows = min(max(row_count, 1), max(selected_page_size, 1))

    header_height = 50
    row_height = 44
    pagination_height = 58
    table_padding = 18

    calculated_height = header_height + (visible_rows * row_height) + pagination_height + table_padding

    min_height = 190
    max_height = max(requested_height, 260)

    return int(min(max(calculated_height, min_height), max_height))


def _build_aggrid_custom_css():
    """
    CSS khusus AgGrid.
    Catatan: tabel di project ini memakai st_aggrid, bukan DataTables.
    Jadi selector yang benar adalah .ag-..., bukan .dataTables_...
    """
    try:
        base_css = get_aggrid_custom_css() or {}
        if not isinstance(base_css, dict):
            base_css = {}
    except Exception:
        base_css = {}

    extra_css = {
        ".ag-root-wrapper": {
            "border": "1px solid rgba(125, 211, 252, 0.28) !important",
            "border-radius": "18px !important",
            "overflow": "hidden !important",
            "box-shadow": "0 18px 48px rgba(0, 0, 0, 0.28) !important",
            "background": "#0f172a !important",
        },
        ".ag-root": {
            "background": "#0f172a !important",
            "color": "#e5e7eb !important",
            "font-family": "Inter, Segoe UI, Arial, sans-serif !important",
        },
        ".ag-header": {
            "background": "linear-gradient(135deg, #0f172a, #172554) !important",
            "border-bottom": "1px solid rgba(125, 211, 252, 0.30) !important",
        },
        ".ag-header-cell": {
            "color": "#ffffff !important",
            "font-size": "15px !important",
            "font-weight": "950 !important",
            "padding-left": "16px !important",
            "padding-right": "16px !important",
        },
        ".ag-header-cell-text": {
            "color": "#ffffff !important",
            "font-weight": "950 !important",
        },
        ".ag-header-cell-label": {
            "justify-content": "flex-start !important",
        },
        ".ag-cell": {
            "color": "#f8fafc !important",
            "font-size": "14.5px !important",
            "padding-left": "16px !important",
            "padding-right": "16px !important",
            "border-bottom": "1px solid rgba(148, 163, 184, 0.16) !important",
            "display": "flex !important",
            "align-items": "center !important",
        },
        ".ag-row": {
            "background": "#111827 !important",
            "color": "#e5e7eb !important",
            "border-color": "rgba(148, 163, 184, 0.16) !important",
        },
        ".ag-row-odd": {
            "background": "#0f172a !important",
        },
        ".ag-row-hover": {
            "background": "rgba(14, 165, 233, 0.18) !important",
        },
        ".ag-row-selected": {
            "background": "rgba(34, 211, 238, 0.18) !important",
        },
        ".ag-paging-panel": {
            "background": "#0f172a !important",
            "color": "#cbd5e1 !important",
            "border-top": "1px solid rgba(125, 211, 252, 0.24) !important",
            "font-size": "13px !important",
            "font-weight": "700 !important",
            "padding": "10px 14px !important",
            "min-height": "52px !important",
        },
        ".ag-paging-panel *": {
            "color": "#cbd5e1 !important",
        },
        ".ag-center-cols-viewport": {
            "overflow-x": "auto !important",
        },
        ".ag-body-horizontal-scroll-viewport": {
            "background": "#0f172a !important",
        },
        ".ag-cell-focus": {
            "border": "none !important",
        },
        ".ag-cell-no-focus": {
            "border": "none !important",
        },
    }

    base_css.update(extra_css)
    return base_css


def _inject_table_css():
    st.markdown(
        """
        <style>
            /* Perluas area halaman agar tabel memanfaatkan ruang kiri-kanan */
            .block-container,
            div[data-testid="stMainBlockContainer"] {
                max-width: 1480px !important;
                padding-left: 1.3rem !important;
                padding-right: 1.3rem !important;
            }

            /* Frame bawaan st.container(border=True) */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 22px !important;
                border: 1px solid rgba(125, 211, 252, 0.25) !important;
                background:
                    linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.94)) !important;
                box-shadow:
                    0 20px 55px rgba(0, 0, 0, 0.28),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.03) !important;
                padding: 1rem !important;
            }

            .clean-table-label {
                font-size: 14px;
                font-weight: 850;
                color: #e5e7eb !important;
                margin-bottom: 6px;
                letter-spacing: 0.01em;
            }

            /* Selectbox show entries */
            div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
                min-height: 42px !important;
                border-radius: 14px !important;
                border: 1px solid rgba(103, 232, 249, 0.35) !important;
                background: rgba(31, 41, 55, 0.92) !important;
                color: #ffffff !important;
            }

            div[data-testid="stSelectbox"] * {
                color: #ffffff !important;
            }

            /* Search input */
            div[data-testid="stTextInput"] input {
                min-height: 42px !important;
                border-radius: 14px !important;
                border: 1px solid rgba(103, 232, 249, 0.35) !important;
                background: rgba(31, 41, 55, 0.92) !important;
                color: #ffffff !important;
                padding: 8px 13px !important;
            }

            div[data-testid="stTextInput"] input:focus {
                border-color: rgba(34, 211, 238, 0.78) !important;
                box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.12) !important;
            }

            div[data-testid="stTextInput"] input::placeholder {
                color: #94a3b8 !important;
                opacity: 1 !important;
            }

            /* AgGrid global polish */
            .ag-theme-streamlit {
                width: 100% !important;
                max-width: 100% !important;
                border-radius: 18px !important;
                overflow: hidden !important;
            }

            .ag-root-wrapper {
                width: 100% !important;
            }

            .ag-body-viewport,
            .ag-center-cols-viewport {
                scrollbar-width: thin !important;
                scrollbar-color: rgba(125, 211, 252, 0.55) rgba(15, 23, 42, 0.8) !important;
            }

            .ag-body-viewport::-webkit-scrollbar,
            .ag-center-cols-viewport::-webkit-scrollbar {
                height: 10px !important;
                width: 10px !important;
            }

            .ag-body-viewport::-webkit-scrollbar-track,
            .ag-center-cols-viewport::-webkit-scrollbar-track {
                background: rgba(15, 23, 42, 0.85) !important;
                border-radius: 999px !important;
            }

            .ag-body-viewport::-webkit-scrollbar-thumb,
            .ag-center-cols-viewport::-webkit-scrollbar-thumb {
                background: rgba(125, 211, 252, 0.55) !important;
                border-radius: 999px !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def show_table(data, key, page_size=10, height=430):
    """
    Menampilkan tabel AgGrid yang rapi:
    - Show entries
    - Search box
    - Sorting
    - Filter column
    - Pagination
    - Horizontal scroll
    - Bingkai tabel
    - Lebar mengikuti area halaman
    - Tinggi otomatis mengikuti jumlah data
    """
    if data is None or len(data) == 0:
        st.info("Data tidak tersedia.")
        return

    _inject_table_css()

    table_data = data.copy()

    # Hindari error jika ada data bertipe object/list/dict yang sulit dirender.
    for col in table_data.columns:
        if table_data[col].dtype == "object":
            table_data[col] = table_data[col].astype(str)

    page_size_options = [5, 10, 25, 50, 100]
    if page_size not in page_size_options:
        page_size_options.insert(0, page_size)

    with _safe_table_container():
        left, spacer, right = st.columns([1.15, 3.35, 1.85])

        with left:
            st.markdown('<div class="clean-table-label">Show entries</div>', unsafe_allow_html=True)
            selected_page_size = st.selectbox(
                "Show entries",
                page_size_options,
                index=page_size_options.index(page_size),
                key=f"{key}_page_size",
                label_visibility="collapsed"
            )

        with right:
            st.markdown('<div class="clean-table-label">Search</div>', unsafe_allow_html=True)
            search_text = st.text_input(
                "Search",
                value="",
                key=f"{key}_search",
                label_visibility="collapsed",
                placeholder="Search..."
            )

        gb = GridOptionsBuilder.from_dataframe(table_data)

        gb.configure_pagination(
            paginationAutoPageSize=False,
            paginationPageSize=selected_page_size
        )

        gb.configure_default_column(
            sortable=True,
            filter=True,
            resizable=True,
            editable=False,
            minWidth=150,
            wrapText=False,
            autoHeight=False
        )

        gb.configure_grid_options(
            quickFilterText=search_text,
            suppressMovableColumns=True,
            suppressCellFocus=True,
            rowHeight=44,
            headerHeight=50,
            animateRows=False,
            domLayout="normal"
        )

        grid_options = gb.build()

        auto_height = _calculate_grid_height(
            row_count=len(table_data),
            selected_page_size=selected_page_size,
            requested_height=height
        )

        AgGrid(
            table_data,
            gridOptions=grid_options,
            height=auto_height,
            fit_columns_on_grid_load=True,
            theme="streamlit",
            key=key,
            allow_unsafe_jscode=True,
            reload_data=False,
            custom_css=_build_aggrid_custom_css()
        )
