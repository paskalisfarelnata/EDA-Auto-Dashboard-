import pandas as pd


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


def format_number(value):
    try:
        if abs(value) >= 1_000_000:
            return f"{value:,.0f}".replace(",", ".")
        if abs(value) >= 1_000:
            return f"{value:,.0f}".replace(",", ".")
        return f"{value:.2f}"
    except Exception:
        return str(value)


def generate_insights(df, numeric_cols=None, date_cols=None, categorical_cols=None):
    insights = []

    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if categorical_cols is None:
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if date_cols is None:
        date_cols = []

    rows, cols = df.shape
    total_missing = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    insights.append("📊 DATASET OVERVIEW")
    insights.append(
        f"Dataset memiliki {rows} baris dan {cols} kolom."
    )
    insights.append(
        f"Terdapat {len(numeric_cols)} variabel numerik, "
        f"{len(categorical_cols)} variabel kategorik, dan "
        f"{len(date_cols)} variabel Date/Datetime."
    )

    if duplicate_rows > 0:
        insights.append(
            f"Ditemukan {duplicate_rows} baris duplikat yang perlu diperhatikan pada proses data cleaning."
        )
    else:
        insights.append(
            "Tidak ditemukan baris duplikat pada dataset."
        )

    insights.append("")
    insights.append("⚠ MISSING VALUE INSIGHT")

    if total_missing > 0:
        missing_percent = (df.isna().sum() / len(df) * 100).sort_values(ascending=False)
        top_missing_col = missing_percent.index[0]
        top_missing_value = missing_percent.iloc[0]

        insights.append(
            f"Dataset memiliki total {total_missing} missing value."
        )
        insights.append(
            f"Kolom dengan missing value tertinggi adalah {top_missing_col} "
            f"sebesar {top_missing_value:.2f}%."
        )
    else:
        insights.append(
            "Tidak ditemukan missing value pada dataset."
        )

    insights.append("")
    insights.append("🔢 NUMERICAL INSIGHT")

    if len(numeric_cols) > 0:
        numeric_summary = {}

        for col in numeric_cols:
            if col in df.columns:
                numeric_data = clean_numeric_series(df[col]).dropna()

                if len(numeric_data) > 0:
                    numeric_summary[col] = {
                        "mean": numeric_data.mean(),
                        "median": numeric_data.median(),
                        "std": numeric_data.std(),
                        "min": numeric_data.min(),
                        "max": numeric_data.max()
                    }

        if numeric_summary:
            first_col = list(numeric_summary.keys())[0]
            first_mean = numeric_summary[first_col]["mean"]
            first_median = numeric_summary[first_col]["median"]

            insights.append(
                f"Variabel {first_col} memiliki rata-rata sebesar {format_number(first_mean)} "
                f"dengan median {format_number(first_median)}."
            )

            std_col = max(
                numeric_summary,
                key=lambda x: numeric_summary[x]["std"]
                if pd.notna(numeric_summary[x]["std"]) else 0
            )

            insights.append(
                f"Variabel dengan variasi terbesar adalah {std_col}."
            )

            outlier_notes = []

            for col, stats in numeric_summary.items():
                if stats["median"] != 0 and pd.notna(stats["median"]):
                    ratio = stats["max"] / stats["median"]

                    if ratio >= 3:
                        outlier_notes.append(col)

            if outlier_notes:
                insights.append(
                    "Terdapat indikasi outlier pada variabel: "
                    + ", ".join(outlier_notes[:5])
                    + "."
                )
            else:
                insights.append(
                    "Tidak ditemukan indikasi outlier ekstrem berdasarkan perbandingan nilai maksimum dan median."
                )
        else:
            insights.append(
                "Tidak ada variabel numerik valid yang dapat dianalisis."
            )
    else:
        insights.append(
            "Tidak terdapat variabel numerik pada dataset."
        )

    insights.append("")
    insights.append("📋 CATEGORICAL INSIGHT")

    valid_categorical = [
        col for col in categorical_cols
        if col in df.columns and df[col].nunique() > 0
    ]

    if len(valid_categorical) > 0:
        for col in valid_categorical[:3]:
            mode_value = df[col].mode(dropna=True)

            if len(mode_value) > 0:
                top_value = mode_value.iloc[0]
                top_count = int((df[col] == top_value).sum())
                top_percent = top_count / len(df) * 100

                insights.append(
                    f"Pada variabel {col}, kategori yang paling dominan adalah "
                    f"{top_value} dengan proporsi {top_percent:.2f}%."
                )
    else:
        insights.append(
            "Tidak terdapat variabel kategorik yang dapat dianalisis."
        )

    insights.append("")
    insights.append("🔗 CORRELATION INSIGHT")

    corr_df = pd.DataFrame()

    for col in numeric_cols:
        if col in df.columns:
            corr_df[col] = clean_numeric_series(df[col])

    corr_df = corr_df.dropna(axis=1, how="all")

    if corr_df.shape[1] >= 2:
        corr_matrix = corr_df.corr().abs()

        corr_pairs = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]

                if pd.notna(corr_value):
                    corr_pairs.append((col1, col2, corr_value))

        if corr_pairs:
            strongest = max(corr_pairs, key=lambda x: x[2])

            strength = "lemah"
            if strongest[2] >= 0.7:
                strength = "kuat"
            elif strongest[2] >= 0.4:
                strength = "sedang"

            insights.append(
                f"Korelasi terkuat ditemukan antara {strongest[0]} dan {strongest[1]} "
                f"dengan nilai korelasi {strongest[2]:.2f}, termasuk kategori {strength}."
            )
        else:
            insights.append(
                "Belum ditemukan pasangan variabel numerik yang memiliki korelasi valid."
            )
    else:
        insights.append(
            "Correlation Insight membutuhkan minimal dua variabel numerik."
        )

    insights.append("")
    insights.append("📈 TIME SERIES INSIGHT")

    if len(date_cols) > 0:
        insights.append(
            f"Dataset memiliki {len(date_cols)} variabel Date/Datetime, yaitu: "
            + ", ".join([str(col) for col in date_cols])
            + "."
        )
        insights.append(
            "Dataset dapat digunakan untuk analisis tren, moving average, rolling mean, dan pola perubahan berdasarkan waktu."
        )
    else:
        insights.append(
            "Time Series Analytics tidak tersedia karena dataset tidak memiliki variabel Date/Datetime."
        )

    insights.append("")
    insights.append("💡 FINAL BUSINESS INSIGHT")

    if total_missing == 0 and duplicate_rows == 0:
        insights.append(
            "Secara umum, dataset memiliki kualitas data yang baik karena tidak ditemukan missing value maupun duplikasi."
        )
    elif total_missing > 0 and duplicate_rows > 0:
        insights.append(
            "Dataset masih memerlukan proses data cleaning karena terdapat missing value dan baris duplikat."
        )
    elif total_missing > 0:
        insights.append(
            "Dataset perlu diperhatikan pada aspek missing value sebelum dilakukan analisis lanjutan."
        )
    else:
        insights.append(
            "Dataset perlu diperhatikan pada aspek duplikasi data sebelum dilakukan analisis lanjutan."
        )

    if len(numeric_cols) > 0 and len(categorical_cols) > 0:
        insights.append(
            "Dataset sudah cukup baik untuk analisis eksploratif karena memiliki kombinasi variabel numerik dan kategorik."
        )

    if len(date_cols) > 0:
        insights.append(
            "Adanya variabel Date/Datetime membuat dataset mendukung analisis time series dan pemantauan tren."
        )

    return insights