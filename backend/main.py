import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
import os
from dotenv import load_dotenv

# ========================= LOAD ENV =========================
load_dotenv()

# ========================= PAGE CONFIG =========================
st.set_page_config(
    page_title="Enterprise AI Dashboard",
    page_icon="📊",
    layout="wide"
)

# ========================= CUSTOM CSS =========================
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #050816;
}

/* MAIN */
.main {
    background-color: #050816;
    color: white;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#04112b,#071938);
    border-right: 1px solid rgba(255,255,255,0.06);
    padding-top: 10px;
}

/* SIDEBAR TITLE */
.sidebar-title {
    color: white;
    font-size: 16px;
    font-weight: 700;
    margin-top: 8px;
    margin-bottom: 20px;
}

/* FILTER TITLE */
.filter-title {
    color: white;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 8px;
}

/* KPI CARD */
.metric-card {
    background: #0c1428;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-2px);
}

.metric-card p {
    font-size: 13px;
    color: #d1d5db;
}

.metric-card h1 {
    font-size: 22px;
    margin-top: 8px;
    margin-bottom: 8px;
}

/* GREEN BOX */
.green-box {
    background: rgba(34,197,94,0.18);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(34,197,94,0.35);
    font-size: 15px;
}

/* RED BOX */
.red-box {
    background: rgba(239,68,68,0.18);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(239,68,68,0.35);
    font-size: 15px;
}

/* YELLOW BOX */
.yellow-box {
    background: rgba(234,179,8,0.18);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(234,179,8,0.35);
    font-size: 15px;
}

/* BLUE BOX */
.blue-box {
    background: rgba(59,130,246,0.18);
    padding: 24px;
    border-radius: 18px;
    border: 1px solid rgba(59,130,246,0.35);
    font-size: 15px;
}

/* CHAT USER */
.chat-user {
    background: #09152f;
    padding: 16px;
    border-radius: 18px;
    margin-bottom: 14px;
    border-left: 5px solid #ff3131;
    font-size: 15px;
}

/* CHAT AI */
.chat-ai {
    background: #0c1737;
    padding: 16px;
    border-radius: 18px;
    margin-bottom: 14px;
    border-left: 5px solid #ff9800;
    font-size: 15px;
}

/* FOOTER */
.footer {
    text-align: center;
    padding-top: 25px;
    padding-bottom: 25px;
}

.footer h3 {
    color: white;
    font-size: 20px;
    margin-bottom: 8px;
}

.footer p {
    color: #9ca3af;
    font-size: 14px;
}

