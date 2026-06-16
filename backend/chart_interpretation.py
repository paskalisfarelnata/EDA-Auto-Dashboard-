import pandas as pd
import numpy as np


# =========================
# BASIC HELPERS
# =========================

def safe_round(value, digits=2):
    try:
        if pd.isna(value):
            return "-"
        return round(float(value), digits)
    except Exception:
        return "-"


def safe_percent(part, total, digits=2):
    try:
        if total == 0 or pd.isna(total):
            return "-"
        return round((float(part) / float(total)) * 100, digits)
    except Exception:
        return "-"


def plain_bullets(items):
    """
    Untuk st.code().
    Output plain text agar ada tombol copy otomatis dan tidak muncul tag HTML.
    """
    if isinstance(items, str):
        items = [items]
    return "\n".join([f"• {item}" for item in items])


def interpretation_box(items):
    """
    Untuk interpretasi per grafik yang tetap tampil sebagai card HTML.
    Baris lanjutan bullet akan rata dengan teks karena memakai <ul><li>.
    """
    if isinstance(items, str):
        items = [items]

    list_html = "".join([f"<li>{item}</li>" for item in items])

    return f"""
    <div class="insight-box interpretation-list-box">
        <b>Interpretasi Grafik:</b>
        <div class="interpretation-content">
            <ul>
                {list_html}
            </ul>
        </div>
    </div>

    <style>
        .interpretation-list-box {{
            overflow-wrap: break-word;
            word-break: normal;
        }}

        .interpretation-content {{
            margin-top: 10px;
            line-height: 1.65;
            font-size: 15px;
        }}

        .interpretation-content ul {{
            margin: 0;
            padding-left: 22px;
        }}

        .interpretation-content li {{
            padding-left: 6px;
            margin-bottom: 7px;
            line-height: 1.65;
        }}
    </style>
    """


def get_numeric_data(df, col):
    return pd.to_numeric(df[col], errors="coerce").dropna()


def get_iqr_info(data):
    q1 = data.quantile(0.25)
    q2 = data.quantile(0.50)
    q3 = data.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = data[(data < lower_bound) | (data > upper_bound)]

    return q1, q2, q3, iqr, lower_bound, upper_bound, outliers


def skew_text(skew_val):
    if pd.isna(skew_val):
        return "belum dapat disimpulkan"
    if skew_val > 1:
        return "sangat miring ke kanan"
    elif skew_val > 0.5:
        return "miring ke kanan"
    elif skew_val < -1:
        return "sangat miring ke kiri"
    elif skew_val < -0.5:
        return "miring ke kiri"
    return "relatif seimbang"


def correlation_strength(corr):
    if pd.isna(corr):
        return "belum dapat disimpulkan"
    if corr >= 0.7:
        return "hubungan positif kuat"
    elif corr >= 0.3:
        return "hubungan positif sedang"
    elif corr > 0:
        return "hubungan positif lemah"
    elif corr <= -0.7:
        return "hubungan negatif kuat"
    elif corr <= -0.3:
        return "hubungan negatif sedang"
    elif corr < 0:
        return "hubungan negatif lemah"
    return "tidak menunjukkan hubungan linear yang jelas"


def get_dominant_range(data, bins=6):
    try:
        counts, edges = np.histogram(data, bins=bins)
        idx = int(np.argmax(counts))
        return safe_round(edges[idx]), safe_round(edges[idx + 1]), int(counts[idx])
    except Exception:
        return "-", "-", 0


def get_top_category_info(df, col):
    data = df[col].dropna()

    if data.empty:
        return None

    counts = data.value_counts()
    total = counts.sum()

    return {
        "counts": counts,
        "total": total,
        "top_category": counts.index[0],
        "top_count": int(counts.iloc[0]),
        "top_percent": safe_percent(int(counts.iloc[0]), total),
        "bottom_category": counts.index[-1],
        "bottom_count": int(counts.iloc[-1]),
        "unique_count": int(data.nunique())
    }


# =========================
# SUMMARY INTERPRETATION
# Dipakai untuk st.code(..., language=None)
# =========================

