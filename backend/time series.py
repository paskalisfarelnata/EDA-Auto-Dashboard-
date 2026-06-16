import pandas as pd
import plotly.express as px


def time_series_chart(df, date_col, value_col, window=3):
    ts_df = df.copy()
    ts_df[date_col] = pd.to_datetime(ts_df[date_col], errors="coerce")
    ts_df = ts_df.dropna(subset=[date_col])
    ts_df = ts_df.sort_values(date_col)

    ts_df["Moving Average"] = ts_df[value_col].rolling(window=window).mean()

    fig = px.line(
        ts_df,
        x=date_col,
        y=[value_col, "Moving Average"],
        title="Time Series Line Chart + Moving Average"
    )

    return fig