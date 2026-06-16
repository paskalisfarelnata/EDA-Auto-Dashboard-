from io import BytesIO
from datetime import datetime
import pandas as pd
from fpdf import FPDF


def clean_text(text):
    text = str(text)

    replacements = {
        "📊": "",
        "⚠": "",
        "🔢": "",
        "📋": "",
        "🔗": "",
        "📈": "",
        "💡": "",
        "✅": "",
        "❌": "",
        "•": "-",
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "’": "'",
        "…": "...",
        "\u2022": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2019": "'"
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
    )

    cleaned = cleaned.str.replace(".", "", regex=False)
    cleaned = cleaned.str.replace(",", ".", regex=False)

    return pd.to_numeric(cleaned, errors="coerce")


def make_overview_df(df):
    date_cols = [
        col for col in df.columns
        if "date" in str(col).lower()
        or "datetime" in str(col).lower()
        or "timestamp" in str(col).lower()
    ]

    numeric_count = 0

    for col in df.columns:
        converted = clean_numeric_series(df[col])

        if converted.notna().sum() >= 2 and col not in date_cols:
            numeric_count += 1

    categorical_count = df.shape[1] - numeric_count - len(date_cols)

    return pd.DataFrame({
        "Metric": [
            "Rows",
            "Columns",
            "Missing Values",
            "Duplicate Rows",
            "Numerical Variables",
            "Categorical Variables",
            "Date/Datetime Variables"
        ],
        "Value": [
            df.shape[0],
            df.shape[1],
            int(df.isna().sum().sum()),
            int(df.duplicated().sum()),
            numeric_count,
            categorical_count,
            len(date_cols)
        ]
    })


def make_data_quality_df(df):
    return pd.DataFrame({
        "Variable": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Count": df.isna().sum().values,
        "Missing Percentage (%)": (df.isna().mean() * 100).round(2).values,
        "Unique Values": df.nunique().values
    })


def make_correlation_matrix(df):
    numeric_df = pd.DataFrame()

    for col in df.columns:
        converted = clean_numeric_series(df[col])

        if converted.notna().sum() >= 2:
            numeric_df[col] = converted

    if numeric_df.shape[1] < 2:
        return pd.DataFrame({
            "Message": [
                "Correlation matrix membutuhkan minimal 2 variabel numerik."
            ]
        })

    return numeric_df.corr().round(3)


def make_time_series_summary(df):
    date_cols = [
        col for col in df.columns
        if "date" in str(col).lower()
        or "datetime" in str(col).lower()
        or "timestamp" in str(col).lower()
    ]

    numeric_cols = []

    for col in df.columns:
        converted = clean_numeric_series(df[col])

        if converted.notna().sum() >= 2 and col not in date_cols:
            numeric_cols.append(col)

    status = (
        "Available"
        if len(date_cols) > 0 and len(numeric_cols) > 0
        else "Not Available"
    )

    return pd.DataFrame({
        "Item": [
            "Time Series Status",
            "Date Columns Detected",
            "Numeric Columns Available"
        ],
        "Value": [
            status,
            ", ".join([str(col) for col in date_cols]) if date_cols else "-",
            ", ".join([str(col) for col in numeric_cols]) if numeric_cols else "-"
        ]
    })


def make_insights_df(insights):
    rows = []
    current_section = "General"

    section_titles = [
        "📊 DATASET OVERVIEW",
        "⚠ MISSING VALUE INSIGHT",
        "🔢 NUMERICAL INSIGHT",
        "📋 CATEGORICAL INSIGHT",
        "🔗 CORRELATION INSIGHT",
        "📈 TIME SERIES INSIGHT",
        "💡 FINAL BUSINESS INSIGHT",
        "DATASET OVERVIEW",
        "MISSING VALUE INSIGHT",
        "NUMERICAL INSIGHT",
        "CATEGORICAL INSIGHT",
        "CORRELATION INSIGHT",
        "TIME SERIES INSIGHT",
        "FINAL BUSINESS INSIGHT"
    ]

    for item in insights:
        item_text = str(item).strip()

        if item_text == "":
            continue

        if item_text in section_titles:
            current_section = clean_text(item_text).strip()

        elif (
            "OVERVIEW" in item_text
            or "INSIGHT" in item_text
            or "FINAL BUSINESS" in item_text
        ):
            current_section = clean_text(item_text).strip()

        else:
            rows.append({
                "Section": current_section,
                "Insight": clean_text(item_text)
            })

    if not rows:
        rows.append({
            "Section": "General",
            "Insight": "Insight tidak tersedia."
        })

    return pd.DataFrame(rows)