def summary_numerical_interpretation(df, col):
    data = get_numeric_data(df, col)

    if data.empty:
        return plain_bullets([f"Variabel {col} tidak memiliki data numerik yang valid."])

    mean_val = safe_round(data.mean())
    median_val = safe_round(data.median())
    min_val = safe_round(data.min())
    max_val = safe_round(data.max())
    std_val = safe_round(data.std())
    range_start, range_end, _ = get_dominant_range(data)
    _, _, _, _, _, _, outliers = get_iqr_info(data)

    items = [
        f"Mayoritas nilai {col} berada pada rentang sekitar {range_start} sampai {range_end}.",
        f"Rata-rata sebesar {mean_val} dan median sebesar {median_val}, dengan nilai minimum {min_val} dan maksimum {max_val}.",
        f"Distribusi data {skew_text(data.skew())} dengan standar deviasi {std_val}.",
        f"Terdapat {len(outliers)} outlier yang perlu diperhatikan dalam analisis."
    ]

    return plain_bullets(items)


def summary_categorical_interpretation(df, col):
    info = get_top_category_info(df, col)

    if info is None:
        return plain_bullets([f"Variabel {col} tidak memiliki data kategorik yang valid."])

    if info["top_percent"] != "-" and info["top_percent"] >= 50:
        balance_text = "Distribusi kategori cenderung didominasi oleh satu kategori."
    else:
        balance_text = "Distribusi kategori relatif lebih tersebar."

    items = [
        f"Variabel {col} memiliki {info['unique_count']} kategori unik.",
        f"Kategori paling dominan adalah {info['top_category']} sebanyak {info['top_count']} data atau sekitar {info['top_percent']}%.",
        f"Kategori paling sedikit adalah {info['bottom_category']} sebanyak {info['bottom_count']} data.",
        balance_text
    ]

    return plain_bullets(items)


def summary_time_series_interpretation(df, date_col, value_col):
    try:
        temp = df[[date_col, value_col]].copy()
        temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
        temp[value_col] = pd.to_numeric(temp[value_col], errors="coerce")
        temp = temp.dropna().sort_values(date_col)

        if len(temp) < 2:
            return plain_bullets([f"Time series untuk {value_col} belum dapat dianalisis karena data tanggal terlalu sedikit."])

        first_date = temp[date_col].iloc[0]
        last_date = temp[date_col].iloc[-1]
        first_val = temp[value_col].iloc[0]
        last_val = temp[value_col].iloc[-1]

        change = last_val - first_val
        change_percent = (change / first_val * 100) if first_val != 0 else np.nan

        if change > 0:
            trend = "meningkat"
        elif change < 0:
            trend = "menurun"
        else:
            trend = "stabil"

        max_idx = temp[value_col].idxmax()
        min_idx = temp[value_col].idxmin()

        max_val = temp.loc[max_idx, value_col]
        max_date = temp.loc[max_idx, date_col]

        min_val = temp.loc[min_idx, value_col]
        min_date = temp.loc[min_idx, date_col]

        items = [
            f"Data {value_col} menunjukkan tren {trend} selama periode {first_date.date()} sampai {last_date.date()}.",
            f"Perubahan total sebesar {safe_round(change)} atau sekitar {safe_round(change_percent)}%.",
            f"Nilai tertinggi sebesar {safe_round(max_val)} terjadi pada {max_date.date()}.",
            f"Nilai terendah sebesar {safe_round(min_val)} terjadi pada {min_date.date()}."
        ]

        return plain_bullets(items)

    except Exception:
        return plain_bullets(["Interpretasi time series belum dapat dibuat."])


interpret_numeric_summary = summary_numerical_interpretation
interpret_categorical_summary = summary_categorical_interpretation
interpret_time_series_summary = summary_time_series_interpretation


# =========================
# NUMERICAL VISUALIZATION
# =========================

