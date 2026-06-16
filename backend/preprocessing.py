import pandas as pd


def dataset_information(df):
    return pd.DataFrame({
        "Variable": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Count": df.isna().sum().values,
        "Missing Percentage (%)": (df.isna().mean() * 100).round(2).values,
        "Unique Values": df.nunique().values
    })


def cleaning_summary(df):
    return pd.DataFrame({
        "Item": [
            "Total Rows",
            "Total Columns",
            "Missing Values",
            "Duplicate Rows"
        ],
        "Value": [
            df.shape[0],
            df.shape[1],
            df.isna().sum().sum(),
            df.duplicated().sum()
        ]
    })


def remove_duplicates(df):
    return df.drop_duplicates()