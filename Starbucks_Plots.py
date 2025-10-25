import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

COFFEE = ["#006241", "#7A5228", "#B6895B", "#CBB58A", "#3C2F2F"]
pio.templates["coffee"] = pio.templates["plotly_white"]
pio.templates["coffee"].layout.colorway = COFFEE
pio.templates.default = "coffee"

def monthly_trends(orders: pd.DataFrame):
    ts = "Order Timestamp"
    m = (orders
         .set_index(ts).resample("MS")
         .agg(Total=("Total Amount","sum"), Orders=("Order ID","nunique"))
         .reset_index())
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m[ts], y=m["Total"], name="Revenue", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=m[ts], y=m["Orders"], name="Orders", mode="lines+markers", yaxis="y2"))
    fig.update_layout(
        title="Monthly Trends: Revenue & Orders",
        yaxis=dict(title="Revenue"),
        yaxis2=dict(title="Orders", overlaying="y", side="right"),
        margin=dict(l=10,r=10,t=50,b=10)
    )
    return fig

def category_profitability(orders: pd.DataFrame, items: pd.DataFrame):
    if not {"Order ID","Category","Price","Quantity"}.issubset(items.columns):
        return None
    it = items.copy()
    it["Line Revenue"] = it["Price"] * it["Quantity"]
    cat = (it.groupby("Category", as_index=False)
             .agg(Revenue=("Line Revenue","sum")))
    # join order Profit at order level then re-aggregate by Category via share
    # simpler: approximate profit by allocating proportionally to item revenue per order
    per_order_rev = it.groupby("Order ID", as_index=False)["Line Revenue"].sum().rename(columns={"Line Revenue":"OrderRevenue"})
    it = it.merge(per_order_rev, on="Order ID", how="left")
    orders_profit = orders[["Order ID","Profit"]]
    it = it.merge(orders_profit, on="Order ID", how="left")
    it["AllocProfit"] = it["Profit"] * (it["Line Revenue"] / it["OrderRevenue"]).fillna(0)
    cat_profit = it.groupby("Category", as_index=False).agg(Revenue=("Line Revenue","sum"), Profit=("AllocProfit","sum"))

    fig = px.bar(cat_profit.melt(id_vars="Category", value_vars=["Revenue","Profit"]),
                 x="Category", y="value", color="variable",
                 barmode="group", title="Category Profitability: Revenue vs Profit",
                 labels={"value":"","variable":""})
    fig.update_layout(margin=dict(l=10,r=10,t=50,b=10))
    return fig

def channel_share_over_time(orders: pd.DataFrame, freq="MS"):
    if "Channel" not in orders.columns:
        return None
    ts = "Order Timestamp"
    grp = (orders
           .set_index(ts)
           .groupby([pd.Grouper(freq=freq), "Channel"])
           .agg(Revenue=("Total Amount","sum"))
           .reset_index())
    total = grp.groupby(ts)["Revenue"].transform("sum")
    grp["Share"] = grp["Revenue"] / total * 100
    fig = px.area(grp, x=ts, y="Share", color="Channel",
                  title="Channel Mix Over Time (100% share)", groupnorm="fraction")
    fig.update_layout(yaxis_ticksuffix="%", margin=dict(l=10,r=10,t=50,b=10))
    return fig

def daypart_week_heatmap(orders: pd.DataFrame):
    if "Daypart" not in orders.columns:
        return None
    df = orders.copy()
    df["Weekday"] = df["Order Timestamp"].dt.day_name()
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    df["Weekday"] = pd.Categorical(df["Weekday"], categories=order, ordered=True)
    pivot = df.pivot_table(index="Daypart", columns="Weekday", values="Total Amount", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, text_auto=True, aspect="auto",
                    title="Heatmap: Revenue by Daypart × Weekday",
                    labels=dict(color="Revenue"))
    fig.update_layout(margin=dict(l=10,r=10,t=50,b=10))
    return fig

def correlation_heatmap(orders):
    # select numerical columns of interest
    num_cols = ["Total Amount","Profit","Temperature (C)","Num Items","Discount Amount","Tip Amount"]
    df = orders[num_cols].copy()
    corr = df.corr().round(2)
    fig = px.imshow(corr, text_auto=True, aspect="auto",
                    color_continuous_scale="BrBG",
                    title="Correlation Matrix of Key Metrics")
    return fig