def interpret_histogram(df, col):
    data = get_numeric_data(df, col)

    if data.empty:
        return interpretation_box([f"Variabel <b>{col}</b> tidak memiliki data numerik yang valid."])

    range_start, range_end, _ = get_dominant_range(data)

    items = [
        f"Mayoritas nilai <b>{col}</b> berada pada rentang sekitar <b>{range_start}</b> sampai <b>{range_end}</b>.",
        f"Distribusi data <b>{skew_text(data.skew())}</b>.",
        f"Nilai minimum sebesar <b>{safe_round(data.min())}</b> dan maksimum sebesar <b>{safe_round(data.max())}</b>."
    ]

    return interpretation_box(items)


def interpret_boxplot(df, col):
    data = get_numeric_data(df, col)

    if data.empty:
        return interpretation_box([f"Boxplot <b>{col}</b> tidak dapat dianalisis karena data kosong."])

    q1, median, q3, iqr, lower_bound, upper_bound, outliers = get_iqr_info(data)

    if len(outliers) > 0:
        outlier_text = f"Ditemukan <b>{len(outliers)}</b> outlier yang perlu diperhatikan."
    else:
        outlier_text = "Tidak ditemukan outlier berdasarkan batas IQR."

    items = [
        f"Median <b>{col}</b> berada pada nilai <b>{safe_round(median)}</b>.",
        f"Sebagian besar data berada di antara Q1 <b>{safe_round(q1)}</b> dan Q3 <b>{safe_round(q3)}</b>.",
        outlier_text
    ]

    return interpretation_box(items)


def interpret_density(df, col):
    data = get_numeric_data(df, col)

    if data.empty:
        return interpretation_box([f"Density plot <b>{col}</b> tidak dapat dianalisis karena data kosong."])

    range_start, range_end, _ = get_dominant_range(data)

    items = [
        f"Kepadatan nilai <b>{col}</b> paling terlihat pada rentang sekitar <b>{range_start}</b> sampai <b>{range_end}</b>.",
        f"Rata-rata sebesar <b>{safe_round(data.mean())}</b> dan median sebesar <b>{safe_round(data.median())}</b>.",
        f"Bentuk distribusi data <b>{skew_text(data.skew())}</b>."
    ]

    return interpretation_box(items)


def interpret_qq_plot(df, col):
    data = get_numeric_data(df, col)

    if len(data) < 3:
        return interpretation_box([f"QQ Plot <b>{col}</b> belum dapat dianalisis karena jumlah data terlalu sedikit."])

    skew_val = data.skew()
    _, _, _, _, _, _, outliers = get_iqr_info(data)

    if abs(skew_val) < 0.5 and len(outliers) == 0:
        normal_text = "cukup mendekati distribusi normal"
    elif skew_val > 0:
        normal_text = "belum normal sepenuhnya karena cenderung miring ke kanan"
    else:
        normal_text = "belum normal sepenuhnya karena cenderung miring ke kiri"

    items = [
        f"QQ Plot menunjukkan bahwa <b>{col}</b> <b>{normal_text}</b>.",
        f"Nilai skewness sebesar <b>{safe_round(skew_val)}</b>.",
        f"Terdapat <b>{len(outliers)}</b> outlier yang dapat memengaruhi pola normalitas."
    ]

    return interpretation_box(items)


def interpret_violin(df, col):
    data = get_numeric_data(df, col)

    if data.empty:
        return interpretation_box([f"Violin plot <b>{col}</b> tidak dapat dianalisis karena data kosong."])

    _, median, _, _, _, _, outliers = get_iqr_info(data)
    range_start, range_end, _ = get_dominant_range(data)

    items = [
        f"Mayoritas nilai <b>{col}</b> terkonsentrasi pada rentang sekitar <b>{range_start}</b> sampai <b>{range_end}</b>.",
        f"Median sebesar <b>{safe_round(median)}</b> dan rata-rata sebesar <b>{safe_round(data.mean())}</b>.",
        f"Distribusi <b>{skew_text(data.skew())}</b> dengan <b>{len(outliers)}</b> kemungkinan outlier."
    ]

    return interpretation_box(items)


def interpret_numeric(df, col):
    return summary_numerical_interpretation(df, col)


# =========================
# CATEGORICAL VISUALIZATION
# =========================

