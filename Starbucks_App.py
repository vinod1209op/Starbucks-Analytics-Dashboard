import os, hashlib
import streamlit as st
import pandas as pd

from Starbucks_AI import generate_ai_insights
from Starbucks_Plots import monthly_trends, channel_share_over_time, daypart_week_heatmap, correlation_heatmap
from Starbucks_Faker import generate_and_save 

def file_md5(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

FAKER_PATH = "Starbucks_Faker.py"
os.makedirs("data", exist_ok=True)
HASH_FILE = "data/_faker_hash.txt"

st.set_page_config(page_title="Brewed Insights ☕", page_icon="☕", layout="wide")

# --- subtle CSS polish (coffee accents) ---
st.markdown("""
<style>
/* rounded panels */
.block-container { padding-top: 1.5rem; }
section[data-testid="stSidebar"] { background: #E8D9C7; }
div[data-testid="stMetricValue"] { font-weight: 700; }
.kpi-card {
  background: #FFF7EA; border: 1px solid #E3D5C3;
  padding: 16px; border-radius: 16px; text-align:center;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.kpi-title { font-size: 0.85rem; color:#7A5228; margin-bottom:6px; }
.kpi-value { font-size: 1.4rem; }
.right-rail { position: sticky; top: 84px; }
.card { background:#FFF7EA; border:1px solid #E3D5C3; border-radius:16px; padding:16px; box-shadow:0 1px 6px rgba(0,0,0,0.04); }
.card h3 { margin:0 0 8px 0; color:#7A5228; }
</style>
""", unsafe_allow_html=True)

@st.cache_data()
def load_data(faker_hash: str):
    prev_hash = None
    if os.path.exists(HASH_FILE):
        try:
            prev_hash = open(HASH_FILE, "r").read().strip()
        except Exception:
            prev_hash = None

    csv_missing = not (os.path.exists("data/stores.csv")
                       and os.path.exists("data/orders.csv")
                       and os.path.exists("data/order_items.csv"))

    if csv_missing or (faker_hash != prev_hash):
        with st.spinner("Generating synthetic data…"):
            stores_df, orders_df, items_df = generate_and_save()
        # record the new hash
        with open(HASH_FILE, "w") as f:
            f.write(faker_hash)
    else:
        stores_df = pd.read_csv("data/stores.csv")
        orders_df = pd.read_csv("data/orders.csv", parse_dates=["Order Timestamp"])
        items_df  = pd.read_csv("data/order_items.csv")
    return orders_df, items_df, stores_df

faker_hash = file_md5(FAKER_PATH)
orders, items, stores = load_data(faker_hash)
all_regions  = sorted(stores["Region"].dropna().unique().tolist()) if "Region" in stores else []
all_channels = sorted(orders["Channel"].dropna().unique().tolist()) if "Channel" in orders else []
min_date = pd.to_datetime(orders["Order Timestamp"].min()).date()
max_date = pd.to_datetime(orders["Order Timestamp"].max()).date()

# ---------- APPLY FILTERS ----------
if "date_range" not in st.session_state:
    st.session_state.date_range = (min_date, max_date)
if "regions" not in st.session_state:
    st.session_state.regions = all_regions[:]
if "channels" not in st.session_state:
    st.session_state.channels = all_channels[:]

# Ensure Region exists on orders (join once if needed)
if (
    "Region" not in orders.columns
    and {"Store ID"}.issubset(orders.columns)
    and {"Store ID", "Region"}.issubset(stores.columns)
):
    orders = orders.merge(stores[["Store ID", "Region"]], on="Store ID", how="left")

# Read current filter values from session_state
date_range = st.session_state.date_range
regions_sel = st.session_state.regions
channels_sel = st.session_state.channels

# Normalize date_range safely
if isinstance(date_range, (tuple, list)) and len(date_range) == 2 and all(pd.notnull(d) for d in date_range):
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Apply filters to create f + fi
f = orders.loc[
    (orders["Order Timestamp"].dt.date >= start_date)
    & (orders["Order Timestamp"].dt.date <= end_date)
].copy()
if regions_sel:
    f = f[f["Region"].isin(regions_sel)]
if channels_sel and "Channel" in f.columns:
    f = f[f["Channel"].isin(channels_sel)]
fi = items[items["Order ID"].isin(f["Order ID"].unique())].copy()

# ---------- TITLE + KPIs ----------
st.markdown("### **Brewed Insights** — Starbucks-style Analytics ☕")
st.caption("Warm, synthetic data. Not affiliated with Starbucks.")

total_revenue = float(f["Total Amount"].sum())
total_orders = int(f["Order ID"].nunique())
aov = total_revenue / max(total_orders, 1)
gross_margin_pct = (f["Profit"].sum() / total_revenue * 100) if total_revenue else 0.0

iced_subcats = {"Cold Coffee","Cold Tea","Refreshers","Frappuccino"}
fi["Iced"] = fi["Subcategory"].isin(iced_subcats)
merged = f.merge(fi[["Order ID","Iced"]], on="Order ID", how="left")
hot_days = merged.loc[merged["Temperature (C)"] >= 26, "Iced"].mean()
cold_days = merged.loc[merged["Temperature (C)"] < 18, "Iced"].mean()
weather_sensitivity = (hot_days - cold_days) * 100

rev_str = f"${total_revenue:,.2f}"
orders_str = f"{total_orders:,}"
aov_str = f"${aov:,.2f}"
gross_str = f"{gross_margin_pct:.1f}%"
weather_str = f"{weather_sensitivity:+.1f}%"

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.markdown(f'<div class="kpi-card"><div class="kpi-title">💵 Total Revenue</div><div class="kpi-value">{rev_str}</div></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="kpi-card"><div class="kpi-title">🧾 Orders</div><div class="kpi-value">{orders_str}</div></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="kpi-card"><div class="kpi-title">🍪 Average Order Value</div><div class="kpi-value">{aov_str}</div></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="kpi-card"><div class="kpi-title">💰 Gross Profit Margin %</div><div class="kpi-value">{gross_str}</div></div>', unsafe_allow_html=True)
with col5: st.markdown(f'<div class="kpi-card"><div class="kpi-title">🌥 Weather Sensitivity %</div><div class="kpi-value">{weather_str}</div></div>', unsafe_allow_html=True)

# ---- keep date defaults in-bounds of current data ----
def clamp_date_range(dr, lo, hi):
    # normalize and clamp to [lo, hi]
    if not isinstance(dr, (tuple, list)) or len(dr) != 2:
        return (lo, hi)
    s, e = dr
    # swap if reversed
    if s and e and s > e:
        s, e = e, s
    # clamp to dataset bounds
    s = max(lo, min(s or lo, hi))
    e = max(lo, min(e or hi, hi))
    # if still invalid (e.g., lo==hi), force full window
    if s > e:
        return (lo, hi)
    return (s, e)

# if data window changed since last run, fix session defaults
bounds = (min_date, max_date)
if st.session_state.get("_last_bounds") != bounds:
    st.session_state.date_range = clamp_date_range(
        st.session_state.get("date_range", bounds), min_date, max_date
    )
    st.session_state._last_bounds = bounds
else:
    # also clamp proactively (covers manual edits, etc.)
    st.session_state.date_range = clamp_date_range(
        st.session_state.get("date_range", bounds), min_date, max_date
    )


# ---------- PLOTS + FILTERS ----------
col_content, col_filters = st.columns([6, 2], gap="medium")

with col_filters:
    st.markdown('<div class="right-rail card">', unsafe_allow_html=True)
    st.markdown("### ☕ Filters")
    with st.form("filters_form", border=False):
        # Bind widgets to session_state so KPIs/plots update on submit
        st.date_input("Date range", value=st.session_state.date_range,
                      min_value=min_date, max_value=max_date, key="date_range")
        st.multiselect("Region", options=all_regions, default=st.session_state.regions, key="regions")
        st.multiselect("Channel", options=all_channels, default=st.session_state.channels, key="channels")
        st.form_submit_button("Apply", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_content:
    tab_trend, tab_mix, tab_heat, tab_corr = st.tabs(
        ["Monthly Trends", "Channel Mix", "Daypart × Weekday", "Correlations"]
    )
    with tab_trend:
        st.plotly_chart(monthly_trends(f), use_container_width=True)
    with tab_mix:
        st.plotly_chart(channel_share_over_time(f), use_container_width=True)
    with tab_heat:
        hm = daypart_week_heatmap(f)
        if hm is not None:
            st.plotly_chart(hm, use_container_width=True)
        else:
            st.info("Daypart column not found.")
    with tab_corr:
        ch = correlation_heatmap(f)
        if ch is not None:
            st.plotly_chart(ch, use_container_width=True) 
        else:
            st.info("Not enough numeric columns to build a correlation matrix.")

with st.expander("☕ AI Insights Summary"):
    run = st.button("Generate Insights", use_container_width=True)

    active_filters = {
        "regions": regions if 'regions' in locals() else None,
        "channels": channels if 'channels' in locals() else None,
        "date_range": (start_date, end_date) if 'start_date' in locals() else None
    }

    if run:
        summary = generate_ai_insights(f, date_range=active_filters.get("date_range"), active_filters=active_filters)
        st.markdown(f"<div class='ai-card'>{summary}</div>", unsafe_allow_html=True)
    else:
        st.info("Click **Generate Insights** to summarize your filtered data.")

with st.expander("Preview data"):
    st.dataframe(f.head(100), hide_index=True)

# ---------- Footer ----------
st.markdown("<br>", unsafe_allow_html=True)
st.caption("© Brewed Insights • Demo app for educational purposes.")