def export_excel(df, num_stats, cat_stats, insights=None):
    if insights is None:
        insights = []

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        make_overview_df(df).to_excel(writer, index=False, sheet_name="Overview")
        make_data_quality_df(df).to_excel(writer, index=False, sheet_name="Data Quality")

        if num_stats is not None:
            num_stats.to_excel(writer, index=False, sheet_name="Numerical Stats")

        if cat_stats is not None:
            cat_stats.to_excel(writer, index=False, sheet_name="Categorical Stats")

        make_correlation_matrix(df).to_excel(writer, sheet_name="Correlation Matrix")
        make_time_series_summary(df).to_excel(writer, index=False, sheet_name="Time Series Summary")
        make_insights_df(insights).to_excel(writer, index=False, sheet_name="Insights")
        df.to_excel(writer, index=False, sheet_name="Raw Data")

    return output.getvalue()


def export_csv(df):
    overview_df = make_overview_df(df)
    data_quality_df = make_data_quality_df(df)

    if len(data_quality_df) > 0:
        top_missing = data_quality_df.sort_values(
            "Missing Count",
            ascending=False
        ).iloc[0]

        extra_df = pd.DataFrame({
            "Metric": [
                "Top Missing Column",
                "Top Missing Percentage"
            ],
            "Value": [
                top_missing["Variable"],
                top_missing["Missing Percentage (%)"]
            ]
        })

        summary_df = pd.concat([overview_df, extra_df], ignore_index=True)

    else:
        summary_df = overview_df

    return summary_df.to_csv(index=False).encode("utf-8")


def dataframe_to_html_table(df, max_rows=10):
    if df is None or len(df) == 0:
        return "<p>Data tidak tersedia.</p>"

    return df.head(max_rows).to_html(
        index=False,
        border=0,
        classes="table"
    )


def export_html(insights, df=None, num_stats=None, cat_stats=None):
    rows = df.shape[0] if df is not None else "-"
    cols = df.shape[1] if df is not None else "-"
    missing = int(df.isna().sum().sum()) if df is not None else "-"
    duplicate = int(df.duplicated().sum()) if df is not None else "-"

    overview_html = dataframe_to_html_table(make_overview_df(df)) if df is not None else ""
    data_quality_html = dataframe_to_html_table(make_data_quality_df(df), max_rows=15) if df is not None else ""
    corr_html = dataframe_to_html_table(make_correlation_matrix(df), max_rows=10) if df is not None else ""
    ts_html = dataframe_to_html_table(make_time_series_summary(df)) if df is not None else ""

    num_html = dataframe_to_html_table(num_stats, max_rows=15) if num_stats is not None else ""
    cat_html = dataframe_to_html_table(cat_stats, max_rows=15) if cat_stats is not None else ""

    insights_df = make_insights_df(insights)
    insight_cards = ""

    for section in insights_df["Section"].unique():
        section_df = insights_df[insights_df["Section"] == section]

        items = "".join([
            f"<p>{clean_text(row)}</p>"
            for row in section_df["Insight"]
        ])

        insight_cards += f"""
        <div class="card">
            <h3>{clean_text(section)}</h3>
            {items}
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Auto EDA Analytics Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background-color: #f6f8fb;
                color: #2f3542;
            }}

            .container {{
                background: white;
                padding: 30px;
                border-radius: 14px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            }}

            h1 {{
                text-align: center;
                color: #1f3c88;
            }}

            h2 {{
                color: #1f3c88;
                border-bottom: 2px solid #dfe6f3;
                padding-bottom: 6px;
                margin-top: 28px;
            }}

            .summary {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 14px;
                margin: 25px 0;
            }}

            .summary-card {{
                background: #eef5ff;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }}

            .summary-card h3 {{
                margin: 0;
                color: #1f3c88;
            }}

            .summary-card p {{
                margin: 6px 0 0;
                font-size: 18px;
                font-weight: bold;
            }}

            .card {{
                padding: 16px;
                margin-bottom: 16px;
                border-left: 5px solid #1f77b4;
                background: #eef5ff;
                border-radius: 8px;
            }}

            .table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 22px;
                font-size: 14px;
            }}

            .table th {{
                background: #1f3c88;
                color: white;
                padding: 8px;
                text-align: left;
            }}

            .table td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }}

            p {{
                line-height: 1.7;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <h1>AUTO EDA ANALYTICS REPORT</h1>

            <p style="text-align:center;">
                Generated At: {datetime.now().strftime('%d %B %Y %H:%M')}
            </p>

            <div class="summary">
                <div class="summary-card">
                    <h3>Rows</h3>
                    <p>{rows}</p>
                </div>

                <div class="summary-card">
                    <h3>Columns</h3>
                    <p>{cols}</p>
                </div>

                <div class="summary-card">
                    <h3>Missing</h3>
                    <p>{missing}</p>
                </div>

                <div class="summary-card">
                    <h3>Duplicate</h3>
                    <p>{duplicate}</p>
                </div>
            </div>

            <h2>Dataset Overview</h2>
            {overview_html}

            <h2>Data Quality Assessment</h2>
            {data_quality_html}

            <h2>Numerical Statistics</h2>
            {num_html}

            <h2>Categorical Statistics</h2>
            {cat_html}

            <h2>Correlation Analysis</h2>
            {corr_html}

            <h2>Time Series Summary</h2>
            {ts_html}

            <h2>Intelligent Insights</h2>
            {insight_cards}

            <h2>Final Conclusion</h2>
            <p>
                Dataset telah dianalisis secara otomatis untuk melihat kualitas data,
                distribusi variabel, hubungan antar variabel, serta potensi analisis lanjutan.
                Hasil report ini dapat digunakan sebagai dasar pengambilan keputusan dan
                pengembangan analisis berikutnya.
            </p>
        </div>
    </body>
    </html>
    """

    return html


