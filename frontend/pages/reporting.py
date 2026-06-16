from io import BytesIO
from datetime import datetime
import os
import glob
import streamlit as st

import pandas as pd
import numpy as np
from fpdf import FPDF


# =========================================================
# PASTEL THEME
# =========================================================
TEXT = (15, 23, 42)
MUTED = (100, 116, 139)
WHITE = (255, 255, 255)
BORDER = (203, 213, 225)

BLUE = (96, 165, 250)
VIOLET = (167, 139, 250)
PINK = (244, 114, 182)
TEAL = (45, 212, 191)
MINT = (134, 239, 172)
AMBER = (252, 211, 77)
PEACH = (253, 186, 116)

BLUE_LIGHT = (239, 246, 255)
PURPLE_LIGHT = (245, 243, 255)
PINK_LIGHT = (253, 242, 248)
TEAL_LIGHT = (240, 253, 250)
MINT_LIGHT = (240, 253, 244)
AMBER_LIGHT = (255, 251, 235)
PEACH_LIGHT = (255, 247, 237)
LAVENDER = (237, 233, 254)


# =========================================================
# BASIC HELPERS
# =========================================================
def clean_text(text):
    text = str(text) if text is not None else "-"

    replacements = {
        "📊": "", "⚠": "", "🔢": "", "📋": "", "🔗": "", "📈": "",
        "💡": "", "✅": "", "❌": "", "📄": "", "🌐": "", "📤": "",
        "📥": "", "⬇️": "", "🚀": "", "🔍": "", "📦": "",
        "•": "-", "–": "-", "—": "-", "“": '"', "”": '"', "’": "'",
        "…": "...", "\u2022": "-", "\u2013": "-", "\u2014": "-",
        "\u201c": '"', "\u201d": '"', "\u2019": "'", "\u2026": "...",
        "\u00b7": "-"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode("latin-1", "ignore").decode("latin-1")


def clean_numeric_series(series):
    cleaned = (
        series.astype(str)
        .str.replace("Rp", "", regex=False)
        .str.replace("rp", "", regex=False)
        .str.replace("IDR", "", regex=False)
        .str.replace("idr", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def to_dataframe(value, default_col="Value"):
    if value is None:
        return pd.DataFrame()
    if isinstance(value, pd.DataFrame):
        return value.copy()
    if isinstance(value, pd.Series):
        return value.to_frame(name=default_col)
    if isinstance(value, list):
        return pd.DataFrame({default_col: value})
    if isinstance(value, tuple):
        return pd.DataFrame({default_col: list(value)})
    if isinstance(value, dict):
        return pd.DataFrame([value])
    return pd.DataFrame({default_col: [value]})


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


def normalize_export_args(arg1=None, arg2=None, arg3=None, arg4=None):
    if isinstance(arg1, pd.DataFrame):
        df, num_stats, cat_stats, insights = arg1, arg2, arg3, arg4
    else:
        insights, df, num_stats, cat_stats = arg1, arg2, arg3, arg4

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()

    return normalize_insights(insights), df, to_dataframe(num_stats), to_dataframe(cat_stats)


def format_number(value):
    try:
        if pd.isna(value):
            return "-"
        if isinstance(value, (float, np.floating)):
            if abs(value) >= 1000:
                return f"{value:,.2f}"
            return f"{value:.3f}".rstrip("0").rstrip(".")
        if isinstance(value, (int, np.integer)):
            return f"{value:,}"
        return str(value)
    except Exception:
        return str(value)


# =========================================================
# DATA BUILDERS
# =========================================================
def get_numeric_columns(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return []

    cols = []
    for col in df.columns:
        converted = clean_numeric_series(df[col])
        if converted.notna().sum() >= 2:
            cols.append(col)

    return cols


def get_categorical_columns(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return []

    numeric_cols = set(get_numeric_columns(df))
    return [col for col in df.columns if col not in numeric_cols]


def make_overview_df(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame({
            "Metric": ["Rows", "Columns", "Missing Values", "Duplicate Rows"],
            "Value": [0, 0, 0, 0]
        })

    date_cols = [
        c for c in df.columns
        if any(k in str(c).lower() for k in ("date", "datetime", "timestamp"))
    ]

    numeric_cols = get_numeric_columns(df)
    categorical_count = max(df.shape[1] - len(numeric_cols) - len(date_cols), 0)

    return pd.DataFrame({
        "Metric": [
            "Rows", "Columns", "Missing Values", "Duplicate Rows",
            "Numerical Variables", "Categorical Variables", "Date/Datetime Variables"
        ],
        "Value": [
            df.shape[0],
            df.shape[1],
            int(df.isna().sum().sum()),
            int(df.duplicated().sum()),
            len(numeric_cols),
            categorical_count,
            len(date_cols)
        ]
    })


def make_data_quality_df(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame({
            "Variable": ["-"],
            "Data Type": ["-"],
            "Missing Count": [0],
            "Missing %": [0],
            "Unique Values": [0]
        })

    return pd.DataFrame({
        "Variable": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Count": df.isna().sum().values,
        "Missing %": (df.isna().mean() * 100).round(2).values,
        "Unique Values": df.nunique().values
    })


def make_correlation_matrix(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame({"Message": ["Dataset tidak tersedia."]})

    numeric_df = pd.DataFrame()
    for col in df.columns:
        converted = clean_numeric_series(df[col])
        if converted.notna().sum() >= 2:
            numeric_df[col] = converted

    if numeric_df.shape[1] < 2:
        return pd.DataFrame({"Message": ["Butuh minimal 2 variabel numerik."]})

    return numeric_df.corr().round(3).reset_index().rename(columns={"index": "Variable"})


def make_time_series_summary(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame({"Item": ["Time Series Status"], "Value": ["Not Available"]})

    date_cols = [
        c for c in df.columns
        if any(k in str(c).lower() for k in ("date", "datetime", "timestamp"))
    ]
    numeric_cols = get_numeric_columns(df)

    return pd.DataFrame({
        "Item": ["Time Series Status", "Date Columns Detected", "Numeric Columns Available"],
        "Value": [
            "Available" if date_cols and numeric_cols else "Not Available",
            ", ".join(str(c) for c in date_cols) if date_cols else "-",
            ", ".join(str(c) for c in numeric_cols) if numeric_cols else "-",
        ]
    })


def make_insights_df(insights):
    insights = normalize_insights(insights)
    rows = []
    current_section = "General"

    for item in insights:
        item_text = clean_text(item).strip()
        if not item_text:
            continue

        upper = item_text.upper()
        if any(k in upper for k in ("OVERVIEW", "INSIGHT", "FINAL BUSINESS", "MISSING VALUE")):
            current_section = item_text
        else:
            rows.append({"Section": current_section, "Insight": item_text})

    if not rows:
        rows.append({"Section": "General", "Insight": "Insight otomatis belum tersedia."})

    return pd.DataFrame(rows)


# =========================================================
# CHART GENERATION - NO INTERPRETATION
# =========================================================
def generate_pdf_charts(df):
    chart_items = []

    if not isinstance(df, pd.DataFrame) or df.empty:
        return chart_items

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
    except Exception:
        return chart_items

    out = os.path.join("outputs", "reports", "pdf_charts")
    os.makedirs(out, exist_ok=True)

    for old_file in glob.glob(os.path.join(out, "*.png")):
        try:
            os.remove(old_file)
        except Exception:
            pass

    numeric_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)

    BLUE_HEX = "#60A5FA"
    VIOLET_HEX = "#A78BFA"
    PINK_HEX = "#F472B6"
    TEAL_HEX = "#2DD4BF"
    AMBER_HEX = "#FCD34D"
    MINT_HEX = "#86EFAC"
    PEACH_HEX = "#FDBA74"
    NAVY_HEX = "#1E293B"
    GRID_HEX = "#E2E8F0"
    PALETTE = [BLUE_HEX, VIOLET_HEX, PINK_HEX, TEAL_HEX, AMBER_HEX, MINT_HEX, PEACH_HEX, "#C4B5FD"]

    def style_ax(ax, title):
        ax.set_title(title, fontsize=11, fontweight="bold", color=NAVY_HEX, pad=8)
        ax.tick_params(labelsize=7.5, colors="#475569")
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_color(GRID_HEX)

    # Histogram
    if numeric_cols:
        col = numeric_cols[0]
        data = clean_numeric_series(df[col]).dropna()

        if len(data) > 0:
            fig, ax = plt.subplots(figsize=(7.2, 3.6), facecolor="white")
            ax.hist(data, bins=min(28, max(5, len(data) // 5)), color=BLUE_HEX, edgecolor="white", alpha=0.90)
            ax.grid(axis="y", color=GRID_HEX, linestyle="-", linewidth=0.7)
            ax.set_xlabel(str(col), fontsize=8, color="#475569")
            ax.set_ylabel("Frequency", fontsize=8, color="#475569")
            style_ax(ax, f"Distribution: {col}")
            fig.tight_layout(pad=1.2)

            path = os.path.join(out, "01_histogram.png")
            fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
            plt.close(fig)

            chart_items.append({"title": f"Histogram - {col}", "path": path})

    # Boxplot
    if numeric_cols:
        col = numeric_cols[0]
        data = clean_numeric_series(df[col]).dropna()

        if len(data) > 0:
            fig, ax = plt.subplots(figsize=(7.2, 3.6), facecolor="white")
            ax.boxplot(
                data,
                vert=False,
                patch_artist=True,
                boxprops=dict(facecolor=TEAL_HEX, color=BLUE_HEX, alpha=0.78, linewidth=1.5),
                medianprops=dict(color=VIOLET_HEX, linewidth=2.5),
                whiskerprops=dict(color=BLUE_HEX, linewidth=1.3),
                capprops=dict(color=BLUE_HEX, linewidth=1.3),
                flierprops=dict(marker="o", markerfacecolor=PINK_HEX, markeredgecolor=PINK_HEX, alpha=0.50, markersize=4)
            )
            ax.grid(axis="x", color=GRID_HEX, linestyle="-", linewidth=0.7)
            ax.set_xlabel(str(col), fontsize=8, color="#475569")
            style_ax(ax, f"Boxplot: {col}")
            fig.tight_layout(pad=1.2)

            path = os.path.join(out, "02_boxplot.png")
            fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
            plt.close(fig)

            chart_items.append({"title": f"Boxplot - {col}", "path": path})

    # Bar categorical
    if cat_cols:
        col = cat_cols[0]
        counts = df[col].astype(str).value_counts().head(8)

        if len(counts) > 0:
            fig, ax = plt.subplots(figsize=(7.2, 3.6), facecolor="white")
            colors = (PALETTE * 2)[:len(counts)]
            ax.barh(counts.index[::-1], counts.values[::-1], color=colors[::-1], height=0.62, edgecolor="white")
            ax.grid(axis="x", color=GRID_HEX, linestyle="-", linewidth=0.7)
            ax.set_xlabel("Count", fontsize=8, color="#475569")
            style_ax(ax, f"Top Values: {col}")
            fig.tight_layout(pad=1.2)

            path = os.path.join(out, "03_bar_category.png")
            fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
            plt.close(fig)

            chart_items.append({"title": f"Bar Chart - {col}", "path": path})

    # Heatmap
    if len(numeric_cols) >= 2:
        selected = numeric_cols[:6]
        numeric_df = pd.DataFrame({c: clean_numeric_series(df[c]) for c in selected})
        corr = numeric_df.corr()

        if not corr.empty:
            cmap = mcolors.LinearSegmentedColormap.from_list(
                "pastel_cmap",
                ["#EFF6FF", "#93C5FD", "#A78BFA"]
            )

            fig, ax = plt.subplots(figsize=(7.2, 4.3), facecolor="white")
            im = ax.imshow(corr, cmap=cmap, vmin=-1, vmax=1, aspect="auto")
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=40, ha="right", fontsize=7.5, color="#334155")
            ax.set_yticklabels(corr.columns, fontsize=7.5, color="#334155")

            for i in range(len(corr.columns)):
                for j in range(len(corr.columns)):
                    val = corr.iloc[i, j]
                    color = "white" if abs(val) > 0.55 else NAVY_HEX
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6.5, color=color)

            cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
            cb.ax.tick_params(labelsize=7)
            style_ax(ax, "Correlation Heatmap")
            fig.tight_layout(pad=1.2)

            path = os.path.join(out, "04_heatmap.png")
            fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
            plt.close(fig)

            chart_items.append({"title": "Correlation Heatmap", "path": path})

    return chart_items


# =========================================================
# PDF CLASS
# =========================================================
class AutoEDAPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return

        self.set_font("Arial", "B", 7)
        self.set_text_color(*BLUE)
        self.cell(0, 5, "Auto EDA Analytics Report", ln=False, align="R")
        self.set_y(self.get_y() + 5)
        self.set_draw_color(*BORDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

    def footer(self):
        self.set_y(-9)
        self.set_draw_color(*BORDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_font("Arial", "", 6.5)
        self.set_text_color(*MUTED)
        self.cell(0, 5, f"Page {self.page_no()}  |  Auto EDA Analytics", align="C")


# =========================================================
# PDF LAYOUT HELPERS
# =========================================================
MARGIN_TOP = 8
MARGIN_SIDE = 10
PAGE_BOTTOM = 276


def set_rgb(pdf, rgb, target="text"):
    if target == "text":
        pdf.set_text_color(*rgb)
    elif target == "fill":
        pdf.set_fill_color(*rgb)
    elif target == "draw":
        pdf.set_draw_color(*rgb)


def check_space(pdf, needed):
    if pdf.get_y() + needed > PAGE_BOTTOM:
        pdf.add_page()


def add_section(pdf, title, fill_color=BLUE, gap_before=5):
    check_space(pdf, 14)

    if pdf.get_y() > MARGIN_TOP + 10:
        pdf.ln(gap_before)

    x = pdf.l_margin
    y = pdf.get_y()
    w = pdf.w - pdf.l_margin - pdf.r_margin
    h = 7

    set_rgb(pdf, fill_color, "fill")
    pdf.rect(x, y, w * 0.58, h, style="F")
    set_rgb(pdf, VIOLET, "fill")
    pdf.rect(x + w * 0.58, y, w * 0.42, h, style="F")

    pdf.set_xy(x + 3, y + 0.8)
    pdf.set_font("Arial", "B", 9.5)
    set_rgb(pdf, WHITE, "text")
    pdf.cell(w - 3, h - 1, clean_text(title), ln=True)

    set_rgb(pdf, TEXT, "text")
    pdf.ln(2)


def add_text(pdf, text, font_size=8.3, color=TEXT):
    pdf.set_font("Arial", "", font_size)
    set_rgb(pdf, color, "text")

    estimated_lines = max(1, len(str(text)) // 72 + 1)
    check_space(pdf, estimated_lines * 4.5 + 2)

    pdf.multi_cell(0, 4.5, clean_text(text))
    pdf.ln(1.5)


def add_metric_cards(pdf, df):
    overview = make_overview_df(df)
    pairs = overview.values.tolist()

    card_colors = [BLUE_LIGHT, PURPLE_LIGHT, TEAL_LIGHT, AMBER_LIGHT, MINT_LIGHT, PINK_LIGHT, LAVENDER]

    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    cols = 4
    card_w = page_w / cols
    card_h = 14

    rows_needed = -(-len(pairs) // cols)
    check_space(pdf, rows_needed * (card_h + 3) + 4)

    start_y = pdf.get_y()

    for idx, (metric, value) in enumerate(pairs):
        row = idx // cols
        col = idx % cols
        x = pdf.l_margin + col * card_w
        y = start_y + row * (card_h + 3)

        set_rgb(pdf, card_colors[idx % len(card_colors)], "fill")
        set_rgb(pdf, BORDER, "draw")
        pdf.set_line_width(0.2)
        pdf.rect(x, y, card_w - 2, card_h, style="DF")

        pdf.set_xy(x + 2, y + 1.5)
        pdf.set_font("Arial", "B", 6)
        set_rgb(pdf, BLUE, "text")
        pdf.multi_cell(card_w - 5, 3.2, clean_text(metric), align="C")

        pdf.set_xy(x + 2, y + 7.5)
        pdf.set_font("Arial", "B", 9)
        set_rgb(pdf, TEXT, "text")
        pdf.cell(card_w - 5, 5, clean_text(str(value)), align="C")

    pdf.set_y(start_y + rows_needed * (card_h + 3) + 2)


def add_table(pdf, dataframe, max_rows=15, max_cols=5, font_size=6.3):
    dataframe = to_dataframe(dataframe)

    if dataframe.empty:
        add_text(pdf, "Data tidak tersedia.", font_size=8)
        return

    df_show = dataframe.head(max_rows).iloc[:, :max_cols].copy()
    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    col_w = page_w / max(1, len(df_show.columns))
    row_h = 5.0
    header_h = 6.0

    estimated_h = header_h + len(df_show) * row_h + 4
    check_space(pdf, estimated_h)

    pdf.set_font("Arial", "B", font_size)
    set_rgb(pdf, BLUE, "fill")
    set_rgb(pdf, WHITE, "text")
    set_rgb(pdf, BORDER, "draw")
    pdf.set_line_width(0.15)

    for col in df_show.columns:
        pdf.cell(col_w, header_h, clean_text(str(col))[:22], border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Arial", "", font_size)
    set_rgb(pdf, TEXT, "text")

    pastel_rows = [BLUE_LIGHT, (255, 255, 255), PURPLE_LIGHT, TEAL_LIGHT]

    for i, (_, row) in enumerate(df_show.iterrows()):
        if pdf.get_y() + row_h > PAGE_BOTTOM:
            pdf.add_page()

            pdf.set_font("Arial", "B", font_size)
            set_rgb(pdf, BLUE, "fill")
            set_rgb(pdf, WHITE, "text")

            for col in df_show.columns:
                pdf.cell(col_w, header_h, clean_text(str(col))[:22], border=1, align="C", fill=True)
            pdf.ln()

            pdf.set_font("Arial", "", font_size)
            set_rgb(pdf, TEXT, "text")

        set_rgb(pdf, pastel_rows[i % len(pastel_rows)], "fill")

        for value in row:
            pdf.cell(col_w, row_h, clean_text(format_number(value))[:26], border=1, fill=True)
        pdf.ln()

    pdf.ln(2.5)


def add_note_box(pdf, text, fill_color=BLUE_LIGHT, accent_color=BLUE):
    card_w = pdf.w - pdf.l_margin - pdf.r_margin
    lines = max(1, len(str(text)) // 88 + 1)
    card_h = max(10, lines * 4.1 + 5)

    check_space(pdf, card_h + 3)

    x = pdf.l_margin
    y = pdf.get_y()

    set_rgb(pdf, accent_color, "fill")
    pdf.rect(x, y, 2.6, card_h, style="F")

    set_rgb(pdf, fill_color, "fill")
    set_rgb(pdf, BORDER, "draw")
    pdf.rect(x + 2.6, y, card_w - 2.6, card_h, style="DF")

    pdf.set_xy(x + 5, y + 2.2)
    pdf.set_font("Arial", "", 7.7)
    set_rgb(pdf, TEXT, "text")
    pdf.multi_cell(card_w - 8, 4, clean_text(text[:260]))

    pdf.set_y(y + card_h + 2)


def add_insight_cards(pdf, insights, max_items=10):
    insight_df = make_insights_df(insights)

    if insight_df.empty:
        add_text(pdf, "Insight otomatis belum tersedia.")
        return

    count = 0
    current_section = None
    colors = [BLUE_LIGHT, PURPLE_LIGHT, TEAL_LIGHT, MINT_LIGHT, AMBER_LIGHT, PINK_LIGHT]
    accents = [BLUE, VIOLET, TEAL, MINT, AMBER, PINK]

    for _, row in insight_df.iterrows():
        if count >= max_items:
            break

        section = clean_text(row["Section"])
        insight = clean_text(row["Insight"])

        if section != current_section:
            current_section = section
            check_space(pdf, 12)
            pdf.set_font("Arial", "B", 8)
            set_rgb(pdf, BLUE, "text")
            pdf.cell(0, 5, current_section, ln=True)
            set_rgb(pdf, TEXT, "text")

        add_note_box(
            pdf,
            insight,
            fill_color=colors[count % len(colors)],
            accent_color=accents[count % len(accents)]
        )

        count += 1


def add_charts_to_pdf(pdf, chart_items):
    if not chart_items:
        add_section(pdf, "10. Visualization Summary", fill_color=PINK)
        add_note_box(
            pdf,
            "Visualisasi belum dapat dibuat. Pastikan matplotlib sudah terinstall dan dataset memiliki variabel numerik atau kategorik yang valid.",
            fill_color=PINK_LIGHT,
            accent_color=PINK
        )
        return

    add_section(pdf, "10. Visualization Summary", fill_color=PINK)

    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    img_h = 72

    for idx, item in enumerate(chart_items[:4]):
        path = item.get("path")
        title = item.get("title", "Visualization")

        if not path or not os.path.exists(path):
            continue

        check_space(pdf, img_h + 11)

        pdf.set_font("Arial", "B", 8.5)
        set_rgb(pdf, [BLUE, VIOLET, TEAL, PINK][idx % 4], "text")
        pdf.cell(0, 5, clean_text(title), ln=True)
        set_rgb(pdf, TEXT, "text")

        try:
            pdf.image(path, x=pdf.l_margin, y=pdf.get_y(), w=page_w, h=img_h)
            pdf.set_y(pdf.get_y() + img_h + 4)
        except Exception:
            add_text(pdf, "Gambar visualisasi gagal dimuat.", font_size=7.5)


# =========================================================
# COVER PAGE
# =========================================================
def build_cover(pdf, df):
    set_rgb(pdf, BLUE_LIGHT, "fill")
    pdf.rect(0, 0, 210, 297, style="F")

    set_rgb(pdf, PURPLE_LIGHT, "fill")
    pdf.ellipse(150, -20, 82, 82, style="F")
    set_rgb(pdf, TEAL_LIGHT, "fill")
    pdf.ellipse(-20, 225, 90, 90, style="F")
    set_rgb(pdf, PINK_LIGHT, "fill")
    pdf.ellipse(158, 230, 70, 70, style="F")

    set_rgb(pdf, BLUE, "fill")
    pdf.rect(0, 0, 105, 5, style="F")
    set_rgb(pdf, VIOLET, "fill")
    pdf.rect(105, 0, 105, 5, style="F")

    pdf.set_y(58)
    pdf.set_font("Arial", "B", 25)
    set_rgb(pdf, TEXT, "text")
    pdf.cell(0, 12, "AUTO EDA", ln=True, align="C")

    pdf.set_font("Arial", "B", 24)
    set_rgb(pdf, BLUE, "text")
    pdf.cell(0, 12, "ANALYTICS REPORT", ln=True, align="C")

    pdf.ln(4)
    set_rgb(pdf, VIOLET, "draw")
    pdf.set_line_width(0.6)
    pdf.line(67, pdf.get_y(), 143, pdf.get_y())
    pdf.ln(6)

    pdf.set_font("Arial", "", 9)
    set_rgb(pdf, MUTED, "text")
    pdf.cell(0, 6, "Generated Automatically by Auto EDA Dashboard", ln=True, align="C")
    pdf.set_font("Arial", "", 8.5)
    pdf.cell(0, 5, datetime.now().strftime("%d %B %Y  |  %H:%M"), ln=True, align="C")

    if isinstance(df, pd.DataFrame) and not df.empty:
        pdf.ln(15)
        stats = [
            ("Rows", f"{df.shape[0]:,}"),
            ("Columns", f"{df.shape[1]:,}"),
            ("Missing", f"{int(df.isna().sum().sum()):,}"),
            ("Duplicates", f"{int(df.duplicated().sum()):,}"),
        ]

        card_colors = [BLUE_LIGHT, PURPLE_LIGHT, TEAL_LIGHT, PINK_LIGHT]
        card_w = 38
        gap = 3
        total_w = card_w * len(stats) + gap * (len(stats) - 1)
        start_x = (210 - total_w) / 2
        y = pdf.get_y()

        for i, (label, val) in enumerate(stats):
            x = start_x + i * (card_w + gap)

            set_rgb(pdf, card_colors[i], "fill")
            set_rgb(pdf, BORDER, "draw")
            pdf.rect(x, y, card_w, 19, style="DF")

            pdf.set_xy(x, y + 2.3)
            pdf.set_font("Arial", "B", 11)
            set_rgb(pdf, TEXT, "text")
            pdf.cell(card_w, 7, val, align="C")

            pdf.set_xy(x, y + 10.5)
            pdf.set_font("Arial", "", 6.5)
            set_rgb(pdf, MUTED, "text")
            pdf.cell(card_w, 5, label, align="C")

    pdf.set_y(274)
    pdf.set_font("Arial", "", 7)
    set_rgb(pdf, MUTED, "text")
    pdf.cell(0, 5, "Powered by Auto EDA Analytics  |  Pastel Report Edition", align="C")


# =========================================================
# MAIN PDF EXPORT
# =========================================================
def export_pdf(arg1=None, arg2=None, arg3=None, arg4=None):
    insights, df, num_stats, cat_stats = normalize_export_args(arg1, arg2, arg3, arg4)

    pdf = AutoEDAPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_margins(MARGIN_SIDE, MARGIN_TOP, MARGIN_SIDE)

    pdf.add_page()
    build_cover(pdf, df)

    pdf.add_page()

    add_section(pdf, "1. Executive Summary", fill_color=BLUE)
    add_text(
        pdf,
        "Laporan ini dibuat secara otomatis oleh Auto EDA Analytics Dashboard. Isi report mencakup ringkasan kualitas data, "
        "statistik deskriptif, analisis korelasi, informasi time series, visualisasi otomatis, dan insight cerdas dari dataset "
        "yang diunggah. Report ini dapat digunakan sebagai fondasi awal sebelum analisis lanjutan."
    )

    add_section(pdf, "2. Dataset Summary", fill_color=VIOLET)
    add_metric_cards(pdf, df)

    add_section(pdf, "3. Dataset Overview", fill_color=TEAL)
    add_table(pdf, make_overview_df(df), max_rows=8, max_cols=2, font_size=7.5)

    add_section(pdf, "4. Initial Intelligent Insights", fill_color=PINK)
    add_insight_cards(pdf, insights, max_items=8)

    add_section(pdf, "5. Data Quality Assessment", fill_color=BLUE)
    add_text(
        pdf,
        "Ringkasan kualitas data berikut menunjukkan missing value, tipe data, dan jumlah nilai unik pada setiap variabel.",
        font_size=8
    )
    add_table(pdf, make_data_quality_df(df), max_rows=14, max_cols=5, font_size=6.3)

    add_section(pdf, "6. Numerical Statistics", fill_color=VIOLET)
    if isinstance(num_stats, pd.DataFrame) and not num_stats.empty:
        add_table(pdf, num_stats, max_rows=13, max_cols=5, font_size=6.2)
    else:
        add_text(pdf, "Numerical statistics tidak tersedia.", font_size=8)

    add_section(pdf, "7. Categorical Statistics", fill_color=TEAL)
    if isinstance(cat_stats, pd.DataFrame) and not cat_stats.empty:
        add_table(pdf, cat_stats, max_rows=13, max_cols=5, font_size=6.2)
    else:
        add_text(pdf, "Categorical statistics tidak tersedia.", font_size=8)

    add_section(pdf, "8. Correlation Analysis", fill_color=PINK)
    add_text(
        pdf,
        "Matriks korelasi menunjukkan kekuatan hubungan linier antar variabel numerik. Nilai mendekati 1 atau -1 menunjukkan hubungan yang semakin kuat.",
        font_size=8
    )
    add_table(pdf, make_correlation_matrix(df), max_rows=9, max_cols=5, font_size=6)

    add_section(pdf, "9. Time Series Summary", fill_color=AMBER)
    add_table(pdf, make_time_series_summary(df), max_rows=4, max_cols=2, font_size=7)

    chart_items = generate_pdf_charts(df)
    add_charts_to_pdf(pdf, chart_items)

    add_section(pdf, "11. Final Conclusion", fill_color=VIOLET)
    add_text(
        pdf,
        "Dataset telah dianalisis secara menyeluruh mulai dari kualitas data, statistik deskriptif, distribusi variabel, "
        "hubungan antar variabel, visualisasi otomatis, hingga potensi analisis time series. Laporan ini dapat dijadikan "
        "referensi awal sebelum proses data cleaning lanjutan, dashboard monitoring, business intelligence, maupun machine learning.",
        font_size=8.3
    )

    pdf_output = pdf.output(dest="S")

    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1", errors="ignore")

    return bytes(pdf_output)


# =========================================================
# HTML EXPORT
# =========================================================
def dataframe_to_html_table(value, max_rows=20):
    dataframe = to_dataframe(value)

    if dataframe.empty:
        return "<p>Data tidak tersedia.</p>"

    return dataframe.head(max_rows).to_html(index=False, border=0, classes="table")


def export_html(arg1=None, arg2=None, arg3=None, arg4=None):
    insights, df, num_stats, cat_stats = normalize_export_args(arg1, arg2, arg3, arg4)

    rows = df.shape[0] if isinstance(df, pd.DataFrame) and not df.empty else 0
    cols = df.shape[1] if isinstance(df, pd.DataFrame) and not df.empty else 0
    missing = int(df.isna().sum().sum()) if isinstance(df, pd.DataFrame) and not df.empty else 0
    duplicate = int(df.duplicated().sum()) if isinstance(df, pd.DataFrame) and not df.empty else 0

    overview_html = dataframe_to_html_table(make_overview_df(df))
    data_quality_html = dataframe_to_html_table(make_data_quality_df(df), max_rows=20)
    corr_html = dataframe_to_html_table(make_correlation_matrix(df), max_rows=10)
    ts_html = dataframe_to_html_table(make_time_series_summary(df))
    num_html = dataframe_to_html_table(num_stats, max_rows=15)
    cat_html = dataframe_to_html_table(cat_stats, max_rows=15)

    insights_df = make_insights_df(insights)
    insight_cards = ""

    for section in insights_df["Section"].unique():
        section_df = insights_df[insights_df["Section"] == section]
        items = "".join([f"<p>{clean_text(row)}</p>" for row in section_df["Insight"]])
        insight_cards += f"""
        <div class="card">
            <h3>{clean_text(section)}</h3>
            {items}
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Auto EDA Analytics Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 35px;
    background: linear-gradient(135deg, #eff6ff, #f5f3ff, #fff1f2);
    color: #0f172a;
}}
.container {{
    background: white;
    padding: 36px;
    border-radius: 22px;
    box-shadow: 0 12px 34px rgba(15,23,42,.12);
    max-width: 1100px;
    margin: auto;
}}
h1 {{
    text-align: center;
    color: #2563eb;
    margin-bottom: 4px;
    font-size: 28px;
    letter-spacing: -.5px;
}}
.subtitle {{
    text-align: center;
    color: #64748b;
    font-size: 13px;
    margin-bottom: 28px;
}}
h2 {{
    color: white;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
    padding: 11px 16px;
    border-radius: 12px;
    margin-top: 28px;
    font-size: 15px;
}}
.summary {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 24px 0;
}}
.summary-card {{
    background: #eff6ff;
    padding: 16px;
    border-radius: 16px;
    text-align: center;
    border: 1px solid #bfdbfe;
}}
.summary-card h3 {{
    margin: 0;
    color: #2563eb;
    font-size: 12px;
}}
.summary-card p {{
    margin: 6px 0 0;
    font-size: 22px;
    font-weight: bold;
    color: #0f172a;
}}
.card {{
    padding: 16px;
    margin-bottom: 14px;
    border-left: 5px solid #a78bfa;
    background: #f5f3ff;
    border-radius: 12px;
}}
.card h3 {{
    color: #6d28d9;
    margin: 0 0 8px;
    font-size: 13px;
}}
.card p {{
    margin: 4px 0;
    font-size: 13px;
    line-height: 1.6;
    color: #1e293b;
}}
.table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    font-size: 13px;
}}
.table th {{
    background: #60a5fa;
    color: white;
    padding: 9px 11px;
    text-align: left;
}}
.table td {{
    padding: 7px 11px;
    border-bottom: 1px solid #dbeafe;
}}
.table tr:nth-child(even) {{
    background: #f8faff;
}}
p {{
    line-height: 1.65;
}}
</style>
</head>
<body>
<div class="container">
<h1>AUTO EDA ANALYTICS REPORT</h1>
<p class="subtitle">Generated At: {datetime.now().strftime('%d %B %Y  |  %H:%M')}</p>
<div class="summary">
  <div class="summary-card"><h3>Rows</h3><p>{rows}</p></div>
  <div class="summary-card"><h3>Columns</h3><p>{cols}</p></div>
  <div class="summary-card"><h3>Missing</h3><p>{missing}</p></div>
  <div class="summary-card"><h3>Duplicates</h3><p>{duplicate}</p></div>
</div>
<h2>Dataset Overview</h2>{overview_html}
<h2>Data Quality Assessment</h2>{data_quality_html}
<h2>Numerical Statistics</h2>{num_html}
<h2>Categorical Statistics</h2>{cat_html}
<h2>Correlation Analysis</h2>{corr_html}
<h2>Time Series Summary</h2>{ts_html}
<h2>Intelligent Insights</h2>{insight_cards}
<h2>Final Conclusion</h2>
<p>Dataset telah dianalisis secara otomatis untuk melihat kualitas data, distribusi variabel, hubungan antar variabel, serta potensi analisis lanjutan.</p>
</div>
</body>
</html>"""

    return html


# =========================================================
# EXCEL & CSV EXPORT
# =========================================================
def export_excel(df, num_stats, cat_stats, insights=None):
    insights = normalize_insights(insights)

    df = df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    num_stats = to_dataframe(num_stats)
    cat_stats = to_dataframe(cat_stats)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        make_overview_df(df).to_excel(writer, index=False, sheet_name="Overview")
        make_data_quality_df(df).to_excel(writer, index=False, sheet_name="Data Quality")
        num_stats.to_excel(writer, index=False, sheet_name="Numerical Stats")
        cat_stats.to_excel(writer, index=False, sheet_name="Categorical Stats")
        make_correlation_matrix(df).to_excel(writer, index=False, sheet_name="Correlation")
        make_time_series_summary(df).to_excel(writer, index=False, sheet_name="Time Series")
        make_insights_df(insights).to_excel(writer, index=False, sheet_name="Insights")
        df.to_excel(writer, index=False, sheet_name="Raw Data")

    return output.getvalue()


def export_csv(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return "Metric,Value\nRows,0\nColumns,0\n".encode("utf-8")

    summary_df = make_overview_df(df)
    data_quality_df = make_data_quality_df(df)

    if isinstance(data_quality_df, pd.DataFrame) and not data_quality_df.empty:
        top = data_quality_df.sort_values("Missing Count", ascending=False).iloc[0]
        extra = pd.DataFrame({
            "Metric": ["Top Missing Column", "Top Missing %"],
            "Value": [top["Variable"], top["Missing %"]]
        })
        summary_df = pd.concat([summary_df, extra], ignore_index=True)

    return summary_df.to_csv(index=False).encode("utf-8")

# =========================================================
# STREAMLIT REPORTING PAGES
# Dipakai oleh app.py:
# from frontend.pages.reporting import (
#     show_download_pdf_page,
#     show_download_html_page,
#     show_export_excel_csv_page,
# )
# =========================================================

def _safe_output_base_name(file_name=None):
    """Membuat nama file output yang aman dari nama dataset."""
    import re

    if file_name:
        base_name = os.path.splitext(str(file_name))[0]
    else:
        base_name = "dataset"

    base_name = base_name.lower()
    base_name = re.sub(r"[^a-zA-Z0-9_]+", "_", base_name)
    base_name = re.sub(r"_+", "_", base_name)

    return base_name.strip("_") or "dataset"


def _ensure_report_dirs():
    os.makedirs("outputs/reports", exist_ok=True)
    os.makedirs("outputs/exported_files", exist_ok=True)


def _render_report_page_header(title, subtitle=None):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        """,
        unsafe_allow_html=True
    )

    if subtitle:
        st.caption(subtitle)


def show_download_pdf_page(
    df,
    file_name=None,
    file_ext=None,
    file_size=None,
    saved_file_path=None,
    numeric_cols=None,
    categorical_cols=None,
    date_cols=None,
    num_stats=None,
    cat_stats=None,
    insights=None,
    save_visualizations=None,
    render_summary_interpretation=None,
    calculate_health_score=None,
    get_health_label=None
):
    """Halaman Streamlit untuk download PDF report."""
    _render_report_page_header(
        "📄 Download Report PDF",
        "Generate laporan PDF otomatis dari hasil EDA, statistik, visualisasi, dan insight."
    )

    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("Belum ada dataset yang bisa dibuat report. Silakan upload data terlebih dahulu.")
        return

    output_base = _safe_output_base_name(file_name)
    pdf_filename = f"auto_eda_{output_base}_report.pdf"

    try:
        pdf_data = export_pdf(
            insights,
            df,
            num_stats,
            cat_stats
        )

        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_data,
            file_name=pdf_filename,
            mime="application/pdf",
            use_container_width=True
        )

        _ensure_report_dirs()

        pdf_path = os.path.join(
            "outputs",
            "reports",
            pdf_filename
        )

        with open(pdf_path, "wb") as file:
            file.write(pdf_data)

        st.success(f"PDF berhasil dibuat: {pdf_filename}")
        st.caption(f"Saved path: {pdf_path}")

    except Exception as e:
        st.error("❌ PDF Report gagal dibuat.")
        st.code(str(e))


def show_download_html_page(
    df,
    file_name=None,
    file_ext=None,
    file_size=None,
    saved_file_path=None,
    numeric_cols=None,
    categorical_cols=None,
    date_cols=None,
    num_stats=None,
    cat_stats=None,
    insights=None,
    save_visualizations=None,
    render_summary_interpretation=None,
    calculate_health_score=None,
    get_health_label=None
):
    """Halaman Streamlit untuk download HTML dashboard/report."""
    _render_report_page_header(
        "🌐 Download HTML Dashboard",
        "Export ringkasan EDA ke file HTML yang bisa dibuka di browser."
    )

    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("Belum ada dataset yang bisa dibuat HTML. Silakan upload data terlebih dahulu.")
        return

    output_base = _safe_output_base_name(file_name)
    html_filename = f"auto_eda_{output_base}_dashboard.html"

    try:
        html_data = export_html(
            insights,
            df,
            num_stats,
            cat_stats
        )

        st.download_button(
            label="📥 Download HTML Dashboard",
            data=html_data,
            file_name=html_filename,
            mime="text/html",
            use_container_width=True
        )

        _ensure_report_dirs()

        html_path = os.path.join(
            "outputs",
            "reports",
            html_filename
        )

        with open(html_path, "w", encoding="utf-8") as file:
            file.write(html_data)

        st.success(f"HTML berhasil dibuat: {html_filename}")
        st.caption(f"Saved path: {html_path}")

    except Exception as e:
        st.error("❌ HTML Dashboard gagal dibuat.")
        st.code(str(e))


def show_export_excel_csv_page(
    df,
    file_name=None,
    file_ext=None,
    file_size=None,
    saved_file_path=None,
    numeric_cols=None,
    categorical_cols=None,
    date_cols=None,
    num_stats=None,
    cat_stats=None,
    insights=None,
    save_visualizations=None,
    render_summary_interpretation=None,
    calculate_health_score=None,
    get_health_label=None
):
    """Halaman Streamlit untuk export Excel dan CSV."""
    _render_report_page_header(
        "📤 Export Result to Excel / CSV",
        "Download hasil EDA dalam format Excel atau CSV."
    )

    if not isinstance(df, pd.DataFrame) or df.empty:
        st.warning("Belum ada dataset yang bisa diexport. Silakan upload data terlebih dahulu.")
        return

    output_base = _safe_output_base_name(file_name)

    excel_filename = f"auto_eda_{output_base}_result.xlsx"
    csv_filename = f"auto_eda_{output_base}_result.csv"

    col1, col2 = st.columns(2)

    with col1:
        try:
            excel_data = export_excel(
                df,
                num_stats,
                cat_stats,
                insights
            )

            st.download_button(
                label="📥 Export Excel",
                data=excel_data,
                file_name=excel_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

            _ensure_report_dirs()

            excel_path = os.path.join(
                "outputs",
                "exported_files",
                excel_filename
            )

            with open(excel_path, "wb") as file:
                file.write(excel_data)

            st.success(f"Excel berhasil dibuat: {excel_filename}")
            st.caption(f"Saved path: {excel_path}")

        except Exception as e:
            st.error("❌ Export Excel gagal.")
            st.code(str(e))

    with col2:
        try:
            csv_data = export_csv(df)

            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
                use_container_width=True
            )

            _ensure_report_dirs()

            csv_path = os.path.join(
                "outputs",
                "exported_files",
                csv_filename
            )

            with open(csv_path, "wb") as file:
                file.write(csv_data)

            st.success(f"CSV berhasil dibuat: {csv_filename}")
            st.caption(f"Saved path: {csv_path}")

        except Exception as e:
            st.error("❌ Export CSV gagal.")
            st.code(str(e))