def interpret_bar_chart(df, col):
    info = get_top_category_info(df, col)

    if info is None:
        return interpretation_box([f"Bar chart <b>{col}</b> tidak dapat dianalisis karena data kosong."])

    items = [
        f"Kategori dominan pada <b>{col}</b> adalah <b>{info['top_category']}</b> sebanyak <b>{info['top_count']}</b> data.",
        f"Proporsi kategori dominan mencapai sekitar <b>{info['top_percent']}%</b> dari total data valid.",
        f"Kategori paling sedikit adalah <b>{info['bottom_category']}</b> dengan <b>{info['bottom_count']}</b> data."
    ]

    return interpretation_box(items)


def interpret_pie_chart(df, col):
    info = get_top_category_info(df, col)

    if info is None:
        return interpretation_box([f"Pie chart <b>{col}</b> tidak dapat dianalisis karena data kosong."])

    balance_text = "distribusi kategori cukup seimbang"
    if info["top_percent"] != "-" and info["top_percent"] >= 50:
        balance_text = "distribusi kategori cenderung didominasi satu kategori"

    items = [
        f"Kategori terbesar adalah <b>{info['top_category']}</b> dengan proporsi sekitar <b>{info['top_percent']}%</b>.",
        f"Jumlah kategori unik pada variabel <b>{col}</b> adalah <b>{info['unique_count']}</b> kategori.",
        f"Secara proporsi, <b>{balance_text}</b>."
    ]

    return interpretation_box(items)


def interpret_count_plot(df, col):
    info = get_top_category_info(df, col)

    if info is None:
        return interpretation_box([f"Count plot <b>{col}</b> tidak dapat dianalisis karena data kosong."])

    items = [
        f"Kategori yang paling sering muncul adalah <b>{info['top_category']}</b> sebanyak <b>{info['top_count']}</b> data.",
        f"Kategori tersebut mewakili sekitar <b>{info['top_percent']}%</b> dari total data valid.",
        f"Distribusi kategori <b>{col}</b> dapat terlihat dari perbedaan tinggi tiap batang."
    ]

    return interpretation_box(items)


def interpret_pareto(df, col):
    info = get_top_category_info(df, col)

    if info is None:
        return interpretation_box([f"Pareto chart <b>{col}</b> tidak dapat dianalisis karena data kosong."])

    counts = info["counts"]
    total = info["total"]
    cumulative = (counts.cumsum() / total) * 100

    top_80_count = int((cumulative <= 80).sum())
    if top_80_count == 0:
        top_80_count = 1

    items = [
        f"Kategori terbesar adalah <b>{info['top_category']}</b> dengan <b>{info['top_count']}</b> data atau sekitar <b>{info['top_percent']}%</b>.",
        f"Sekitar <b>{top_80_count}</b> kategori teratas memberi kontribusi terbesar terhadap total distribusi.",
        "Pareto membantu menentukan kategori utama yang paling perlu diperhatikan."
    ]

    return interpretation_box(items)


def interpret_categorical(df, col):
    return summary_categorical_interpretation(df, col)


# =========================
# BIVARIATE & MULTIVARIATE
# =========================

def interpret_scatter_plot(df, x_col, y_col):
    try:
        temp = df[[x_col, y_col]].apply(pd.to_numeric, errors="coerce").dropna()

        if len(temp) < 2:
            return interpretation_box([f"Scatter plot <b>{x_col}</b> dan <b>{y_col}</b> belum dapat dianalisis karena data valid terlalu sedikit."])

        corr = temp[x_col].corr(temp[y_col])

        if corr > 0:
            trend_text = f"Semakin besar <b>{x_col}</b>, <b>{y_col}</b> cenderung meningkat."
        elif corr < 0:
            trend_text = f"Semakin besar <b>{x_col}</b>, <b>{y_col}</b> cenderung menurun."
        else:
            trend_text = f"Tidak terlihat pola linear yang jelas antara <b>{x_col}</b> dan <b>{y_col}</b>."

        items = [
            f"Korelasi antara <b>{x_col}</b> dan <b>{y_col}</b> sebesar <b>{safe_round(corr, 3)}</b>.",
            f"Hubungan keduanya termasuk <b>{correlation_strength(corr)}</b>.",
            trend_text
        ]

        return interpretation_box(items)

    except Exception:
        return interpretation_box([f"Scatter plot antara <b>{x_col}</b> dan <b>{y_col}</b> belum dapat diinterpretasikan."])