def add_pdf_section(pdf, title):
    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.set_fill_color(225, 235, 250)
    pdf.cell(0, 9, clean_text(title), ln=True, fill=True)
    pdf.ln(3)


def add_pdf_text(pdf, text):
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, clean_text(text))
    pdf.ln(1)


def add_metric_table(pdf, dataframe):
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(31, 60, 136)
    pdf.set_text_color(255, 255, 255)

    pdf.cell(95, 8, "Metric", border=1, align="C", fill=True)
    pdf.cell(95, 8, "Value", border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)

    for _, row in dataframe.iterrows():
        pdf.cell(95, 8, clean_text(row.iloc[0])[:35], border=1)
        pdf.cell(95, 8, clean_text(row.iloc[1])[:35], border=1)
        pdf.ln()

    pdf.ln(4)


def add_table(pdf, dataframe, max_rows=12, max_cols=5):
    if dataframe is None or len(dataframe) == 0:
        add_pdf_text(pdf, "Data tidak tersedia.")
        return

    df_show = dataframe.head(max_rows).copy()
    df_show = df_show.iloc[:, :max_cols]

    page_width = pdf.w - 2 * pdf.l_margin
    col_width = page_width / max(1, len(df_show.columns))

    pdf.set_font("Arial", "B", 7)
    pdf.set_fill_color(31, 60, 136)
    pdf.set_text_color(255, 255, 255)

    for col in df_show.columns:
        pdf.cell(col_width, 7, clean_text(col)[:18], border=1, align="C", fill=True)

    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 7)

    for _, row in df_show.iterrows():
        for value in row:
            pdf.cell(col_width, 6, clean_text(value)[:18], border=1)
        pdf.ln()

    pdf.ln(4)


