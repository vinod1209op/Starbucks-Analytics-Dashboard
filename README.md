# ☕ [Brewed Insights — Starbucks Analytics Dashboard](https://starbucks-analytics-dashboard-glsebjytxrkbrsgf5enggk.streamlit.app/)

**Brewed Insights** is an interactive **Streamlit dashboard** for visualizing and exploring Starbucks-style retail data.  
It includes KPI metrics, interactive charts, and AI-generated business insights powered by OpenAI GPT.

---

## 🚀 Features

- 📊 **Comprehensive KPIs** — Revenue, AOV, Orders, and Profitability
- 🧭 **Interactive Filters** — Date range, Region, Channel, Category
- 🌍 **Visual Analytics**:
  - Monthly Sales Trends  
  - Channel Mix Over Time  
  - Daypart × Weekday Heatmap
  - Correlation Map
- 🤖 **AI Insights** — GPT-powered summary of key trends and recommendations
- ☕ **Cohesive Coffee-Themed UI** — Latte-inspired color palette for a warm, professional feel

---

## 🧠 Demo Preview

Streamlit Cloud Dashboard: https://starbucks-analytics-dashboard-glsebjytxrkbrsgf5enggk.streamlit.app/
> <img width="1440" height="900" alt="image" src="https://github.com/user-attachments/assets/cd3dae1f-791c-4e2a-a145-ed4ef3bfd248" />


---

## 🧩 Project Structure

📁 Starbucks_App/ \
├── Starbucks_App.py # Main Streamlit dashboard \
├── Starbucks_Plots.py # Plotly visualization components \
├── Starbucks_Faker.py # Synthetic data generator \
├── Starbucks_AI.py # OpenAI insights logic \
└── .streamlit/ \
└── secrets.toml # (not committed) stores API keys \
└── config.toml # setting the theme \


---

## ⚙️ Installation & Setup

'''bash \
git clone https://github.com/<your-username>/Starbucks-Dashboard.git \
cd Starbucks-Dashboard \
pip install -r requirements.txt \
streamlit run Starbucks_App.py 

---

## 🧰 Tech Stack

| Component   | Technology                  |
| ----------- | --------------------------- |
| Framework   | Streamlit                   |
| Charts      | Plotly                      |
| Data        | Pandas                      |
| AI Insights | OpenAI GPT                  |
| Styling     | Custom CSS (coffee palette) |

---

## 📝 License

This project is licensed under the MIT License — feel free to use, improve, and share.


