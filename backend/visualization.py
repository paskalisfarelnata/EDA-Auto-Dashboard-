import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# =========================
# BRIGHT PASTEL THEME
# =========================

PASTEL_COLORS = [
    "#38BDF8",  # sky
    "#A78BFA",  # violet
    "#FB7185",  # rose
    "#2DD4BF",  # teal
    "#FACC15",  # yellow
    "#4ADE80",  # green
    "#FB923C",  # orange
    "#C084FC",  # purple
]

PASTEL_HEATMAP = [
    "#EFF6FF",
    "#BAE6FD",
    "#38BDF8",
    "#A78BFA",
    "#FB7185",
]

PASTEL_CONTINUOUS = [
    "#EFF6FF",
    "#DBEAFE",
    "#93C5FD",
    "#A78BFA",
    "#FB7185",
]

DASHBOARD_TEMPLATE = "plotly_white"


def apply_pastel_theme(fig, height=520, title_size=18):
    """Merapikan semua visualisasi agar pastel cerah, soft, dan tidak monoton."""
    fig.update_layout(
        template=DASHBOARD_TEMPLATE,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.92)",
        font=dict(
            family="Arial",
            size=12,
            color="#334155"
        ),
        title=dict(
            text=fig.layout.title.text if fig.layout.title.text else "",
            x=0.5,
            xanchor="center",
            y=0.97,
            yanchor="top",
            font=dict(
                family="Arial",
                size=title_size,
                color="#0F172A"
            )
        ),
        title_automargin=True,
        margin=dict(
            t=90,
            l=55,
            r=45,
            b=60
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            font=dict(size=11, color="#475569")
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.18)",
        zeroline=False,
        linecolor="rgba(148,163,184,0.35)",
        tickfont=dict(color="#475569")
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.18)",
        zeroline=False,
        linecolor="rgba(148,163,184,0.35)",
        tickfont=dict(color="#475569")
    )

    return fig


def apply_marker_style(fig, color=None):
    """Memberi warna pastel pada chart marker/bar."""
    chosen_color = color or PASTEL_COLORS[0]

    try:
        fig.update_traces(
            marker=dict(
                color=chosen_color,
                line=dict(color="white", width=1.2)
            ),
            opacity=0.92
        )
    except Exception:
        pass

    return fig


def apply_multi_color(fig):
    """Memberi variasi warna pastel untuk bar/pie/area multi kategori."""
    try:
        fig.update_traces(
            marker=dict(
                color=PASTEL_COLORS,
                line=dict(color="white", width=1.2)
            ),
            opacity=0.94
        )
    except Exception:
        pass

    return fig


def shorten_title(text, max_len=15):
    text = str(text)

    if len(text) > max_len:
        return text[:max_len] + "..."

    return text


def center_title(fig):
    return apply_pastel_theme(fig)
