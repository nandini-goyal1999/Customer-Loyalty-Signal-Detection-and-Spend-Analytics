import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Shopping Analytics",
    page_icon="https://api.iconify.design/lucide:bar-chart-3.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Color Palette ────────────────────────────────────────────────────────────

COLORS = {
    "primary": "#6366f1",
    "secondary": "#8b5cf6",
    "accent": "#06b6d4",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "bg_dark": "#0f172a",
    "bg_card": "#1e293b",
    "bg_surface": "#334155",
    "text": "#f8fafc",
    "text_muted": "#94a3b8",
    "border": "#475569",
}

CHART_COLORS = [
    "#6366f1", "#06b6d4", "#10b981", "#f59e0b",
    "#ef4444", "#ec4899", "#8b5cf6", "#14b8a6",
]

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Global ── */
    .stApp {{
        background-color: {COLORS["bg_dark"]};
        color: {COLORS["text"]};
        font-family: 'Inter', sans-serif;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS["bg_card"]};
        border-right: 1px solid {COLORS["border"]};
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label {{
        color: {COLORS["text"]} !important;
    }}

    /* ── Header area ── */
    header[data-testid="stHeader"] {{
        background-color: transparent;
    }}

    /* ── KPI Metric Cards ── */
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, {COLORS["bg_card"]}, {COLORS["bg_surface"]});
        border: 1px solid {COLORS["border"]};
        border-radius: 14px;
        padding: 22px 26px;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.12);
    }}
    div[data-testid="stMetric"] label {{
        color: {COLORS["text_muted"]} !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {COLORS["text"]} !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
    }}

    /* ── Dataframe ── */
    .stDataFrame {{
        border: 1px solid {COLORS["border"]};
        border-radius: 14px;
        overflow: hidden;
    }}

    /* ── Divider ── */
    hr {{
        border-color: {COLORS["border"]};
        opacity: 0.3;
    }}

    /* ── Multiselect ── */
    .stMultiSelect > div > div {{
        background-color: {COLORS["bg_surface"]};
        border-color: {COLORS["border"]};
        border-radius: 10px;
        color: {COLORS["text"]};
    }}
    .stMultiSelect span[data-baseweb="tag"] {{
        background-color: {COLORS["primary"]} !important;
        border-radius: 6px;
    }}

    /* ── Plotly chart containers ── */
    .stPlotlyChart {{
        background-color: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 14px;
        padding: 10px;
    }}

    /* ── Chart headings ── */
    .chart-title {{
        color: {COLORS["text"]};
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 2px;
        padding: 0;
    }}
    .chart-subtitle {{
        color: {COLORS["text_muted"]};
        font-size: 0.82rem;
        margin-bottom: 14px;
    }}

    /* ── Expander ── */
    .streamlit-expanderHeader {{
        background-color: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        color: {COLORS["text"]} !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        color: {COLORS["text_muted"]};
        padding: 8px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS["primary"]} !important;
        border-color: {COLORS["primary"]} !important;
        color: white !important;
    }}

    /* ── Hide default decoration ── */
    #MainMenu, footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ─── Plotly Layout Template ──────────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Inter, sans-serif", size=13),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(
        gridcolor="rgba(71,85,105,0.3)",
        zerolinecolor="rgba(71,85,105,0.3)",
    ),
    yaxis=dict(
        gridcolor="rgba(71,85,105,0.3)",
        zerolinecolor="rgba(71,85,105,0.3)",
    ),
    hoverlabel=dict(
        bgcolor=COLORS["bg_card"],
        font_size=13,
        font_color=COLORS["text"],
        bordercolor=COLORS["border"],
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_muted"]),
    ),
)


# ─── Generate Fallback Data ──────────────────────────────────────────────────

def generate_sample_data():
    """Generates sample data if the CSV file is not found."""
    np.random.seed(42)
    n = 2000
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Beauty"]
    channels = ["Online", "In-Store"]
    genders = ["Male", "Female"]

    dates = pd.date_range("2023-01-01", periods=365, freq="D")

    return pd.DataFrame({
        "Customer_ID": np.random.randint(1000, 5000, n),
        "Date": np.random.choice(dates, n),
        "Category": np.random.choice(categories, n),
        "Channel": np.random.choice(channels, n),
        "Gender": np.random.choice(genders, n),
        "Age": np.random.randint(18, 65, n),
        "Purchase_Amount": np.round(np.random.exponential(80, n) + 10, 2),
        "Discount": np.round(np.random.uniform(0, 0.4, n), 2),
    })