def interpret_regression_plot(df, x_col, y_col):
    try:
        temp = df[[x_col, y_col]].apply(pd.to_numeric, errors="coerce").dropna()

        if len(temp) < 2:
            return interpretation_box([f"Regression plot <b>{x_col}</b> dan <b>{y_col}</b> belum dapat dianalisis karena data valid terlalu sedikit."])

        corr = temp[x_col].corr(temp[y_col])

        if corr > 0:
            direction = "garis regresi menunjukkan tren naik"
        elif corr < 0:
            direction = "garis regresi menunjukkan tren turun"
        else:
            direction = "garis regresi cenderung datar"

        items = [
            f"<b>{direction}</b> antara <b>{x_col}</b> dan <b>{y_col}</b>.",
            f"Korelasi sebesar <b>{safe_round(corr, 3)}</b>, termasuk <b>{correlation_strength(corr)}</b>.",
            "Pola hubungan belum tentu kuat jika titik data masih menyebar jauh dari garis regresi."
        ]

        return interpretation_box(items)

    except Exception:
        return interpretation_box([f"Regression plot antara <b>{x_col}</b> dan <b>{y_col}</b> belum dapat diinterpretasikan."])


def interpret_correlation(df, x_col, y_col):
    return interpret_scatter_plot(df, x_col, y_col)


def interpret_heatmap(df, numeric_cols):
    try:
        if len(numeric_cols) < 2:
            return interpretation_box(["Correlation heatmap membutuhkan minimal dua variabel numerik."])

        temp = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
        corr_matrix = temp.corr()

        pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                value = corr_matrix.iloc[i, j]
                if pd.notna(value):
                    pairs.append((col1, col2, value, abs(value)))

        if not pairs:
            return interpretation_box(["Belum ada pasangan variabel numerik yang dapat dihitung korelasinya."])

        strongest = max(pairs, key=lambda x: x[3])

        items = [
            f"Korelasi terkuat terdapat antara <b>{strongest[0]}</b> dan <b>{strongest[1]}</b>.",
            f"Nilai korelasinya sebesar <b>{safe_round(strongest[2], 3)}</b>, termasuk <b>{correlation_strength(strongest[2])}</b>.",
            "Variabel dengan korelasi rendah menunjukkan hubungan linear yang tidak terlalu kuat."
        ]

        return interpretation_box(items)

    except Exception:
        return interpretation_box(["Interpretasi correlation heatmap belum dapat dibuat."])


def interpret_pair_plot(df, numeric_cols):
    try:
        if len(numeric_cols) < 2:
            return interpretation_box(["Pair plot membutuhkan minimal dua variabel numerik."])

        valid_cols = numeric_cols[:5]
        temp = df[valid_cols].apply(pd.to_numeric, errors="coerce")
        corr_matrix = temp.corr()

        pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                value = corr_matrix.iloc[i, j]
                if pd.notna(value):
                    pairs.append((col1, col2, value, abs(value)))

        if pairs:
            strongest = max(pairs, key=lambda x: x[3])
            items = [
                f"Pasangan variabel yang paling berkorelasi adalah <b>{strongest[0]}</b> dan <b>{strongest[1]}</b>.",
                f"Nilai korelasinya sebesar <b>{safe_round(strongest[2], 3)}</b>.",
                "Variabel lain menunjukkan hubungan yang lebih lemah."
            ]
        else:
            items = [
                "Belum terlihat pasangan variabel dengan pola linear yang kuat.",
                "Sebagian besar titik menyebar tanpa pola linear yang jelas.",
                f"Variabel yang dibandingkan adalah <b>{', '.join(valid_cols)}</b>."
            ]

        return interpretation_box(items)

    except Exception:
        return interpretation_box(["Interpretasi pair plot belum dapat dibuat."])


