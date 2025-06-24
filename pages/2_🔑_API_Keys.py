import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_monitors import get_cached_balances, get_status_color, calculate_deepseek_stats

st.set_page_config(page_title="API Keys Monitor", page_icon="🔑", layout="wide")

st.title("🔑 DeepSeek API Monitor")
st.markdown("Track DeepSeek API balances and usage")
st.markdown("---")

# Refresh button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Show loading state
with st.spinner("Checking DeepSeek API balances..."):
    try:
        # Get API balance data
        api_results = get_cached_balances()
        
        # Calculate statistics
        stats = calculate_deepseek_stats(api_results)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Balance",
                value=f"${stats['total_balance']:.2f}",
                help="Sum of all DeepSeek balances"
            )
        
        with col2:
            st.metric(
                label="Average Balance",
                value=f"${stats['average_balance']:.2f}",
                help="Average balance per active key"
            )
        
        with col3:
            st.metric(
                label="Lowest Balance",
                value=f"${stats['lowest_balance']:.2f}",
                delta=f"-${stats['average_balance'] - stats['lowest_balance']:.2f}" if stats['lowest_balance'] > 0 else None,
                help="Lowest balance among active keys"
            )
        
        with col4:
            st.metric(
                label="Active Keys",
                value=f"{stats['active_keys']}/{stats['total_keys']}",
                help="Active keys out of total"
            )
        
        # API Status Table
        st.markdown("## DeepSeek API Keys Status")
        
        # Convert results to DataFrame
        df_apis = pd.DataFrame(api_results)
        
        # Remove hidden fields from display
        display_columns = [col for col in df_apis.columns if not col.startswith('_')]
        df_display = df_apis[display_columns].copy()
        
        # Add status indicator
        def format_status(status):
            colors = {
                "active": "🟢",
                "insufficient": "🟡",
                "error": "🔴",
                "not_configured": "⚫",
                "unknown": "⚫"
            }
            return f"{colors.get(status, '⚫')} {status.title()}"
        
        df_display['Status'] = df_display['Status'].apply(format_status)
        
        # Display table with custom styling
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Service": st.column_config.TextColumn("API Key", width="medium"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Total Balance": st.column_config.TextColumn("Total Balance", width="small"),
                "Granted": st.column_config.TextColumn("Granted", width="small"),
                "Topped Up": st.column_config.TextColumn("Topped Up", width="small"),
                "Last Check": st.column_config.TextColumn("Last Check", width="small"),
                "Error": st.column_config.TextColumn("Error", width="medium")
            }
        )
        
        # Detailed view with progress bars
        st.markdown("## Balance Details")
        
        # Create columns for each key
        cols = st.columns(3)
        
        for i, result in enumerate(api_results):
            with cols[i % 3]:
                with st.container():
                    st.subheader(result["Service"])
                    
                    if result["Status"] == "active":
                        # Get balance value for progress calculation
                        balance_value = result.get("_balance_value", 0)
                        
                        # Progress bar (assuming $100 is full)
                        progress = min(balance_value / 100, 1.0)
                        
                        # Color based on balance
                        if balance_value < 10:
                            st.error(f"Low Balance: {result['Total Balance']}")
                        elif balance_value < 25:
                            st.warning(f"Balance: {result['Total Balance']}")
                        else:
                            st.success(f"Balance: {result['Total Balance']}")
                        
                        # Progress bar
                        st.progress(progress, text=f"{int(progress * 100)}% of $100")
                        
                        # Additional details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption(f"Granted: {result['Granted']}")
                        with col2:
                            st.caption(f"Topped Up: {result['Topped Up']}")
                            
                    elif result["Status"] == "not_configured":
                        st.info("Not configured")
                        st.caption("Add key to .env file")
                    else:
                        st.error(f"Error: {result.get('Error', 'Unknown error')}")
                    
                    st.divider()
        
        # Usage tips
        st.markdown("## Balance Management Tips")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Low Balance Warning**
            - Keys with < $10 are considered low
            - Top up before balance reaches $0
            - Monitor usage patterns regularly
            """)
            
        with col2:
            st.info("""
            **Balance Types**
            - **Granted**: Free credits from DeepSeek
            - **Topped Up**: Credits you purchased
            - **Total**: Sum of both types
            """)
        
        # Last update time
        st.markdown("---")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Cache refreshes every 5 minutes")
        
    except Exception as e:
        st.error(f"**[ERROR]** Failed to check API balances: {str(e)}")
        st.info("Make sure you have configured your DeepSeek API keys in the .env file")

# Configuration helper
with st.expander("How to configure DeepSeek monitoring"):
    st.markdown("""
    1. Copy `.env.example` to `.env`
    2. Add your DeepSeek API keys:
       ```
       DEEPSEEK_API_KEY_1=sk-xxxxxxxxxxxx
       DEEPSEEK_API_KEY_2=sk-xxxxxxxxxxxx
       DEEPSEEK_API_KEY_3=sk-xxxxxxxxxxxx
       ```
    3. Run `poetry install` to install dependencies
    4. Restart the application
    
    **Getting DeepSeek API Keys:**
    1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
    2. Create an account or login
    3. Generate API keys in the dashboard
    4. DeepSeek provides free credits for new accounts
    """)