def export_pdf(insights, df=None, num_stats=None, cat_stats=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # PAGE 1 - COVER
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 14, "AUTO EDA ANALYTICS REPORT", ln=True, align="C")

    pdf.ln(6)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, "Generated Automatically by Auto EDA Dashboard", ln=True, align="C")
    pdf.cell(0, 8, f"Generated At: {datetime.now().strftime('%d %B %Y %H:%M')}", ln=True, align="C")

    pdf.ln(15)

    if df is not None:
        overview_df = make_overview_df(df)

        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 9, "Dataset Summary", ln=True, align="C")

        pdf.ln(3)
        add_metric_table(pdf, overview_df)

    # PAGE 2 - EXECUTIVE SUMMARY
    pdf.add_page()
    add_pdf_section(pdf, "1. EXECUTIVE SUMMARY")
    add_pdf_text(
        pdf,
        "Laporan ini dibuat secara otomatis menggunakan Auto EDA Analytics Dashboard. "
        "Report ini berfungsi untuk memberikan ringkasan kualitas data, statistik deskriptif, "
        "analisis korelasi, informasi time series, serta insight otomatis dari dataset yang diunggah."
    )

    add_pdf_text(
        pdf,
        "Hasil laporan ini dapat digunakan sebagai dasar awal dalam exploratory data analysis, "
        "pengambilan keputusan, serta pengembangan analisis lanjutan seperti predictive modeling "
        "atau business intelligence."
    )

    if df is not None:
        add_pdf_section(pdf, "2. DATASET OVERVIEW")
        add_metric_table(pdf, make_overview_df(df))

    # PAGE 3 - DATA QUALITY
    if df is not None:
        pdf.add_page()
        add_pdf_section(pdf, "3. DATA QUALITY ASSESSMENT")
        add_pdf_text(
            pdf,
            "Bagian ini menampilkan kualitas data berdasarkan missing value, tipe data, "
            "dan jumlah nilai unik pada setiap variabel."
        )

        data_quality_df = make_data_quality_df(df)
        add_table(pdf, data_quality_df, max_rows=15, max_cols=5)

        total_missing = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        add_pdf_text(
            pdf,
            f"Total missing value pada dataset adalah {total_missing}. "
            f"Jumlah duplicate rows yang terdeteksi adalah {duplicate_rows}."
        )

    # PAGE 4 - NUMERICAL STATISTICS
    pdf.add_page()
    add_pdf_section(pdf, "4. NUMERICAL STATISTICS")

    if num_stats is not None:
        add_table(pdf, num_stats, max_rows=15, max_cols=5)
        add_pdf_text(
            pdf,
            "Numerical statistics digunakan untuk memahami nilai rata-rata, median, minimum, "
            "maksimum, dan pola sebaran pada variabel numerik."
        )
    else:
        add_pdf_text(pdf, "Numerical statistics tidak tersedia.")

    # PAGE 5 - CATEGORICAL STATISTICS
    pdf.add_page()
    add_pdf_section(pdf, "5. CATEGORICAL STATISTICS")

    if cat_stats is not None:
        add_table(pdf, cat_stats, max_rows=15, max_cols=5)
        add_pdf_text(
            pdf,
            "Categorical statistics digunakan untuk melihat kategori dominan, jumlah kategori unik, "
            "dan distribusi frekuensi pada variabel kategorik."
        )
    else:
        add_pdf_text(pdf, "Categorical statistics tidak tersedia.")

    # PAGE 6 - CORRELATION AND TIME SERIES
    if df is not None:
        pdf.add_page()
        add_pdf_section(pdf, "6. CORRELATION ANALYSIS")
        add_pdf_text(
            pdf,
            "Correlation analysis digunakan untuk melihat hubungan antar variabel numerik. "
            "Nilai korelasi mendekati 1 menunjukkan hubungan positif kuat, sedangkan nilai "
            "mendekati 0 menunjukkan hubungan yang lemah."
        )

        add_table(pdf, make_correlation_matrix(df), max_rows=8, max_cols=5)

        add_pdf_section(pdf, "7. TIME SERIES SUMMARY")
        add_pdf_text(
            pdf,
            "Time Series Analysis hanya tersedia jika dataset memiliki variabel Date/Datetime "
            "dan minimal satu variabel numerik yang dapat dianalisis berdasarkan waktu."
        )

        add_table(pdf, make_time_series_summary(df), max_rows=5, max_cols=2)

    # PAGE 7 - INSIGHTS
    pdf.add_page()
    add_pdf_section(pdf, "8. INTELLIGENT INSIGHTS")

    grouped_insights = make_insights_df(insights)

    current_section = None

    for _, row in grouped_insights.iterrows():
        section = clean_text(row["Section"])
        insight = clean_text(row["Insight"])

        if section != current_section:
            current_section = section
            pdf.ln(3)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 7, current_section)

        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 7, insight)

    # PAGE 8 - CONCLUSION
    pdf.add_page()
    add_pdf_section(pdf, "9. FINAL CONCLUSION")
    add_pdf_text(
        pdf,
        "Berdasarkan hasil Auto EDA Analytics, dataset telah dianalisis dari sisi kualitas data, "
        "statistik deskriptif, distribusi variabel, hubungan antar variabel, serta potensi analisis "
        "time series. Report ini memberikan gambaran awal mengenai kondisi dataset sebelum dilakukan "
        "analisis lanjutan."
    )

    add_pdf_text(
        pdf,
        "Apabila dataset memiliki kualitas data yang baik, maka dataset dapat digunakan untuk "
        "analisis lanjutan seperti dashboard monitoring, business intelligence, maupun machine learning. "
        "Jika masih terdapat missing value atau duplikasi, maka proses data cleaning perlu dilakukan "
        "sebelum tahap analisis berikutnya."
    )

    pdf_output = pdf.output(dest="S")

    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1", errors="ignore")

    return bytes(pdf_output)