# ─── Load Data ────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    csv_path = "customer_shopping_behavior.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        st.sidebar.warning("CSV not found -- using generated sample data.")
        df = generate_sample_data()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    return df


df = load_data()


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:20px 0 10px">
        <div style="
            display:inline-flex; align-items:center; justify-content:center;
            width:48px; height:48px;
            background:linear-gradient(135deg, {COLORS["primary"]}, {COLORS["accent"]});
            border-radius:12px; margin-bottom:8px;
        ">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                 stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>
            </svg>
        </div>
        <h2 style="color:{COLORS["text"]}; margin:0; font-size:1.2rem; font-weight:800;">
            Shopping Analytics
        </h2>
        <p style="color:{COLORS["text_muted"]}; font-size:0.78rem; margin-top:2px;">
            Customer Behavior Insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        f'<p style="color:{COLORS["text_muted"]}; font-size:0.72rem; '
        f'text-transform:uppercase; letter-spacing:0.1em; font-weight:700; '
        f'margin-bottom:8px;">Filters</p>',
        unsafe_allow_html=True,
    )

    category_filter = (
        st.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
        if "Category" in df.columns else []
    )
    channel_filter = (
        st.multiselect("Sales Channel", sorted(df["Channel"].unique()), default=sorted(df["Channel"].unique()))
        if "Channel" in df.columns else []
    )
    gender_filter = (
        st.multiselect("Gender", sorted(df["Gender"].unique()), default=sorted(df["Gender"].unique()))
        if "Gender" in df.columns else []
    )

    st.markdown("---")
    st.markdown(
        f'<p style="color:{COLORS["text_muted"]}; font-size:0.68rem; text-align:center;">'
        f'Showing filtered results</p>',
        unsafe_allow_html=True,
    )


# ─── Apply Filters ───────────────────────────────────────────────────────────

filtered = df.copy()
if category_filter and "Category" in filtered.columns:
    filtered = filtered[filtered["Category"].isin(category_filter)]
if channel_filter and "Channel" in filtered.columns:
    filtered = filtered[filtered["Channel"].isin(channel_filter)]
if gender_filter and "Gender" in filtered.columns:
    filtered = filtered[filtered["Gender"].isin(gender_filter)]


# ─── Page Header ──────────────────────────────────────────────────────────────

st.markdown(f"""
<div style="margin-bottom:28px;">
    <h1 style="
        color:{COLORS["text"]}; font-size:2rem; font-weight:800;
        margin:0; letter-spacing:-0.02em;
    ">Customer Shopping Behavior</h1>
    <p style="color:{COLORS["text_muted"]}; font-size:1rem; margin-top:4px;">
        Analyze purchase patterns, channel performance, and discount impact
    </p>
</div>
""", unsafe_allow_html=True)


# ─── KPI Cards ────────────────────────────────────────────────────────────────

total_sales = filtered["Purchase_Amount"].sum() if "Purchase_Amount" in filtered.columns else 0
avg_sales = filtered["Purchase_Amount"].mean() if "Purchase_Amount" in filtered.columns else 0
total_orders = len(filtered)
unique_customers = filtered["Customer_ID"].nunique() if "Customer_ID" in filtered.columns else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"${total_sales:,.0f}")
k2.metric("Avg. Order Value", f"${avg_sales:,.2f}")
k3.metric("Total Orders", f"{total_orders:,}")
k4.metric("Unique Customers", f"{unique_customers:,}")

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)


# ─── Row 1: Category Sales & Channel Donut ───────────────────────────────────

