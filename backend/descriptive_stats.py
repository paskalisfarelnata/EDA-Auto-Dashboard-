import pandas as pd
from scipy import stats


def numerical_statistics(df):
    numeric_cols = df.select_dtypes(include="number").columns
    result = []

    for col in numeric_cols:
        data = df[col].dropna()

        if len(data) == 0:
            continue

        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        outliers = ((data < q1 - 1.5 * iqr) | (data > q3 + 1.5 * iqr)).sum()

        if len(data) >= 8:
            try:
                p_value = stats.normaltest(data).pvalue
                normality = "Normal" if p_value > 0.05 else "Not Normal"
            except Exception:
                normality = "Cannot Test"
        else:
            normality = "Data Too Small"

        result.append({
            "Variable": col,
            "Mean": round(data.mean(), 3),
            "Median": round(data.median(), 3),
            "Minimum": round(data.min(), 3),
            "Maximum": round(data.max(), 3),
            "Std Dev": round(data.std(), 3),
            "Variance": round(data.var(), 3),
            "Mode": data.mode().iloc[0] if not data.mode().empty else "-",
            "Skewness": round(data.skew(), 3),
            "Kurtosis": round(data.kurtosis(), 3),
            "Missing Count": df[col].isna().sum(),
            "Missing Percentage (%)": round(df[col].isna().mean() * 100, 2),
            "Outliers": int(outliers),
            "Normality Test": normality
        })

    return pd.DataFrame(result)