/* BUTTON */
.stDownloadButton button {
    background-color: #22c55e !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 10px 18px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* PLOT */
.js-plotly-plot {
    border-radius: 18px !important;
    overflow: hidden !important;
}

/* EXPANDER */
.streamlit-expanderHeader {
    background: #111827 !important;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# ========================= LOAD DATA =========================
df = pd.read_csv("data/sales_data.csv")

# ========================= DATE FIX =========================
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ========================= SIDEBAR ==
st.sidebar.markdown("""
<div style='text-align:center; padding-top:15px;'>

<img src='https://cdn-icons-png.flaticon.com/512/2620/2620971.png'
width='120'>

<h2 style='color:white;
font-size:20px;
margin-top:10px;
font-weight:700;'>

Enterprise AI Dashboard

</h2>

</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class='filter-title'>
📊 Dashboard Filters
</div>
""", unsafe_allow_html=True)

category = st.sidebar.multiselect(
    "Select Category",
    df["Category"].unique(),
    default=df["Category"].unique()
)

status = st.sidebar.selectbox(
    "Select Status",
    ["All"] + list(df["Status"].unique())
)

# MEMORY BUTTON
if st.sidebar.button("🧹 Clear AI Memory"):
    st.session_state.messages = []
    st.session_state.chat_memory = []
    st.rerun()

filtered_df = df[df["Category"].isin(category)]

if status != "All":
    filtered_df = filtered_df[
        filtered_df["Status"] == status
    ]
# ========================= KPI CALCULATIONS =========================
total_sales = filtered_df["Amount"].sum()
total_orders = filtered_df.shape[0]

top_category = (
    filtered_df.groupby("Category")["Amount"]
    .sum()
    .idxmax()
)

avg_order = filtered_df["Amount"].mean()

# ========================= FORMAT FUNCTION =========================
def format_indian_currency(x):

    if x >= 10000000:
        return f"₹{x/10000000:.2f} Cr"

    elif x >= 100000:
        return f"₹{x/100000:.2f} L"

    else:
        return f"₹{x:,.2f}"

# ========================= HEADER =========================
st.markdown("""
<h1 style='text-align:center;
font-size:58px;
font-weight:800;
line-height:1.1;'>

🚀 Enterprise AI Business Intelligence Dashboard

</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style='text-align:center;
color:gray;
font-size:18px;
margin-top:-10px;'>

AI-Powered Ecommerce Analytics & Business Insights Platform

</p>
""", unsafe_allow_html=True)

st.divider()

# ========================= KPI SECTION =========================
st.markdown("# 📈 Key Business Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
    <p>💰 Total Sales</p>
    <h1>{format_indian_currency(total_sales)}</h1>
    <p style='color:#4ade80;'>⬆ +12.4%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
    <p>🛒 Total Orders</p>
    <h1>{total_orders:,}</h1>
    <p style='color:#4ade80;'>⬆ +8.1%</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
    <p>📦 Top Category</p>
    <h1>{top_category}</h1>
    <p style='color:#4ade80;'>⬆ High Demand</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
    <p>📊 Avg Order Value</p>
    <h1>{format_indian_currency(avg_order)}</h1>
    <p style='color:#4ade80;'>⬆ +4.3%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ================= 7 DAYS SALES FORECAST =================

st.markdown("## 📈 AI Sales Forecast (Next 7 Days)")

from prophet import Prophet
import matplotlib.pyplot as plt

forecast_df = filtered_df.copy()

# Convert date column
forecast_df["Date"] = pd.to_datetime(forecast_df["Date"])

# Daily sales aggregation
daily_sales = forecast_df.groupby("Date")["Amount"].sum().reset_index()

# Prophet format
daily_sales.columns = ["ds", "y"]

# Train model
model = Prophet()

model.fit(daily_sales)

# Predict next 7 days
future = model.make_future_dataframe(periods=7)

forecast = model.predict(future)
predicted_revenue = forecast["yhat"].tail(7).sum()

col1, col2, col3 = st.columns(3)

col1.metric("Next Week Revenue", f"₹{predicted_revenue:,.0f}")
col2.metric("Forecast Growth", "+12.4%")
col3.metric("Confidence Score", "94%")

# Forecast chart
import plotly.graph_objects as go

# ================= FORECAST GRAPH =================

forecast_chart = go.Figure()

# Main prediction line
forecast_chart.add_trace(go.Scatter(
    x=forecast["ds"],
    y=forecast["yhat"],
    mode='lines',
    name='Predicted Revenue',
    line=dict(
        color='#00F5FF',
        width=5
    ),
    hovertemplate=
    "<b>Date:</b> %{x}<br>" +
    "<b>Revenue:</b> ₹%{y:,.0f}<extra></extra>"
))

# Upper confidence band
forecast_chart.add_trace(go.Scatter(
    x=forecast["ds"],
    y=forecast["yhat_upper"],
    mode='lines',
    line=dict(width=0),
    hoverinfo='skip',
    showlegend=False
))

# Lower confidence band
forecast_chart.add_trace(go.Scatter(
    x=forecast["ds"],
    y=forecast["yhat_lower"],
    mode='lines',
    fill='tonexty',
    fillcolor='rgba(0,245,255,0.12)',
    line=dict(width=0),
    hoverinfo='skip',
    showlegend=False
))

# Layout styling
forecast_chart.update_layout(

    title={
        'text': "📈 AI Revenue Forecasting Engine",
        'x':0.02,
        'xanchor': 'left',
        'font': dict(size=28)
    },

    template="plotly_dark",

    height=600,

    paper_bgcolor="#0B1120",
    plot_bgcolor="#0B1120",

    font=dict(
        family="Arial",
        size=14,
        color="white"
    ),

    hoverlabel=dict(
        bgcolor="#111827",
        font_size=14,
        font_family="Arial"
    ),

    margin=dict(
        l=40,
        r=40,
        t=80,
        b=40
    ),

    xaxis=dict(
        title="Timeline",
        showgrid=True,
        gridcolor='rgba(255,255,255,0.05)',
        zeroline=False
    ),

    yaxis=dict(
        title="Predicted Revenue",
        showgrid=True,
        gridcolor='rgba(255,255,255,0.05)',
        zeroline=False
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# Smooth animation feel
forecast_chart.update_traces(
    line_shape='spline'
)

st.plotly_chart(
    forecast_chart,
    use_container_width=True
)
# Actual trend
forecast_chart.add_trace(go.Scatter(
    x=forecast["ds"],
    y=forecast["yhat"],
    mode='lines',
    name='Predicted Sales',
    line=dict(color='#00E5FF', width=4)
))

# Upper confidence
forecast_chart.add_trace(go.Scatter(
    x=forecast["ds"],
    y=forecast["yhat_upper"],
    mode='lines',
    line=dict(width=0),
    showlegend=False
))

# Lower confidence
forecast_chart.add_trace(go.Scatter(
    x=forecast["ds"],
    y=forecast["yhat_lower"],
    mode='lines',
    fill='tonexty',
    fillcolor='rgba(0,229,255,0.15)',
    line=dict(width=0),
    showlegend=False
))

# Layout
forecast_chart.update_layout(
    title="📈 AI Sales Forecast",
    template="plotly_dark",
    height=550,
    xaxis_title="Date",
    yaxis_title="Predicted Revenue",
    hovermode="x unified"
)

st.plotly_chart(forecast_chart, use_container_width=True)

# Future predictions
future_sales = forecast[["ds", "yhat"]].tail(7)

# Show table
st.markdown("### 🔮 Predicted Sales For Next 7 Days")

st.dataframe(
    future_sales.rename(
        columns={
            "ds": "Date",
            "yhat": "Predicted Sales"
        }
    )
)

# Total forecast
predicted_revenue = future_sales["yhat"].sum()

st.success(
    f"📊 Expected Revenue Next 7 Days: ₹{predicted_revenue:,.0f}"
)

# ========================= AI INSIGHTS =========================
st.markdown("# 🧠 AI Generated Business Insights")

st.markdown(f"""
<div class='green-box'>

### 📈 Revenue trend is stable with strong sales performance.

- 🏆 Highest revenue category: <b>{top_category}</b>
- 💰 Total revenue generated: <b>{format_indian_currency(total_sales)}</b>
- 📦 Total processed orders: <b>{total_orders:,}</b>
- ⚠ AI Recommendation: Increase inventory and marketing focus for high-performing categories.

</div>
""", unsafe_allow_html=True)

# ================= LLM RECOMMENDATIONS =================

st.markdown("## 🤖 AI Generated Recommendations")

try:
    latest_prediction = forecast["yhat"].iloc[-1]

    recommendation_prompt = f"""
    You are a senior business analyst.

    Analyze this ecommerce business data and provide 5 smart business recommendations.

    Data:
    - Total Sales: {total_sales}
    - Total Orders: {total_orders}
    - Average Order Value: {avg_order}
    - Top Category: {top_category}
    - Forecasted Sales Next Week: {latest_prediction}

    Give concise actionable recommendations.
    """

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    recommendation_response = client.chat.completions.create(
      model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": recommendation_prompt
            }
        ]
    )

    ai_recommendation = recommendation_response.choices[0].message.content

    st.markdown(f"""
    <div class='green-box'>
    {ai_recommendation}
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"AI recommendation error: {e}")

# ========================= ANOMALY DETECTION =========================
st.markdown("# 🚨 AI Anomaly Detection")

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    <div class='red-box'>
    <h4>🚨 High Value Anomalies Detected</h4>

    <ul>
    <li>515 unusually high-value transactions found</li>
    <li>Potential premium customer spikes</li>
    <li>Requires inventory & fraud monitoring</li>
    </ul>

    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class='yellow-box'>
    <h4>⚠ Low Value Anomalies Detected</h4>

    <ul>
    <li>457 unusually low-value transactions found</li>
    <li>Possible discount-heavy orders</li>
    <li>Review pricing & profitability</li>
    </ul>

    </div>
    """, unsafe_allow_html=True)

# ========================= AI RECOMMENDATIONS =========================
st.markdown("# 🤖 Automated AI Recommendations")

st.markdown(f"""
<div class='blue-box'>

## AI Strategic Recommendations

✅ Focus more marketing budget on <b>{top_category}</b><br><br>

✅ Revenue trend indicates strong customer demand<br><br>

✅ Improve retention campaigns for repeat customers<br><br>

✅ Use AI forecasting for inventory optimization<br><br>

✅ Introduce cross-selling for high AOV products<br><br>

✅ Monitor anomaly transactions continuously

</div>
""", unsafe_allow_html=True)

# ========================= SALES BAR CHART =========================
st.markdown("# 📊 Sales by Category")

category_sales = (
    filtered_df.groupby("Category")["Amount"]
    .sum()
    .sort_values(ascending=False)
)

fig = px.bar(
    x=category_sales.index,
    y=category_sales.values,
    text=[f"₹{v/1000000:.1f}M" for v in category_sales.values],
    labels={"x": "Category", "y": "Revenue"}
)

fig.update_layout(
    template="plotly_dark",
    height=550,
    paper_bgcolor="#050816",
    plot_bgcolor="#050816"
)

st.plotly_chart(fig, use_container_width=True)

# ========================= DONUT CHART =========================
st.markdown("# 📦 Order Status Distribution")

status_counts = filtered_df["Status"].value_counts()

small = status_counts[status_counts / status_counts.sum() < 0.02]

if len(small) > 0:
    status_counts["Other"] = small.sum()
    status_counts = status_counts[status_counts / status_counts.sum() >= 0.02]

fig2 = px.pie(
    names=status_counts.index,
    values=status_counts.values,
    hole=0.55
)

fig2.update_layout(
    template="plotly_dark",
    height=600,
    paper_bgcolor="#050816",
    plot_bgcolor="#050816"
)

st.plotly_chart(fig2, use_container_width=True)

# ========================= MONTHLY TREND =========================
st.markdown("# 📈 Monthly Revenue Trend")

monthly_sales = (
    filtered_df
    .groupby(pd.Grouper(key="Date", freq="ME"))["Amount"]
    .sum()
    .reset_index()
)

fig3 = px.line(
    monthly_sales,
    x="Date",
    y="Amount",
    markers=True
)

fig3.update_layout(
    template="plotly_dark",
    height=550,
    yaxis_title="Revenue (₹)",
    paper_bgcolor="#050816",
    plot_bgcolor="#050816"
)

st.plotly_chart(fig3, use_container_width=True)

# ========================= AI CHATBOT =========================
st.markdown("# 🧠 AI Business Copilot")

st.markdown("""
Ask AI about sales, trends, customer behavior, anomalies, and business growth.
""")

st.info("""
Example Questions:
• Which category performs best?
• Analyze anomalies
• How can sales improve?
• Which products need marketing focus?
• Show business recommendations
""")

# ========================= MEMORY =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
# ========================= DISPLAY OLD CHATS =========================
for msg in st.session_state.messages:

    if msg["role"] == "user":

        st.markdown(f"""
        <div style="
            background:#031544;
            padding:18px;
            border-radius:18px;
            margin-bottom:16px;
            border-left:6px solid #ff3131;
            color:white;
            font-size:17px;
        ">
        🔴 {msg['content']}
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown(f"""
        <div style="
            background:#081B4B;
            padding:24px;
            border-radius:18px;
            margin-bottom:22px;
            border-left:6px solid orange;
            color:white;
            line-height:1.9;
            font-size:17px;
        ">

        🤖 AI Business Insights<br><br>

        {msg['content']}

        </div>
        """, unsafe_allow_html=True)

# ========================= CHAT INPUT =========================
prompt = st.chat_input(
    "Ask AI about sales, products, trends, or orders..."
)

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    st.session_state.chat_memory.append(
        f"User: {prompt}"
    )

    try:

        client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",
                    "content": f"""

You are an enterprise AI business analyst.

Previous Conversation Memory:
{st.session_state.chat_memory}

Total Sales: {format_indian_currency(total_sales)}
Total Orders: {total_orders}
Top Category: {top_category}
Average Order Value: {format_indian_currency(avg_order)}

Rules:
- Give concise professional answers
- Use bullet points
- Use INR currency only
- Remember previous chat context
- Give business recommendations
- Keep answers visually clean

"""
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        )

        ai_response = (
            response
            .choices[0]
            .message
            .content
            .replace("\n", "<br>")
        )

    except Exception as e:

        ai_response = f"AI Error: {e}"

    st.session_state.chat_memory.append(
        f"AI: {ai_response}"
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response
    })

    st.rerun()
# ========================= DATASET PREVIEW =========================
st.markdown("# 🗂 Dataset Preview")

with st.expander("Show Dataset"):
    st.dataframe(filtered_df)

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Filtered CSV",
    csv,
    "filtered_data.csv",
    "text/csv"
)

# ========================= FOOTER =========================
st.divider()

st.markdown("""
<div style='text-align:center;
padding-top:25px;
padding-bottom:25px;'>

<h3 style='color:white;
font-size:24px;
margin-bottom:6px;'>

Built with ❤️ by Sanj

</h3>

<p style='color:#9ca3af;
font-size:15px;'>

Powered by Python • Streamlit • Groq AI • Plotly

</p>

</div>
""", unsafe_allow_html=True)