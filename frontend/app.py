import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API = "http://localhost:8000"

st.set_page_config(
    page_title="BI Agent — Amazon Sales",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f0f13; }
[data-testid="stSidebar"] { background: #16161d; border-right: 1px solid #2a2a3a; }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
.main-title { font-size: 2rem; font-weight: 700; color: #ffffff; margin-bottom: 0; }
.main-sub { font-size: 0.95rem; color: #888; margin-bottom: 1.5rem; }
.kpi-card {
    background: #1a1a24;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.kpi-label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #fff; }
.kpi-delta { font-size: 12px; margin-top: 4px; }
.kpi-positive { color: #4ade80; }
.kpi-negative { color: #f87171; }
.section-title { font-size: 1.1rem; font-weight: 600; color: #fff; margin: 1.5rem 0 0.75rem; }
.chat-answer {
    background: #1a1a24;
    border: 1px solid #2a2a3a;
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    padding: 16px 20px;
    color: #e0e0e0;
    font-size: 14px;
    line-height: 1.7;
    margin-top: 12px;
}
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.stButton button {
    background: #1e1e2e !important;
    color: #a0a0c0 !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    padding: 4px 14px !important;
}
.stButton button:hover {
    background: #6366f1 !important;
    color: #fff !important;
    border-color: #6366f1 !important;
}
div[data-testid="metric-container"] {
    background: #1a1a24;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 BI Agent")
    st.markdown("Amazon India Fashion Sales")
    st.divider()

    try:
        filt = requests.get(f"{API}/filters", timeout=5).json()
        cats = filt.get("categories", [])
        statuses = filt.get("statuses", [])
    except Exception:
        cats, statuses = [], []

    st.markdown("**Filter by Category**")
    sel_cats = st.multiselect("", cats, default=cats[:5] if cats else [], label_visibility="collapsed")

    st.markdown("**Filter by Status**")
    status_options = ["All Statuses"] + statuses
    sel_status = st.selectbox("", status_options, label_visibility="collapsed")

    st.divider()
    st.markdown("**Quick Actions**")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Load data ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_summary():
    try:
        return requests.get(f"{API}/summary", timeout=10).json()
    except Exception as e:
        return None

data = get_summary()

# ── Header ────────────────────────────────────────────────
st.markdown('<div class="main-title">AI-Powered Business Intelligence Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">Amazon India Fashion Sales · Real-time AI Analytics</div>', unsafe_allow_html=True)

if not data:
    st.error("Cannot connect to backend. Make sure `uvicorn backend.main:app --reload --port 8000` is running.")
    st.stop()

kpis = data["kpis"]

# ── KPI Row ───────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def fmt_inr(val):
    if val >= 1e7:
        return f"₹{val/1e7:.2f} Cr"
    elif val >= 1e5:
        return f"₹{val/1e5:.1f} L"
    return f"₹{val:,.0f}"

with k1:
    st.metric("Total Sales", fmt_inr(kpis["total_sales"]), delta="↑ Live data")
with k2:
    st.metric("Total Orders", f"{kpis['total_orders']:,}")
with k3:
    st.metric("Total Qty", f"{kpis['total_qty']:,}")
with k4:
    st.metric("Avg Order Value", f"₹{kpis['avg_order_value']:,.2f}")
with k5:
    st.metric("Cancel Rate", f"{kpis['cancel_rate']}%",
              delta=f"{kpis['cancel_rate']}% orders lost",
              delta_color="inverse")

st.divider()

# ── Charts Row 1 ──────────────────────────────────────────
col1, col2 = st.columns([1.2, 0.8])

with col1:
    st.markdown('<div class="section-title">Sales by Category</div>', unsafe_allow_html=True)
    cat_df = pd.DataFrame(data["by_category"])
    if not cat_df.empty:
        cat_df = cat_df[cat_df["Sales"] > 0].sort_values("Sales", ascending=True)
        if sel_cats:
            cat_df = cat_df[cat_df["Category"].isin(sel_cats)]
        fig = px.bar(cat_df, x="Sales", y="Category", orientation="h",
                     color="Sales", color_continuous_scale="Purples",
                     template="plotly_dark")
        fig.update_layout(
            plot_bgcolor="#1a1a24", paper_bgcolor="#1a1a24",
            coloraxis_showscale=False, margin=dict(t=10, b=10, l=10, r=10),
            height=320, xaxis_title="Revenue (₹)", yaxis_title=""
        )
        fig.update_traces(hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">Order Status Breakdown</div>', unsafe_allow_html=True)
    status_df = pd.DataFrame(data["by_status"])
    if not status_df.empty and sel_status == "All Statuses":
        fig2 = px.pie(status_df, names="Status", values="Sales",
                      template="plotly_dark", hole=0.5,
                      color_discrete_sequence=px.colors.sequential.Purples_r)
        fig2.update_layout(
            plot_bgcolor="#1a1a24", paper_bgcolor="#1a1a24",
            margin=dict(t=10, b=10, l=10, r=10), height=320,
            legend=dict(font=dict(size=10))
        )
        fig2.update_traces(hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>")
        st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────
col3, col4 = st.columns([1.2, 0.8])

with col3:
    st.markdown('<div class="section-title">Monthly Revenue Trend</div>', unsafe_allow_html=True)
    monthly_df = pd.DataFrame(data["monthly_trend"])
    if not monthly_df.empty:
        monthly_df = monthly_df[monthly_df["Sales"] > 0].sort_values("Month")
        fig3 = px.area(monthly_df, x="Month", y="Sales",
                       template="plotly_dark",
                       color_discrete_sequence=["#6366f1"])
        fig3.update_layout(
            plot_bgcolor="#1a1a24", paper_bgcolor="#1a1a24",
            margin=dict(t=10, b=10, l=10, r=10), height=280,
            xaxis_title="", yaxis_title="Revenue (₹)"
        )
        fig3.update_traces(
            fill="tozeroy", fillcolor="rgba(99,102,241,0.15)",
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown('<div class="section-title">Top 10 States by Revenue</div>', unsafe_allow_html=True)
    state_df = pd.DataFrame(data["by_state"])
    if not state_df.empty:
        fig4 = px.bar(state_df.sort_values("Sales"), x="Sales", y="State",
                      orientation="h", template="plotly_dark",
                      color_discrete_sequence=["#818cf8"])
        fig4.update_layout(
            plot_bgcolor="#1a1a24", paper_bgcolor="#1a1a24",
            margin=dict(t=10, b=10, l=10, r=10), height=280,
            xaxis_title="Revenue (₹)", yaxis_title=""
        )
        fig4.update_traces(hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>")
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── AI Chat ───────────────────────────────────────────────
st.markdown('<div class="section-title">Ask AI About Your Data</div>', unsafe_allow_html=True)

SAMPLES = [
    "Which category has the highest revenue?",
    "What is the cancellation rate?",
    "Which state has the most orders?",
    "How did sales trend month by month?",
    "What % of orders are B2B?",
    "Which fulfilment type performs better?",
]

cols = st.columns(3)
for i, q in enumerate(SAMPLES):
    if cols[i % 3].button(q, key=f"sq_{i}"):
        st.session_state["ai_question"] = q

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f'<div class="chat-answer">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

prefill = st.session_state.pop("ai_question", "")
question = st.chat_input("Ask anything about your sales data...")

if not question and prefill:
    question = prefill

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.markdown(f"**You:** {question}")
    with st.spinner("Analyzing data..."):
        try:
            res = requests.post(f"{API}/ask",
                                json={"question": question},
                                timeout=30).json()
            answer = res.get("answer", "Sorry, I could not get an answer.")
        except Exception as e:
            answer = f"Error connecting to AI: {e}"
    st.markdown(f'<div class="chat-answer">🤖 {answer}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": answer})

if st.session_state.messages:
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

st.divider()

# ── Data Table ────────────────────────────────────────────
with st.expander("📋 View Raw Data Sample"):
    try:
        df_raw = pd.read_csv("data/sales_data.csv", dtype=str, low_memory=False)
        df_raw.columns = df_raw.columns.str.strip()
        if sel_cats:
            df_raw = df_raw[df_raw["Category"].isin(sel_cats)]
        if sel_status != "All Statuses":
            df_raw = df_raw[df_raw["Status"] == sel_status]
        st.markdown(f"Showing {min(100, len(df_raw))} of {len(df_raw):,} rows")
        st.dataframe(df_raw.drop(columns=["index"], errors="ignore").head(100),
                     use_container_width=True, height=300)
        st.download_button(
            "⬇ Download Filtered Data as CSV",
            df_raw.to_csv(index=False),
            "filtered_sales_data.csv",
            "text/csv"
        )
    except Exception as e:
        st.error(f"Could not load data: {e}")