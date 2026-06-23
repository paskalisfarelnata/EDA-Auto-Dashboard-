from io import BytesIO
from datetime import datetime
import os
import glob

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
# PDF EXPORT - COMPLETE REPORT WITH ACTIVE TABLE OF CONTENTS
# =========================================================
def _add_toc_page(pdf):
    """Reserve page 2 for active/clickable daftar isi."""
    pdf.add_page()
    pdf._toc_page_no = pdf.page_no()
    pdf._toc_entries = []


def _register_toc(pdf, title, level=1):
    """Create internal PDF link and return link id."""
    link_id = pdf.add_link()
    pdf.set_link(link_id, y=0, page=pdf.page_no())
    if not hasattr(pdf, "_toc_entries"):
        pdf._toc_entries = []
    pdf._toc_entries.append({
        "title": clean_text(title),
        "level": level,
        "page": pdf.page_no(),
        "link": link_id
    })
    return link_id


def add_report_section(pdf, title, fill_color=BLUE, level=1, intro=None):
    _register_toc(pdf, title, level=level)
    add_section(pdf, title, fill_color=fill_color)
    if intro:
        add_text(pdf, intro, font_size=8.2)


def _write_toc(pdf):
    """Write active table of contents on the reserved TOC page."""
    if not hasattr(pdf, "_toc_page_no") or not hasattr(pdf, "_toc_entries"):
        return

    current_page = pdf.page
    pdf.page = pdf._toc_page_no
    pdf.set_xy(MARGIN_SIDE, MARGIN_TOP + 14)

    pdf.set_font("Arial", "B", 21)
    set_rgb(pdf, BLUE, "text")
    pdf.cell(0, 11, "DAFTAR ISI", ln=True, align="C")

    pdf.set_font("Arial", "", 8)
    set_rgb(pdf, MUTED, "text")
    pdf.cell(0, 6, "Klik judul bagian untuk langsung menuju halaman terkait.", ln=True, align="C")
    pdf.ln(8)

    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    line_h = 7.0

    for idx, item in enumerate(pdf._toc_entries, start=1):
        if pdf.get_y() + line_h > PAGE_BOTTOM:
            break

        indent = 0 if item["level"] == 1 else 8
        title = item["title"]
        page_num = str(item["page"])
        number = f"{idx}." if item["level"] == 1 else "-"

        set_rgb(pdf, BLUE_LIGHT if idx % 2 else WHITE, "fill")
        set_rgb(pdf, BORDER, "draw")
        y = pdf.get_y()
        pdf.rect(pdf.l_margin, y, page_w, line_h, style="DF")

        pdf.set_xy(pdf.l_margin + 3 + indent, y + 1.1)
        pdf.set_font("Arial", "B" if item["level"] == 1 else "", 8.5 if item["level"] == 1 else 8)
        set_rgb(pdf, TEXT, "text")
        pdf.cell(12, 4.8, clean_text(number), link=item["link"])
        pdf.cell(page_w - 28 - indent, 4.8, clean_text(title)[:78], link=item["link"])

        pdf.set_font("Arial", "B", 8.5)
        set_rgb(pdf, VIOLET, "text")
        pdf.cell(10, 4.8, page_num, align="R", link=item["link"])
        pdf.set_y(y + line_h)

    pdf.page = current_page


