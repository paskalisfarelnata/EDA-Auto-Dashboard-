import pandas as pd


def categorical_statistics(df):
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    result = []

    for col in cat_cols:
        data = df[col].dropna()

        if len(data) == 0:
            continue

        mode_value = data.mode().iloc[0] if not data.mode().empty else "-"
        mode_freq = (data == mode_value).sum() if mode_value != "-" else 0

        result.append({
            "Variable": col,
            "Unique Categories": data.nunique(),
            "Mode": mode_value,
            "Mode Frequency": mode_freq,
            "Mode Percentage (%)": round((mode_freq / len(data)) * 100, 2),
            "Missing Count": df[col].isna().sum(),
            "Missing Percentage (%)": round(df[col].isna().mean() * 100, 2)
        })

    return pd.DataFrame(result)