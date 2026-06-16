import pandas as pd


def load_data(uploaded_file):
    file_name = uploaded_file.name
    file_ext = file_name.split(".")[-1].lower()

    if file_ext == "csv":
        df = pd.read_csv(uploaded_file)

    elif file_ext == "xlsx":
        df = pd.read_excel(uploaded_file)

    elif file_ext == "txt":
        df = pd.read_csv(uploaded_file, sep=None, engine="python")

    else:
        raise ValueError("Format file tidak didukung.")

    return df, file_ext


def clean_numeric_series(series):
    cleaned = (
        series.astype(str)
        .str.replace("Rp", "", regex=False)
        .str.replace("rp", "", regex=False)
        .str.replace("IDR", "", regex=False)
        .str.replace("idr", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("%", "", regex=False)
    )

    return pd.to_numeric(cleaned, errors="coerce")


def is_valid_numeric_column(series):
    converted_num = clean_numeric_series(series)

    if len(series) == 0:
        return False

    valid_ratio = converted_num.notna().sum() / len(series)

    return valid_ratio >= 0.7


def is_identifier_column(col_name, series):
    col_lower = str(col_name).lower()

    identifier_keywords = [
        "id",
        "number",
        "no",
        "code",
        "kode",
        "phone",
        "telp",
        "card",
        "cc",
        "invoice"
    ]

    if any(keyword in col_lower for keyword in identifier_keywords):
        return True

    try:
        avg_len = series.astype(str).str.len().mean()
        unique_ratio = series.nunique() / len(series)

        if avg_len >= 10 and unique_ratio >= 0.8:
            return True

    except Exception:
        pass

    return False


def detect_columns(df):
    numeric_cols = []
    categorical_cols = []
    date_cols = []

    for col in df.columns:
        col_lower = str(col).lower()
        series = df[col]

        # Date detection berdasarkan nama kolom
        if (
            "date" in col_lower
            or "timestamp" in col_lower
            or "datetime" in col_lower
            or "created_at" in col_lower
            or "updated_at" in col_lower
        ):
            date_cols.append(col)
            continue

        # Numeric detection + auto convert string number
        if is_valid_numeric_column(series):

            if not is_identifier_column(col, series):
                df[col] = clean_numeric_series(series)
                numeric_cols.append(col)

            else:
                categorical_cols.append(col)

        else:
            categorical_cols.append(col)

    numeric_cols = [
        col for col in numeric_cols
        if col not in date_cols
    ]

    categorical_cols = [
        col for col in categorical_cols
        if col not in date_cols
        and col not in numeric_cols
    ]

    return numeric_cols, categorical_cols, date_cols