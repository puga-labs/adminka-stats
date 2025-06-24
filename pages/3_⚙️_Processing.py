import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Processing Monitor", page_icon="⚙️", layout="wide")

st.title("⚙️ Processing Monitor")
st.markdown("Track processing queue, errors, and performance")
st.markdown("---")

# Processing metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Queue Size",
        value="0",
        delta="0",
        help="Current tasks in queue"
    )

with col2:
    st.metric(
        label="Processing",
        value="0",
        help="Tasks currently being processed"
    )

with col3:
    st.metric(
        label="Completed (24h)",
        value="0",
        help="Tasks completed in last 24 hours"
    )

with col4:
    st.metric(
        label="Error Rate",
        value="0%",
        delta="0%",
        help="Percentage of failed tasks"
    )

# Task queue
st.markdown("## Current Queue")

# Placeholder data
df_queue = pd.DataFrame({
    'Task ID': ['No tasks'],
    'Type': ['-'],
    'Status': ['-'],
    'Created': ['-'],
    'Duration': ['-']
})

st.dataframe(df_queue, use_container_width=True)

# Error monitoring
st.markdown("## Recent Errors")

tab1, tab2 = st.tabs(["Error Summary", "Error Details"])

with tab1:
    df_errors = pd.DataFrame({
        'Error Type': ['No errors'],
        'Count (24h)': [0],
        'Last Occurrence': ['-'],
        'Severity': ['-']
    })
    st.dataframe(df_errors, use_container_width=True)

with tab2:
    st.info("**[INFO]** No errors in the last 24 hours")

# Performance metrics
st.markdown("## Performance Metrics")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Processing Time")
    df_perf = pd.DataFrame({
        'Task Type': ['Telegram', 'Twitter', 'Discord', 'Reddit', 'YouTube'],
        'Avg Time (s)': [0, 0, 0, 0, 0]
    })
    st.bar_chart(df_perf.set_index('Task Type'))

with col2:
    st.subheader("Worker Status")
    st.info("**[INFO]** Worker status not available - DB not connected")

# System health
st.markdown("## System Health")
health_col1, health_col2, health_col3 = st.columns(3)

with health_col1:
    st.success("**[OK]** Queue Service: Waiting for DB")
    
with health_col2:
    st.success("**[OK]** Workers: Not configured")
    
with health_col3:
    st.warning("**[WARNING]** Configure database connection")