def force_numeric(df, cols):
    temp_df = df.copy()

    for col in cols:
        if col not in temp_df.columns:
            continue

        cleaned = (
            temp_df[col]
            .astype(str)
            .str.replace("Rp", "", regex=False)
            .str.replace("rp", "", regex=False)
            .str.replace("IDR", "", regex=False)
            .str.replace("idr", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace("%", "", regex=False)
        )

        cleaned = cleaned.str.replace(".", "", regex=False)
        cleaned = cleaned.str.replace(",", ".", regex=False)

        temp_df[col] = pd.to_numeric(
            cleaned,
            errors="coerce"
        )

    temp_df = temp_df.dropna(
        subset=[
            col for col in cols
            if col in temp_df.columns
        ]
    )

    return temp_df


# =========================
# DASHBOARD CHARTS
# =========================

def data_type_chart(df):
    type_count = df.dtypes.astype(str).value_counts().reset_index()
    type_count.columns = ["Data Type", "Count"]

    fig = px.pie(
        type_count,
        names="Data Type",
        values="Count",
        hole=0.45,
        title="Data Type Distribution",
        color_discrete_sequence=PASTEL_COLORS
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(t=90, b=80, l=20, r=20),
        height=360
    )

    return center_title(fig)

def missing_chart(df):
    missing = df.isna().sum().reset_index()
    missing.columns = ["Variable", "Missing"]

    fig = px.bar(
        missing,
        x="Missing",
        y="Variable",
        orientation="h",
        title="Missing Value Summary"
    )

    return center_title(fig)


# =========================
# NUMERICAL VISUALIZATION
# =========================

def histogram(df, col):
    temp_df = force_numeric(df, [col])

    fig = px.histogram(
        temp_df,
        x=col,
        title=f"Histogram ({shorten_title(col)})",
        nbins=30,
        color_discrete_sequence=[PASTEL_COLORS[0]]
    )

    return center_title(fig)


def boxplot(df, col):
    temp_df = force_numeric(df, [col])

    fig = px.box(
        temp_df,
        y=col,
        title=f"Boxplot ({shorten_title(col)})",
        color_discrete_sequence=[PASTEL_COLORS[3]]
    )

    return center_title(fig)


def density_plot(df, col):
    temp_df = force_numeric(df, [col])

    fig = px.histogram(
        temp_df,
        x=col,
        histnorm="density",
        marginal="rug",
        title=f"Density Plot ({shorten_title(col)})",
        color_discrete_sequence=[PASTEL_COLORS[1]]
    )

    return center_title(fig)


def qq_plot(df, col):
    temp_df = force_numeric(df, [col])
    data = temp_df[col].dropna()

    if len(data) < 2:
        fig = go.Figure()
        fig.update_layout(
            title=f"QQ Plot ({shorten_title(col)})",
            annotations=[
                dict(
                    text="Data terlalu sedikit untuk QQ Plot",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    osm, osr = stats.probplot(data, dist="norm", fit=False)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=osm,
            y=osr,
            mode="markers",
            name="Data Points",
            marker=dict(color=PASTEL_COLORS[0], size=7, line=dict(color="white", width=1))
        )
    )

    fig.add_trace(
        go.Scatter(
            x=osm,
            y=osm,
            mode="lines",
            name="Normal Line",
            line=dict(color=PASTEL_COLORS[2], width=3)
        )
    )

    fig.update_layout(
        title=f"QQ Plot ({shorten_title(col)})",
        xaxis_title="Theoretical Quantiles",
        yaxis_title="Sample Quantiles"
    )

    return center_title(fig)


def violin_plot(df, col):
    temp_df = force_numeric(df, [col])

    fig = px.violin(
        temp_df,
        y=col,
        box=True,
        points="all",
        title=f"Violin Plot ({shorten_title(col)})",
        color_discrete_sequence=[PASTEL_COLORS[2]]
    )

    return center_title(fig)


# =========================
# CATEGORICAL VISUALIZATION
# =========================

def bar_chart(df, col):
    count_df = df[col].value_counts().reset_index()
    count_df.columns = [col, "Count"]

    fig = px.bar(
        count_df,
        x=col,
        y="Count",
        title=f"Bar Chart ({shorten_title(col)})",
        color_discrete_sequence=PASTEL_COLORS
    )

    return center_title(fig)


def pie_chart(df, col):
    count_df = df[col].value_counts().reset_index()
    count_df.columns = [col, "Count"]

    fig = px.pie(
        count_df,
        names=col,
        values="Count",
        hole=0.35,
        color_discrete_sequence=PASTEL_COLORS
    )

    category_count = len(count_df)
    show_legend = category_count <= 6

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        insidetextorientation="radial",
        textfont_size=12,
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
    )

    fig.update_layout(
        title=dict(
            text=f"Pie Chart ({shorten_title(col)})",
            x=0.5,
            xanchor="center",
            y=0.98,
            yanchor="top",
            font=dict(
                family="Arial",
                size=18,
                color="#2f3542"
            )
        ),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(
            t=90,
            b=160,
            l=30,
            r=30
        ),
        height=460
    )

    fig.update_traces(
        domain=dict(
            x=[0.08, 0.92],
            y=[0.18, 0.88]
        )
    )

    return fig

def count_plot(df, col):
    count_df = df[col].value_counts().reset_index()
    count_df.columns = [col, "Count"]

    fig = px.bar(
        count_df,
        x=col,
        y="Count",
        title=f"Count Plot ({shorten_title(col)})",
        color_discrete_sequence=PASTEL_COLORS
    )

    return center_title(fig)


def pareto_chart(df, col):
    count_df = df[col].value_counts().reset_index()
    count_df.columns = [col, "Count"]

    count_df["Cumulative %"] = (
        count_df["Count"].cumsum()
        / count_df["Count"].sum()
        * 100
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=count_df[col],
            y=count_df["Count"],
            name="Count",
            marker=dict(color=PASTEL_COLORS, line=dict(color="white", width=1.2))
        )
    )

    fig.add_trace(
        go.Scatter(
            x=count_df[col],
            y=count_df["Cumulative %"],
            name="Cumulative %",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color=PASTEL_COLORS[2], width=3),
            marker=dict(color=PASTEL_COLORS[1], size=8, line=dict(color="white", width=1))
        )
    )

    fig.update_layout(
        title=f"Pareto Chart ({shorten_title(col)})",
        yaxis=dict(title="Count"),
        yaxis2=dict(
            title="Cumulative %",
            overlaying="y",
            side="right",
            range=[0, 100]
        )
    )

    return center_title(fig)