col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<p class="chart-title">Revenue by Category</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-subtitle">Total purchase amount per product category</p>', unsafe_allow_html=True)

    if "Category" in filtered.columns and "Purchase_Amount" in filtered.columns:
        cat_sales = (
            filtered.groupby("Category")["Purchase_Amount"]
            .sum().sort_values(ascending=True).reset_index()
        )
        fig_cat = px.bar(
            cat_sales, x="Purchase_Amount", y="Category", orientation="h",
            color="Purchase_Amount",
            color_continuous_scale=[COLORS["primary"], COLORS["accent"]],
        )
        fig_cat.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=False, coloraxis_showscale=False)
        fig_cat.update_traces(
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
        )
        st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    st.markdown('<p class="chart-title">Channel Distribution</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-subtitle">Revenue share by sales channel</p>', unsafe_allow_html=True)

    if "Channel" in filtered.columns and "Purchase_Amount" in filtered.columns:
        ch_sales = filtered.groupby("Channel")["Purchase_Amount"].sum().reset_index()
        fig_ch = px.pie(
            ch_sales, values="Purchase_Amount", names="Channel",
            hole=0.55, color_discrete_sequence=CHART_COLORS,
        )
        fig_ch.update_layout(
            **PLOTLY_LAYOUT, height=380, showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.15,
                xanchor="center", x=0.5,
                bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["text_muted"]),
            ),
        )
        fig_ch.update_traces(
            textinfo="percent+label", textfont_size=13,
            textfont_color=COLORS["text"],
            marker=dict(line=dict(color=COLORS["bg_dark"], width=2)),
            hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
        )
        st.plotly_chart(fig_ch, use_container_width=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ─── Row 2: Monthly Trend & Discount Scatter ─────────────────────────────────

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.markdown('<p class="chart-title">Monthly Sales Trend</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-subtitle">Revenue over time by month</p>', unsafe_allow_html=True)

    if "Date" in filtered.columns and "Purchase_Amount" in filtered.columns:
        monthly = (
            filtered.set_index("Date")
            .resample("M")["Purchase_Amount"].sum().reset_index()
        )
        monthly.columns = ["Month", "Revenue"]
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Revenue"],
            mode="lines+markers",
            line=dict(color=COLORS["primary"], width=3, shape="spline"),
            marker=dict(size=7, color=COLORS["primary"],
                        line=dict(width=2, color=COLORS["bg_dark"])),
            fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
            hovertemplate="<b>%{x|%B %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
        ))
        fig_trend.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=False)
        st.plotly_chart(fig_trend, use_container_width=True)

with col_right2:
    st.markdown('<p class="chart-title">Discount vs. Purchase Amount</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-subtitle">Impact of discounts on order value</p>', unsafe_allow_html=True)

    if "Discount" in filtered.columns and "Purchase_Amount" in filtered.columns:
        scatter_df = (
            filtered.sample(min(500, len(filtered)), random_state=42)
            if len(filtered) > 500 else filtered
        )
        fig_scatter = px.scatter(
            scatter_df, x="Discount", y="Purchase_Amount",
            color="Category" if "Category" in scatter_df.columns else None,
            color_discrete_sequence=CHART_COLORS, opacity=0.7,
        )
        fig_scatter.update_layout(
            **PLOTLY_LAYOUT, height=380,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.25,
                xanchor="center", x=0.5,
                bgcolor="rgba(0,0,0,0)", font=dict(color=COLORS["text_muted"], size=11),
            ),
        )
        fig_scatter.update_traces(
            marker=dict(size=8, line=dict(width=1, color=COLORS["bg_dark"])),
            hovertemplate="<b>Discount:</b> %{x:.0%}<br><b>Amount:</b> $%{y:,.2f}<extra></extra>",
        )
        fig_scatter.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ─── Age Distribution ────────────────────────────────────────────────────────

if "Age" in filtered.columns:
    st.markdown('<p class="chart-title">Customer Age Distribution</p>', unsafe_allow_html=True)
    st.markdown('<p class="chart-subtitle">Breakdown of customers by age group</p>', unsafe_allow_html=True)

    fig_age = px.histogram(
        filtered, x="Age", nbins=20,
        color_discrete_sequence=[COLORS["accent"]],
    )
    fig_age.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False, bargap=0.1)
    fig_age.update_traces(
        marker_line_width=0,
        hovertemplate="<b>Age %{x}</b><br>Count: %{y}<extra></extra>",
    )
    st.plotly_chart(fig_age, use_container_width=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ─── Data Table ───────────────────────────────────────────────────────────────

with st.expander("View Raw Data", expanded=False):
    display_cols = [c for c in filtered.columns if c != "Month"]
    format_dict = {}
    if "Purchase_Amount" in filtered.columns:
        format_dict["Purchase_Amount"] = "${:,.2f}"
    if "Discount" in filtered.columns:
        format_dict["Discount"] = "{:.0%}"

    st.dataframe(
        filtered[display_cols].head(200).style.format(format_dict),
        use_container_width=True,
        height=400,
    )
    st.caption(f"Showing {min(200, len(filtered))} of {len(filtered):,} records")
