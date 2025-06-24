import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.markdown("System overview and real-time statistics")
st.markdown("---")

# Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Messages (24h)",
        value="0",
        delta="0",
        help="Total messages processed in last 24 hours"
    )

with col2:
    st.metric(
        label="Active Sources", 
        value="0",
        help="Number of active data sources"
    )

with col3:
    st.metric(
        label="Top Ticker",
        value="N/A",
        help="Most mentioned ticker today"
    )

with col4:
    st.metric(
        label="Processing Speed",
        value="0 msg/min",
        delta="0%",
        help="Current processing speed"
    )

# Placeholder charts
st.markdown("## Activity Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hourly Activity (Last 24h)")
    # Placeholder data
    hours = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                         end=datetime.now(), freq='h')
    df_hourly = pd.DataFrame({
        'Hour': hours,
        'Messages': [0] * len(hours)
    })
    fig = px.line(df_hourly, x='Hour', y='Messages', 
                  title="Message Processing Timeline")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Platform Distribution")
    # Placeholder data
    df_platforms = pd.DataFrame({
        'Platform': ['Telegram', 'Twitter', 'Discord', 'Reddit', 'YouTube'],
        'Count': [0, 0, 0, 0, 0]
    })
    fig = px.pie(df_platforms, values='Count', names='Platform',
                 title="Messages by Platform")
    st.plotly_chart(fig, use_container_width=True)

# Top tickers table
st.markdown("## Top Mentioned Tickers")
df_tickers = pd.DataFrame({
    'Ticker': ['No data'],
    'Mentions': [0],
    'Sentiment': ['N/A'],
    'Change 24h': ['0%']
})
st.dataframe(df_tickers, use_container_width=True)

# System status
st.markdown("## System Status")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.success("**[OK]** Database Connection: Not configured")
    
with status_col2:
    st.info("**[INFO]** Last Data Update: Never")
    
with status_col3:
    st.warning("**[WARNING]** Configure database in .env file")