def interpret_bubble_chart(df, x_col, y_col, size_col):
    try:
        temp = df[[x_col, y_col, size_col]].apply(pd.to_numeric, errors="coerce").dropna()

        if len(temp) < 2:
            return interpretation_box(["Bubble chart belum dapat dianalisis karena data valid terlalu sedikit."])

        corr_xy = temp[x_col].corr(temp[y_col])

        items = [
            f"Hubungan antara <b>{x_col}</b> dan <b>{y_col}</b> memiliki korelasi <b>{safe_round(corr_xy, 3)}</b>.",
            f"Hubungan yang terbentuk termasuk <b>{correlation_strength(corr_xy)}</b>.",
            f"Semakin besar nilai <b>{size_col}</b>, ukuran bubble akan semakin besar."
        ]

        return interpretation_box(items)

    except Exception:
        return interpretation_box(["Interpretasi bubble chart belum dapat dibuat."])


# =========================
# CATEGORICAL VS NUMERICAL
# =========================

def interpret_boxplot_by_category(df, cat_col, num_col):
    return interpret_category_numeric(df, cat_col, num_col, chart_name="Boxplot by Category")


def interpret_violin_by_category(df, cat_col, num_col):
    return interpret_category_numeric(df, cat_col, num_col, chart_name="Violin by Category")


def interpret_grouped_bar(df, cat_col, num_col):
    return interpret_category_numeric(df, cat_col, num_col, chart_name="Grouped Bar Chart")


def interpret_strip_plot(df, cat_col, num_col):
    return interpret_category_numeric(df, cat_col, num_col, chart_name="Strip Plot")


def interpret_category_numeric(df, cat_col, num_col, chart_name="Categorical vs Numerical"):
    try:
        temp = df[[cat_col, num_col]].copy()
        temp[num_col] = pd.to_numeric(temp[num_col], errors="coerce")
        temp = temp.dropna()

        if temp.empty:
            return interpretation_box([f"Hubungan antara <b>{cat_col}</b> dan <b>{num_col}</b> belum dapat dianalisis karena data tidak valid."])

        group_mean = temp.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
        group_count = temp.groupby(cat_col)[num_col].count().sort_values(ascending=False)

        top_group = group_mean.index[0]
        top_value = safe_round(group_mean.iloc[0])

        low_group = group_mean.index[-1]
        low_value = safe_round(group_mean.iloc[-1])

        most_data_group = group_count.index[0]
        most_data_count = int(group_count.iloc[0])

        items = [
            f"Kategori <b>{top_group}</b> memiliki rata-rata <b>{num_col}</b> tertinggi sebesar <b>{top_value}</b>.",
            f"Kategori <b>{low_group}</b> memiliki rata-rata terendah sebesar <b>{low_value}</b>.",
            f"Jumlah data terbanyak terdapat pada kategori <b>{most_data_group}</b> sebanyak <b>{most_data_count}</b> data.",
            f"Perbedaan rata-rata menunjukkan bahwa <b>{num_col}</b> cenderung berbeda antar kategori <b>{cat_col}</b>."
        ]

        return interpretation_box(items)

    except Exception:
        return interpretation_box([f"Interpretasi hubungan <b>{cat_col}</b> dan <b>{num_col}</b> belum dapat dibuat."])


# =========================
# TIME SERIES
# =========================

def _summary_to_html_box(summary_text):
    items = [
        line.replace("• ", "").strip()
        for line in str(summary_text).splitlines()
        if line.strip()
    ]
    return interpretation_box(items)


def interpret_trend_line(df, date_col, value_col):
    return _summary_to_html_box(summary_time_series_interpretation(df, date_col, value_col))


def interpret_time_series_chart(df, date_col, value_col):
    return _summary_to_html_box(summary_time_series_interpretation(df, date_col, value_col))


def interpret_moving_average(df, date_col, value_col):
    return _summary_to_html_box(summary_time_series_interpretation(df, date_col, value_col))


def interpret_time_series(df, date_col, value_col, chart_name="Time Series"):
    return summary_time_series_interpretation(df, date_col, value_col)
