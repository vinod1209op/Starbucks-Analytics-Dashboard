# Starbucks_AI.py
import os
import json
import pandas as pd
from openai import OpenAI

def generate_ai_insights(df, date_range=None, active_filters=None):
    if df.empty:
        return "No data available for the current filters."

    # --- summary data ---
    d = df.copy()
    if 'Order Timestamp' in d.columns:
        d['Order Timestamp'] = pd.to_datetime(d['Order Timestamp'])
        d['date'] = d['Order Timestamp'].dt.date

    revenue = d['Total Amount'].sum() if 'Total Amount' in d.columns else 0
    orders = d['Order ID'].nunique() if 'Order ID' in d.columns else len(d)
    aov = revenue / orders if orders else 0

    top_cat = d.groupby('Category')['Total Amount'].sum().nlargest(3).to_dict() if 'Category' in d.columns else {}
    top_channel = d.groupby('Channel')['Total Amount'].sum().nlargest(3).to_dict() if 'Channel' in d.columns else {}

    facts = {
        "filters": active_filters,
        "date_range": date_range,
        "revenue": round(revenue, 2),
        "orders": int(orders),
        "aov": round(aov, 2),
        "top_categories": top_cat,
        "top_channels": top_channel,
    }

    system_prompt = (
        "You are an analytics assistant for a coffeehouse chain. "
        "Use the provided data summary to write key insights in a friendly, business tone. "
        "Highlight growth, trends, best performers, and 2 action recommendations. "
        "Be concise — around 6–9 bullet points. Use $ and % where meaningful."
    )

    # --- OpenAI call ---
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", None))
        if not client.api_key:
            return "⚠️ Missing OpenAI API key. Set it in environment or .streamlit/secrets.toml."

        user = f"FACTS JSON:\n{json.dumps(facts, ensure_ascii=False, default=str)}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Error generating insights: {e}"
