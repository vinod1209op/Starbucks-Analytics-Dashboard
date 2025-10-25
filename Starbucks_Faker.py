import pandas as pd 
import random, uuid
from faker import Faker 
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

fake=Faker()
random.seed(42)
np.random.seed(42)

# -----------------------------
# Starbucks-like domain config
# -----------------------------

categories = {
    "Beverages": ["Hot Coffee", "Cold Coffee", "Cold Tea", "Hot Tea", "Refreshers", "Frappuccino"],
    "Food": ["Bakery", "Breakfast", "Lunch", "Snacks", "Treats"],
    "Merchandise": ["Mugs", "Tumblers", "Gift Cards"]
}
sizes = {
    "Hot Coffee": ["Short", "Tall", "Grande", "Venti"],
    "Frappuccino": ["Tall", "Grande", "Venti"],
    "_default": ["Tall", "Grande", "Venti", "Trenta"]
}
channels = ["In-Store", "Mobile Order", "Drive-Thru", "Delivery"]
dayparts = [("Morning",6,11), ("Afternoon",11,15), ("Evening",15,19), ("Night",19,23)]

Region_Base_Temp = {
    "West": {1:0, 2:2, 3:6, 4:12, 5:18, 6:22, 7:25, 8:24, 9:20, 10:14, 11:7, 12:2},
    "Midwest": {1:3, 2:4, 3:8, 4:13, 5:18, 6:21, 7:24, 8:23, 9:19, 10:14, 11:8, 12:4},
    "South": {1:10, 2:12, 3:16, 4:20, 5:25, 6:28, 7:30, 8:29, 9:26, 10:22, 11:16, 12:12},
    "Northeast": {1:25, 2:24, 3:22, 4:18, 5:14, 6:10, 7:8, 8:9, 9:12, 10:16, 11:20, 12:24}
}

def daypart_of(ts):
    h=ts.hour
    for dp,start,end in dayparts:
        if start <= h < end:
            return dp
    return "Late Night"

def seasonal_multipier(ts, subcat):
    month = ts.month
    #summer boost for cold drinks, winter boost for hot drinks
    if subcat in ["Cold Coffee", "Cold Tea", "Refreshers", "Frappuccino"] and month in [5,6,7,8]:
        return 1.35
    #pumpkin/holiday boost for hot drinks
    if subcat in ["Hot Coffee", "Hot Tea"] and month in [10,11,12]:
        return 1.25
    return 1.0

def sample_product():
    category = random.choices(list(categories.keys()), weights=[0.6, 0.3, 0.02])[0]
    subcategory = random.choice(categories[category])
    size = random.choice(sizes.get(subcategory, sizes["_default"]))
    base_price = np.round(np.random.normal(4.0 if category=="Beverages" else 6.0 if category=="Food" else 15.0, scale=0.8),2)
    cogs = np.round(base_price * (0.3 if category=="Beverages" else 0.55 if category=="Food" else 0.55),2)
    name = f"{size} {subcategory}"
    return category, subcategory, name, size, base_price, cogs

def pick_device(channel):
    if channel=="Mobile Order":
        return random.choices(["iOS", "Android"], weights=[0.65, 0.35])[0]
    elif channel=="Delivery":
        return random.choices(["UberEats", "DoorDash", "GrubHub"], weights=[0.5, 0.3, 0.2])[0]
    else:
        return "POS"

def pick_payment(is_member):
    if is_member:
        return random.choices(["Starbucks Card", "Credit Card", "Mobile Pay"], weights=[0.5, 0.3, 0.2])[0]
    else:
        return random.choices(["Credit Card", "Mobile Pay", "Cash"], weights=[0.6, 0.3, 0.1])[0]

def maybe_stars_redeemed(is_member):
    if not is_member:
        return 0
    return np.random.choice([0, 25, 50, 100], p=[0.7, 0.15, 0.1, 0.05])

def maybe_tip(channel):
    base = {"In-Store":0.35, "Mobile Order":0.25, "Drive-Thru":0.30, "Delivery":0.15}[channel]
    if random.random() < base:
        return round(max(0.25, np.random.gamma(2.0, 0.6)),2)
    return 0.0

def maybe_promo(ts):
    if ts.month in [11,12] and random.random() < 0.25:
        return "Holiday Promo"
    if ts.month in [9,10] and random.random() < 0.15:
        return "Fall Promo"
    return "None"

def weather_for(ts, region):
    base_temp = Region_Base_Temp[region][ts.month]
    temp = np.round(np.random.normal(base_temp, 3.0))
    conditions = "Hot" if temp >= 26 else "Warm" if temp >= 18 else "Mild" if temp >= 13 else "Cool" if temp >=8 else "Cold"
    return temp, conditions


# --------------------------
# Main Data Generation 
# --------------------------

