import pandas as pd
import plotly.graph_objects as go


def shorten_title(text, max_len=15):
    text = str(text)

    if len(text) > max_len:
        return text[:max_len] + "..."

    return text


def get_first_column(df, col_name):
    col_name = str(col_name)

    matched_positions = [
        i for i, col in enumerate(df.columns)
        if str(col) == col_name
    ]

    if len(matched_positions) == 0:
        return None

    first_position = matched_positions[0]
    data = df.iloc[:, first_position]

    if isinstance(data, pd.DataFrame):
        data = data.iloc[:, 0]

    return pd.Series(data).reset_index(drop=True)


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


def prepare_time_series_data(df, date_col, value_col):
    date_data = get_first_column(df, date_col)
    value_data = get_first_column(df, value_col)

    if date_data is None or value_data is None:
        return pd.DataFrame(columns=["Date", "Value"])

    date_series = pd.Series(date_data).reset_index(drop=True)

    converted_date = pd.to_datetime(
        date_series.astype(str),
        errors="coerce"
    )

    valid_date_count = converted_date.notna().sum()

    if valid_date_count < 2:
        return pd.DataFrame(columns=["Date", "Value"])

    value_series = clean_numeric_series(
        pd.Series(value_data).reset_index(drop=True)
    )

    result = pd.DataFrame({
        "Date": converted_date,
        "Value": value_series
    })

    result = result.dropna(subset=["Date", "Value"])
    result = result.sort_values(by="Date")

    return result


def center_title(fig):
    fig.update_layout(
        title=dict(
            text=fig.layout.title.text,
            x=0.5,
            xanchor="center",
            y=0.97,
            yanchor="top",
            font=dict(
                family="Arial",
                size=18,
                color="#2f3542"
            )
        ),
        title_automargin=True,
        margin=dict(
            t=100,
            l=50,
            r=50,
            b=50
        ),
        legend=dict(
            orientation="h",
            y=1.03,
            x=0.5,
            xanchor="center"
        )
    )

    return fig


def trend_line_chart(df, date_col, value_col):
    ts_df = prepare_time_series_data(
        df,
        date_col,
        value_col
    )

    fig = go.Figure()

    if ts_df.empty or len(ts_df) < 2:
        fig.update_layout(
            title="Trend Line (No valid date data)",
            annotations=[
                dict(
                    text="Data Date/Datetime tidak valid atau terlalu sedikit",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    ts_df["Trend"] = (
        ts_df["Value"]
        .rolling(
            window=3,
            min_periods=1
        )
        .mean()
    )

    fig.add_trace(
        go.Scatter(
            x=ts_df["Date"],
            y=ts_df["Value"],
            mode="markers",
            name="Actual Data"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ts_df["Date"],
            y=ts_df["Trend"],
            mode="lines",
            name="Trend Line"
        )
    )

    fig.update_layout(
        title=f"Trend Line ({shorten_title(value_col)})",
        xaxis_title="Date",
        yaxis_title=value_col
    )

    return center_title(fig)


def time_series_chart(df, date_col, value_col, window=3):
    ts_df = prepare_time_series_data(
        df,
        date_col,
        value_col
    )

    fig = go.Figure()

    if ts_df.empty or len(ts_df) < 2:
        fig.update_layout(
            title="Time Series (No valid date data)",
            annotations=[
                dict(
                    text="Data Date/Datetime tidak valid atau terlalu sedikit",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    ts_df["Moving Average"] = (
        ts_df["Value"]
        .rolling(
            window=window,
            min_periods=1
        )
        .mean()
    )

    ts_df["Rolling Mean"] = (
        ts_df["Value"]
        .rolling(
            window=window,
            min_periods=1
        )
        .mean()
    )

    fig.add_trace(
        go.Scatter(
            x=ts_df["Date"],
            y=ts_df["Value"],
            mode="lines+markers",
            name="Original Data"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ts_df["Date"],
            y=ts_df["Moving Average"],
            mode="lines",
            name="Moving Average"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ts_df["Date"],
            y=ts_df["Rolling Mean"],
            mode="lines",
            name="Rolling Mean"
        )
    )

    fig.update_layout(
        title=f"Time Series ({shorten_title(value_col)})",
        xaxis_title="Date",
        yaxis_title=value_col
    )

    return center_title(fig)