def export_pdf(arg1=None, arg2=None, arg3=None, arg4=None):
    insights, df, num_stats, cat_stats = normalize_export_args(arg1, arg2, arg3, arg4)

    pdf = AutoEDAPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_margins(MARGIN_SIDE, MARGIN_TOP, MARGIN_SIDE)

    # 1) Cover
    pdf.add_page()
    build_cover(pdf, df)

    # 2) Active TOC page (filled after all pages are created)
    _add_toc_page(pdf)

    # 3) Main report pages
    pdf.add_page()
    add_report_section(
        pdf,
        "ABSTRAK",
        fill_color=BLUE,
        intro=(
            "Laporan ini berisi hasil Exploratory Data Analysis (EDA) otomatis dari dataset yang diunggah ke dashboard. "
            "Analisis mencakup ringkasan dataset, kualitas data, statistik deskriptif, analisis variabel numerik dan kategorik, "
            "korelasi, visualisasi, time series, serta insight otomatis. Tujuan report ini adalah membantu pengguna memahami "
            "karakteristik awal data sebelum melakukan analisis lanjutan."
        )
    )
    add_metric_cards(pdf, df)

    add_report_section(
        pdf,
        "PENDAHULUAN",
        fill_color=VIOLET,
        intro=(
            "Auto EDA Analytics dibuat untuk mempermudah proses eksplorasi data secara cepat, rapi, dan otomatis. "
            "Dashboard ini membantu pengguna melihat struktur data, tipe variabel, nilai kosong, duplikasi data, distribusi data, "
            "hingga hubungan antar variabel tanpa harus membuat analisis dari awal secara manual."
        )
    )
    add_note_box(
        pdf,
        "Ruang lingkup laporan meliputi dataset overview, data quality assessment, descriptive statistics, categorical analysis, "
        "correlation analysis, time series summary, visualization summary, intelligent insights, dan kesimpulan akhir.",
        fill_color=PURPLE_LIGHT,
        accent_color=VIOLET
    )

    add_report_section(pdf, "PEMBAHASAN", fill_color=TEAL)

    add_report_section(pdf, "Dataset Overview", fill_color=TEAL, level=2)
    add_table(pdf, make_overview_df(df), max_rows=8, max_cols=2, font_size=7.5)

    add_report_section(pdf, "Data Quality Assessment", fill_color=BLUE, level=2)
    add_text(
        pdf,
        "Bagian ini menunjukkan tipe data, jumlah missing value, persentase missing value, dan jumlah nilai unik pada setiap variabel.",
        font_size=8
    )
    add_table(pdf, make_data_quality_df(df), max_rows=16, max_cols=5, font_size=6.3)

    add_report_section(pdf, "Numerical Statistics", fill_color=VIOLET, level=2)
    if isinstance(num_stats, pd.DataFrame) and not num_stats.empty:
        add_table(pdf, num_stats, max_rows=14, max_cols=5, font_size=6.2)
    else:
        add_text(pdf, "Numerical statistics tidak tersedia karena tidak ada variabel numerik yang valid atau belum dihitung.", font_size=8)

    add_report_section(pdf, "Categorical Statistics", fill_color=TEAL, level=2)
    if isinstance(cat_stats, pd.DataFrame) and not cat_stats.empty:
        add_table(pdf, cat_stats, max_rows=14, max_cols=5, font_size=6.2)
    else:
        add_text(pdf, "Categorical statistics tidak tersedia karena tidak ada variabel kategorik yang valid atau belum dihitung.", font_size=8)

    add_report_section(pdf, "Correlation Analysis", fill_color=PINK, level=2)
    add_text(
        pdf,
        "Matriks korelasi digunakan untuk melihat kekuatan hubungan linier antar variabel numerik. Nilai mendekati 1 atau -1 menunjukkan hubungan semakin kuat, sedangkan nilai mendekati 0 menunjukkan hubungan semakin lemah.",
        font_size=8
    )
    add_table(pdf, make_correlation_matrix(df), max_rows=10, max_cols=6, font_size=5.8)

    add_report_section(pdf, "Time Series Summary", fill_color=AMBER, level=2)
    add_table(pdf, make_time_series_summary(df), max_rows=4, max_cols=2, font_size=7)

    chart_items = generate_pdf_charts(df)
    add_report_section(pdf, "Visualization Summary", fill_color=PINK, level=2)
    if chart_items:
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
    else:
        add_note_box(
            pdf,
            "Visualisasi belum dapat dibuat. Pastikan matplotlib sudah terinstall dan dataset memiliki variabel numerik atau kategorik yang valid.",
            fill_color=PINK_LIGHT,
            accent_color=PINK
        )

    add_report_section(pdf, "Intelligent Insights", fill_color=BLUE, level=2)
    add_insight_cards(pdf, insights, max_items=10)

    add_report_section(
        pdf,
        "PENUTUP",
        fill_color=VIOLET,
        intro=(
            "Berdasarkan hasil EDA otomatis, dataset sudah dirangkum dari sisi struktur, kualitas data, statistik deskriptif, "
            "korelasi, visualisasi, dan insight awal. Report ini dapat digunakan sebagai dasar untuk proses data cleaning lanjutan, "
            "pengambilan keputusan, dashboard monitoring, business intelligence, maupun pengembangan model machine learning."
        )
    )
    add_note_box(
        pdf,
        "Saran: lakukan pengecekan ulang pada kolom dengan missing value tinggi, duplikasi data, tipe data yang belum sesuai, dan variabel yang memiliki hubungan kuat sebelum analisis lanjutan.",
        fill_color=MINT_LIGHT,
        accent_color=TEAL
    )

    # Fill active TOC after all report pages exist.
    _write_toc(pdf)

    pdf_output = pdf.output(dest="S")
    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1", errors="ignore")
    return bytes(pdf_output)


