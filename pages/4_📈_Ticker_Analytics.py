import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Ticker Analytics", page_icon="📈", layout="wide")

st.title("📈 Ticker Analytics")
st.markdown("Search and analyze cryptocurrency ticker mentions")
st.markdown("---")

# Search section
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    ticker = st.text_input(
        "Search Ticker",
        placeholder="Enter ticker symbol (e.g., BTC, ETH, DOGE)",
        help="Search for a specific cryptocurrency ticker"
    )

with col2:
    date_range = st.selectbox(
        "Time Range",
        ["Last 24h", "Last 7d", "Last 30d", "Custom"],
        help="Select time range for analysis"
    )

with col3:
    search_button = st.button("Search", type="primary", use_container_width=True)

# Filter options
with st.expander("Advanced Filters"):
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        platforms = st.multiselect(
            "Platforms",
            ["All", "Telegram", "Twitter", "Discord", "Reddit", "YouTube"],
            default=["All"]
        )
    
    with filter_col2:
        sentiment_filter = st.multiselect(
            "Sentiment",
            ["All", "Positive", "Neutral", "Negative"],
            default=["All"]
        )

# Results section
if ticker and search_button:
    st.markdown(f"## Results for {ticker.upper()}")
    
    # Summary metrics
    met_col1, met_col2, met_col3, met_col4 = st.columns(4)
    
    with met_col1:
        st.metric("Total Mentions", "0")
    
    with met_col2:
        st.metric("Sentiment Score", "N/A")
    
    with met_col3:
        st.metric("Top Platform", "N/A")
    
    with met_col4:
        st.metric("Trend", "→ 0%")
    
    # Charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Mentions Over Time")
        st.info("**[INFO]** No data available for this ticker")
    
    with chart_col2:
        st.subheader("Sentiment Distribution")
        st.info("**[INFO]** No sentiment data available")
    
    # Recent mentions
    st.markdown("### Recent Mentions")
    df_mentions = pd.DataFrame({
        'Time': ['No data'],
        'Platform': ['-'],
        'Author': ['-'],
        'Content': ['-'],
        'Sentiment': ['-']
    })
    st.dataframe(df_mentions, use_container_width=True)
    
elif not ticker:
    # Default view - popular tickers
    st.markdown("## Trending Tickers")
    
    df_trending = pd.DataFrame({
        'Rank': [1, 2, 3, 4, 5],
        'Ticker': ['N/A'] * 5,
        'Mentions (24h)': [0] * 5,
        'Change': ['0%'] * 5,
        'Sentiment': ['Neutral'] * 5
    })
    
    st.dataframe(df_trending, use_container_width=True, hide_index=True)
    
    st.info("**[INFO]** Connect to database to see trending tickers")

# Export section
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.caption("Export data after search")

with col2:
    st.button("Export CSV", disabled=True, help="Search for a ticker first")

with col3:
    st.button("Export Report", disabled=True, help="Search for a ticker first")