# =========================
# BIVARIATE & MULTIVARIATE
# =========================

def scatter_plot(df, x_col, y_col):
    temp_df = force_numeric(df, [x_col, y_col])

    if temp_df.empty or len(temp_df) < 2:
        fig = go.Figure()
        fig.update_layout(
            title=f"Scatter ({shorten_title(x_col)} vs {shorten_title(y_col)})",
            annotations=[
                dict(
                    text="Data numerik tidak cukup untuk scatter plot",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    fig = px.scatter(
        temp_df,
        x=x_col,
        y=y_col,
        title=f"Scatter ({shorten_title(x_col)} vs {shorten_title(y_col)})",
        color_discrete_sequence=[PASTEL_COLORS[0]]
    )

    return center_title(fig)


def regression_plot(df, x_col, y_col):
    temp_df = force_numeric(df, [x_col, y_col])

    if temp_df.empty or len(temp_df) < 2:
        fig = go.Figure()
        fig.update_layout(
            title=f"Regression ({shorten_title(x_col)} vs {shorten_title(y_col)})",
            annotations=[
                dict(
                    text="Data numerik tidak cukup untuk regression plot",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    fig = px.scatter(
        temp_df,
        x=x_col,
        y=y_col,
        trendline="ols",
        title=f"Regression ({shorten_title(x_col)} vs {shorten_title(y_col)})",
        color_discrete_sequence=[PASTEL_COLORS[1]]
    )

    return center_title(fig)


def correlation_heatmap(df, numeric_cols):
    available_cols = [
        col for col in numeric_cols
        if col in df.columns
    ]

    temp_df = force_numeric(df, available_cols)

    valid_cols = [
        col for col in available_cols
        if temp_df[col].notna().sum() >= 2
    ]

    if len(valid_cols) < 2:
        fig = go.Figure()
        fig.update_layout(
            title="Correlation Heatmap",
            annotations=[
                dict(
                    text="Minimal 2 kolom numerik valid dibutuhkan",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    corr = temp_df[valid_cols].corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale=PASTEL_HEATMAP,
        title="Correlation Heatmap"
    )

    return center_title(fig)


def pair_plot(df, numeric_cols):
    available_cols = [
        col for col in numeric_cols
        if col in df.columns
    ]

    temp_df = force_numeric(df, available_cols)

    valid_cols = [
        col for col in available_cols
        if temp_df[col].notna().sum() >= 2
    ]

    selected_cols = valid_cols[:5]

    if len(selected_cols) < 2:
        fig = go.Figure()
        fig.update_layout(
            title="Pair Plot",
            annotations=[
                dict(
                    text="Minimal 2 kolom numerik valid dibutuhkan",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    fig = px.scatter_matrix(
        temp_df,
        dimensions=selected_cols,
        title="Pair Plot",
        color_discrete_sequence=PASTEL_COLORS
    )

    return center_title(fig)


def bubble_chart(df, x_col, y_col, size_col):
    temp_df = force_numeric(df, [x_col, y_col, size_col])

    if temp_df.empty or len(temp_df) < 2:
        fig = go.Figure()
        fig.update_layout(
            title=f"Bubble ({shorten_title(x_col)}, {shorten_title(y_col)})",
            annotations=[
                dict(
                    text="Data numerik tidak cukup untuk bubble chart",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    fig = px.scatter(
        temp_df,
        x=x_col,
        y=y_col,
        size=size_col,
        title=f"Bubble ({shorten_title(x_col)}, {shorten_title(y_col)})",
        color_discrete_sequence=[PASTEL_COLORS[2]]
    )

    return center_title(fig)


# =========================
# CATEGORICAL VS NUMERICAL
# =========================

def boxplot_by_category(df, cat_col, num_col):
    temp_df = df[[cat_col, num_col]].copy()
    numeric_df = force_numeric(temp_df, [num_col])

    if numeric_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"Boxplot ({shorten_title(num_col)} by {shorten_title(cat_col)})",
            annotations=[
                dict(
                    text="Data numerik tidak cukup untuk boxplot",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    fig = px.box(
        numeric_df,
        x=cat_col,
        y=num_col,
        title=f"Boxplot ({shorten_title(num_col)} by {shorten_title(cat_col)})",
        color_discrete_sequence=PASTEL_COLORS
    )

    return center_title(fig)


def violin_by_category(df, cat_col, num_col):
    temp_df = df[[cat_col, num_col]].copy()
    numeric_df = force_numeric(temp_df, [num_col])

    if numeric_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"Violin ({shorten_title(num_col)} by {shorten_title(cat_col)})",
            annotations=[
                dict(
                    text="Data numerik tidak cukup untuk violin plot",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    fig = px.violin(
        numeric_df,
        x=cat_col,
        y=num_col,
        box=True,
        points="all",
        title=f"Violin ({shorten_title(num_col)} by {shorten_title(cat_col)})",
        color_discrete_sequence=PASTEL_COLORS
    )

    return center_title(fig)


def grouped_bar_chart(df, cat_col, num_col):
    temp_df = df[[cat_col, num_col]].copy()
    numeric_df = force_numeric(temp_df, [num_col])

    if numeric_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"Grouped Bar ({shorten_title(num_col)} by {shorten_title(cat_col)})",
            annotations=[
                dict(
                    text="Data numerik tidak cukup untuk grouped bar chart",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    group_df = numeric_df.groupby(cat_col, as_index=False)[num_col].mean()

    fig = px.bar(
        group_df,
        x=cat_col,
        y=num_col,
        title=f"Grouped Bar ({shorten_title(num_col)} by {shorten_title(cat_col)})",
        color_discrete_sequence=PASTEL_COLORS
    )

    return center_title(fig)


def strip_plot(df, cat_col, num_col):
    temp_df = df[[cat_col, num_col]].copy()
    numeric_df = force_numeric(temp_df, [num_col])

    if numeric_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"Strip Plot ({shorten_title(num_col)} by {shorten_title(cat_col)})",
            annotations=[
                dict(
                    text="Data numerik tidak cukup untuk strip plot",
                    x=0.5,
                    y=0.5,
                    showarrow=False
                )
            ]
        )
        return center_title(fig)

    fig = px.strip(
        numeric_df,
        x=cat_col,
        y=num_col,
        title=f"Strip Plot ({shorten_title(num_col)} by {shorten_title(cat_col)})",
        color_discrete_sequence=PASTEL_COLORS
    )

    return center_title(fig)

def data_type_donut_chart(df):

    numeric_count = len(
        df.select_dtypes(
            include=["int64", "float64"]
        ).columns
    )

    categorical_count = len(
        df.select_dtypes(
            include=["object", "category"]
        ).columns
    )

    datetime_count = len(
        df.select_dtypes(
            include=["datetime64"]
        ).columns
    )

    chart_df = pd.DataFrame({
        "Type": [
            "Numeric",
            "Categorical",
            "Datetime"
        ],
        "Count": [
            numeric_count,
            categorical_count,
            datetime_count
        ]
    })

    fig = px.pie(
        chart_df,
        names="Type",
        values="Count",
        hole=0.55,
        title="Data Type Distribution",
        color_discrete_sequence=PASTEL_COLORS
    )

    return center_title(fig)