# =========================================================
# INTERACTIVE HTML EXPORT WITH PLOTLY VISUALIZATION
# =========================================================
def _plotly_divs_for_html(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return "<p>Visualisasi interaktif belum tersedia karena dataset kosong.</p>"

    try:
        import plotly.express as px
        import plotly.io as pio
    except Exception:
        return "<p>Plotly belum terinstall. Install dengan: pip install plotly</p>"

    numeric_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)
    divs = []

    # Prepare numeric dataframe conversion for plotly
    converted_df = df.copy()
    for col in numeric_cols:
        converted_df[col] = clean_numeric_series(df[col])

    if numeric_cols:
        col = numeric_cols[0]
        fig = px.histogram(converted_df, x=col, marginal="box", title=f"Interactive Distribution - {col}", template="plotly_white")
        fig.update_layout(height=430, title_x=0.02)
        divs.append(pio.to_html(fig, full_html=False, include_plotlyjs="cdn" if not divs else False))

    if cat_cols:
        col = cat_cols[0]
        counts = df[col].astype(str).value_counts().head(10).reset_index()
        counts.columns = [col, "count"]
        fig = px.bar(counts, x=col, y="count", title=f"Interactive Count Plot - {col}", template="plotly_white")
        fig.update_layout(height=430, title_x=0.02, xaxis_tickangle=-25)
        divs.append(pio.to_html(fig, full_html=False, include_plotlyjs=False if divs else "cdn"))

    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        color_col = cat_cols[0] if cat_cols else None
        fig = px.scatter(converted_df, x=x_col, y=y_col, color=color_col, title=f"Interactive Scatter Plot - {x_col} vs {y_col}", template="plotly_white")
        fig.update_layout(height=430, title_x=0.02)
        divs.append(pio.to_html(fig, full_html=False, include_plotlyjs=False if divs else "cdn"))

        corr = converted_df[numeric_cols[:8]].corr().round(3)
        fig = px.imshow(corr, text_auto=True, title="Interactive Correlation Heatmap", template="plotly_white", aspect="auto")
        fig.update_layout(height=470, title_x=0.02)
        divs.append(pio.to_html(fig, full_html=False, include_plotlyjs=False if divs else "cdn"))

    if not divs:
        return "<p>Visualisasi interaktif belum tersedia karena variabel numerik/kategorik valid tidak ditemukan.</p>"

    return "\n".join([f'<div class="viz-card">{div}</div>' for div in divs])


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
    data_quality_html = dataframe_to_html_table(make_data_quality_df(df), max_rows=25)
    corr_html = dataframe_to_html_table(make_correlation_matrix(df), max_rows=12)
    ts_html = dataframe_to_html_table(make_time_series_summary(df))
    num_html = dataframe_to_html_table(num_stats, max_rows=18)
    cat_html = dataframe_to_html_table(cat_stats, max_rows=18)
    viz_html = _plotly_divs_for_html(df)

    insights_df = make_insights_df(insights)
    insight_cards = ""
    for section in insights_df["Section"].unique():
        section_df = insights_df[insights_df["Section"] == section]
        items = "".join([f"<li>{clean_text(row)}</li>" for row in section_df["Insight"]])
        insight_cards += f"""
        <div class="card">
            <h3>{clean_text(section)}</h3>
            <ul>{items}</ul>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Auto EDA Analytics Report</title>
<style>
:root {{
    --blue:#60a5fa; --violet:#a78bfa; --pink:#f472b6; --teal:#2dd4bf;
    --text:#0f172a; --muted:#64748b; --border:#dbeafe; --soft:#f8faff;
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    background: linear-gradient(135deg, #eff6ff, #f5f3ff, #fff1f2);
    color: var(--text);
}}
nav {{
    position: sticky; top:0; z-index:10;
    background: rgba(255,255,255,.92);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 12px 28px;
    display:flex; gap:14px; flex-wrap:wrap; justify-content:center;
}}
nav a {{
    text-decoration:none; color:#2563eb; font-weight:700; font-size:13px;
    padding:8px 12px; border-radius:999px; background:#eff6ff;
}}
.container {{
    background:white; padding:36px; border-radius:24px;
    box-shadow:0 14px 38px rgba(15,23,42,.13);
    max-width:1180px; margin:32px auto;
}}
.cover {{ text-align:center; padding:24px 10px 10px; }}
h1 {{ color:#2563eb; margin:0; font-size:32px; letter-spacing:-.6px; }}
.subtitle {{ color:var(--muted); font-size:13px; margin:10px 0 24px; }}
h2 {{
    color:white; background:linear-gradient(90deg, var(--blue), var(--violet), var(--pink));
    padding:12px 16px; border-radius:14px; margin-top:34px; font-size:16px;
}}
h3 {{ margin-top:0; }}
.summary {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:24px 0; }}
.summary-card {{ background:#eff6ff; padding:18px; border-radius:18px; text-align:center; border:1px solid #bfdbfe; }}
.summary-card h3 {{ margin:0; color:#2563eb; font-size:12px; }}
.summary-card p {{ margin:8px 0 0; font-size:24px; font-weight:800; }}
.card, .viz-card {{ padding:18px; margin-bottom:16px; border-left:6px solid var(--violet); background:#f5f3ff; border-radius:16px; overflow-x:auto; }}
.card li {{ margin:8px 0; line-height:1.55; }}
.table {{ width:100%; border-collapse:collapse; margin-bottom:20px; font-size:13px; overflow:hidden; border-radius:12px; }}
.table th {{ background:var(--blue); color:white; padding:10px 12px; text-align:left; position:sticky; top:48px; }}
.table td {{ padding:8px 12px; border-bottom:1px solid var(--border); }}
.table tr:nth-child(even) {{ background:var(--soft); }}
p {{ line-height:1.7; }}
@media(max-width:800px) {{ .summary {{ grid-template-columns:repeat(2,1fr); }} .container {{ margin:16px; padding:22px; }} }}
</style>
</head>
<body>
<nav>
  <a href="#cover">Cover</a>
  <a href="#abstrak">Abstrak</a>
  <a href="#pendahuluan">Pendahuluan</a>
  <a href="#pembahasan">Pembahasan</a>
  <a href="#visualisasi">Visualisasi</a>
  <a href="#penutup">Penutup</a>
</nav>
<div class="container">
<section id="cover" class="cover">
<h1>AUTO EDA ANALYTICS REPORT</h1>
<p class="subtitle">Generated At: {datetime.now().strftime('%d %B %Y | %H:%M')}</p>
<div class="summary">
  <div class="summary-card"><h3>Rows</h3><p>{rows}</p></div>
  <div class="summary-card"><h3>Columns</h3><p>{cols}</p></div>
  <div class="summary-card"><h3>Missing</h3><p>{missing}</p></div>
  <div class="summary-card"><h3>Duplicates</h3><p>{duplicate}</p></div>
</div>
</section>
<section id="abstrak"><h2>Abstrak</h2><p>Laporan ini menyajikan hasil Exploratory Data Analysis otomatis dari dataset yang diunggah, meliputi struktur data, kualitas data, statistik deskriptif, korelasi, visualisasi interaktif, dan insight awal.</p></section>
<section id="pendahuluan"><h2>Pendahuluan</h2><p>Auto EDA Analytics membantu pengguna melakukan eksplorasi data secara cepat dan sistematis sebelum melakukan analisis lanjutan, dashboard monitoring, atau modeling.</p></section>
<section id="pembahasan"><h2>Pembahasan - Dataset Overview</h2>{overview_html}
<h2>Data Quality Assessment</h2>{data_quality_html}
<h2>Numerical Statistics</h2>{num_html}
<h2>Categorical Statistics</h2>{cat_html}
<h2>Correlation Analysis</h2>{corr_html}
<h2>Time Series Summary</h2>{ts_html}</section>
<section id="visualisasi"><h2>Visualisasi Interaktif</h2>{viz_html}</section>
<section id="insight"><h2>Intelligent Insights</h2>{insight_cards}</section>
<section id="penutup"><h2>Penutup</h2><p>Dataset telah dianalisis secara otomatis mulai dari kualitas data, statistik, hubungan antar variabel, visualisasi, hingga insight. Hasil ini dapat digunakan sebagai dasar data cleaning, business intelligence, dan analisis lanjutan.</p></section>
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