def generate(start="2024-10-21", days=365, stores=150, avg_orders=900):
    start_date = datetime.fromisoformat(start)
    markets = ["Seattle Metro", "LA Metro", "SF Bay", "Chicago Metro",
        "Dallas-Fort Worth", "Atlanta Metro", "NYC Metro", "Boston Metro",
        "Toronto Metro", "London Metro", "Tokyo Metro", "Sao Paulo Metro"]

    stores_df=pd.DataFrame({
        "Store ID": [str(uuid.uuid4()) for _ in range(stores)],
        "Format": np.random.choice(["Drive-Thru", "In-Line", "Kiosk"], p=[0.55,0.35,0.10],size=stores),
        "Region": np.random.choice(["West","Midwest","South","Northeast"], size=stores),
        "Market": np.random.choice(markets, size=stores)
    })

    fmt = stores_df["Format"].values
    wait_cafe = np.random.normal(loc=8, scale=3, size=stores)
    wait_dt = np.random.normal(loc=4, scale=1.5, size=stores)
    wait_kiosk = np.random.normal(loc=6, scale=2, size=stores)
    waits = []
    for i, f in enumerate(fmt):
        if f=="Drive-Thru":
            waits.append(max(2, round(wait_dt[i],1)))
        elif f=="Kiosk":
            waits.append(max(3, round(wait_kiosk[i],1)))
        else:
            waits.append(max(4, round(wait_cafe[i],1)))
    stores_df["Avg Wait Time (mins)"] = np.round(waits,1)

    rows_o, rows_o_i = [], []

    for day_offset in range(days):
        days = start_date + timedelta(days=day_offset)
        for _, store in stores_df.iterrows():
            mult = 1.2 if store["Format"]=="Drive-Thru" else 1.0
            dow = days.weekday()
            wmult = 1.3 if dow in [5,6] else 1.0
            num_orders = int(np.random.poisson(avg_orders/ stores * mult * wmult))

            for _ in range(num_orders):
                minute = random.randint(6*60,20*60)
                order_ts = days + timedelta(minutes=minute)
                order_id = str(uuid.uuid4())[2:8]

                channel = random.choices(channels, weights=[0.46,0.30,0.23,0.05])[0]
                if store["Format"]=="Drive-Thru": 
                    channel = random.choices(channels, weights=[0.25,0.65, 0.20, 0.02])[0]
                device = pick_device(channel)
                temprature_c, weather_cond = weather_for(order_ts, store["Region"])
                items = random.choices([1, 2, 3, 4], weights=[0.72, 0.18, 0.07, 0.03])[0]
                subtotal, cogs_total = 0.0, 0.0
                attached_food = False

                for line in range(items):
                    category, subcat, product_name, size, price, cogs = sample_product()
                    qty = np.random.choice([1, 2, 3], p=[0.85, 0.10, 0.05])
                    price = price * seasonal_multipier(order_ts, subcat)

                    if category == "Food":
                            attached_food = True
                    
                    rows_o_i.append([order_id, line + 1, product_name, category, subcat, size, qty, round(price,2), round(cogs,2)])
                    subtotal += price * qty
                    cogs_total += cogs * qty
                
                basic_discount = round(np.random.choice([0.0, 0.05, 0.10, 0.15], p=[0.85, 0.07, 0.05, 0.03]), 2)
                is_member = random.random() < 0.4
                loyalty_discount = 0.05 if is_member and random.random() < 0.2 else 0.0
                discount_rate = min(basic_discount + loyalty_discount, 0.3)
                tax = round(subtotal * 0.08, 2)
                total = subtotal * (1 - discount_rate) + tax

                stars_redeemed = maybe_stars_redeemed(is_member)
                payment_method = pick_payment(is_member)
                tip_amount = maybe_tip(channel)
                promo_code = maybe_promo(order_ts)

                rows_o.append([order_id, store["Store ID"], store["Region"], store["Market"], order_ts, daypart_of(order_ts),
                            channel, items, device, bool(is_member), payment_method, int(stars_redeemed), bool(attached_food),
                            float(temprature_c), weather_cond, round(subtotal,2), round(discount_rate * subtotal,2), tax, 
                            round(tip_amount,2), round(total + tip_amount,2), round(cogs_total,2), round(total - cogs_total,2)])
    orders_df = pd.DataFrame(rows_o, columns=["Order ID", "Store ID", "Region", "Market", "Order Timestamp", "Daypart",
                                               "Channel", "Num Items", "Device", "Is Loyalty Member", "Payment Method",
                                               "Stars Redeemed", "Has Food Item", "Temperature (C)", "Weather Condition",
                                               "Subtotal", "Discount Amount", "Tax Amount", "Tip Amount", "Total Amount",
                                               "Total COGS", "Profit"])
    order_items_df = pd.DataFrame(rows_o_i, columns=["Order ID", "Line Item", "Product Name", "Category", 
                                                     "Subcategory", "Size", "Quantity", "Price", "COGS"])
    return stores_df, orders_df, order_items_df

# ---------------------------
# Script Entry Point
# ---------------------------
def generate_and_save():
    stores, orders, items = generate()
    stores.to_csv("data/stores.csv", index=False)
    orders.to_csv("data/orders.csv", index=False)
    items.to_csv("data/order_items.csv", index=False)
    return stores, orders, items


    