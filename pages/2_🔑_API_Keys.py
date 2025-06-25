import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_monitors import get_cached_balances, calculate_api_stats, ping_all_apis
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import check_password

st.set_page_config(page_title="API Keys Monitor", page_icon="🔑", layout="wide")

# Check authentication
if not check_password():
    st.stop()

def recreate_ping_display(ping_status: str, ping_time: float) -> str:
    """Recreate ping display based on status and time"""
    if ping_status == "not_tested":
        return "⚪ Not tested"
    elif ping_status == "success":
        if ping_time < 3:
            return f"🟢 {ping_time}s"
        else:
            return f"🟡 {ping_time}s (slow)"
    elif ping_status == "timeout":
        return "🔴 Timeout"
    elif ping_status == "quota_exceeded":
        return "🟡 Quota exceeded"
    elif ping_status == "invalid_key":
        return "🔴 Invalid key"
    elif ping_status == "not_configured":
        return "⚫ Not configured"
    else:
        return "🔴 Failed"

# Header with navigation
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if st.button("🏠 Home", use_container_width=True, help="Return to main page"):
        st.switch_page("app.py")

with col2:
    st.title("🔑 API Monitor")
    st.markdown("Track DeepSeek balances and Gemini status")

with col3:
    if st.button("🚪 Logout", use_container_width=True, help="Click to logout"):
        from auth import cookie_controller
        st.session_state["password_correct"] = False
        cookie_controller.remove("auth_token")
        st.rerun()

st.markdown("---")

# Control buttons
col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
with col2:
    if st.button("🔄 Refresh All", use_container_width=True):
        st.cache_data.clear()
        # Clear ping results on full refresh
        if 'ping_results' in st.session_state:
            del st.session_state['ping_results']
        if 'ping_timestamp' in st.session_state:
            del st.session_state['ping_timestamp']
        st.rerun()

with col3:
    test_ping = st.button("🏓 Test Ping", use_container_width=True)

with col4:
    if st.button("🗑️ Clear Ping", use_container_width=True):
        if 'ping_results' in st.session_state:
            del st.session_state['ping_results']
        if 'ping_timestamp' in st.session_state:
            del st.session_state['ping_timestamp']
        st.rerun()

# Handle ping test separately
if test_ping:
    st.markdown("## 🏓 Ping Test Results")
    
    with st.spinner(f"🚀 Testing APIs in parallel..."):
        start_time = datetime.now()
        ping_results = ping_all_apis()
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Store ping results in session state to persist them
        st.session_state['ping_results'] = ping_results
        st.session_state['ping_timestamp'] = datetime.now()
        
        # Count actual tests performed
        actual_count = len([r for r in ping_results if r.get('ping_status') != 'not_configured'])
        
        st.success(f"✅ All {actual_count} ping tests completed in {total_time:.2f} seconds (parallel execution)")
        
        # Display ping results in a nice format
        for result in ping_results:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
            
            with col1:
                st.write(f"**{result['service']}**")
            
            with col2:
                ping_status = result.get('ping_status', 'unknown')
                if ping_status == 'success':
                    st.success("✅ Success")
                elif ping_status == 'timeout':
                    st.error("🔴 Timeout")
                elif ping_status == 'quota_exceeded':
                    st.warning("🟡 Quota exceeded")
                else:
                    st.error(f"❌ {ping_status}")
            
            with col3:
                ping_time = result.get('ping_time', 0)
                if ping_time > 0:
                    st.metric("Response time", f"{ping_time}s")
                else:
                    st.write("-")
            
            with col4:
                ping_response = result.get('ping_response', '')
                if ping_response:
                    st.code(ping_response[:50] + "..." if len(ping_response) > 50 else ping_response)
                elif result.get('ping_error'):
                    st.error(result['ping_error'][:50] + "..." if len(result['ping_error']) > 50 else result['ping_error'])
                else:
                    st.write("-")
        
        st.divider()

# Show loading state
with st.spinner("Checking API balances..."):
    try:
        # Get API balance data
        api_results = get_cached_balances()
        
        # Merge with stored ping results if available
        if 'ping_results' in st.session_state:
            ping_results = st.session_state['ping_results']
            
            # Validate that ping results match current API keys
            current_services = {r.get('Service', '') for r in api_results}
            ping_services = {pr['service'] for pr in ping_results}
            
            # If services don't match, clear outdated ping results
            if current_services != ping_services:
                del st.session_state['ping_results']
                if 'ping_timestamp' in st.session_state:
                    del st.session_state['ping_timestamp']
            else:
                # Create a dictionary for O(1) lookup
                ping_dict = {pr['service']: pr for pr in ping_results}
                
                # Update api_results with ping data
                for api_result in api_results:
                    service_name = api_result.get('Service', '')
                    if service_name in ping_dict:
                        ping_result = ping_dict[service_name]
                        # Update internal fields - display formatting is already done in _format_result
                        api_result['_ping_status'] = ping_result.get('ping_status', 'not_tested')
                        api_result['_ping_time'] = ping_result.get('ping_time', 0)
                        api_result['_ping_response'] = ping_result.get('ping_response', '')
                        # Re-format the Ping Test field with updated data
                        api_result['Ping Test'] = recreate_ping_display(
                            ping_result.get('ping_status', 'not_tested'),
                            ping_result.get('ping_time', 0)
                        )
        
        # Calculate statistics
        stats = calculate_api_stats(api_results)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="DeepSeek Balance",
                value=f"${stats['deepseek']['total_balance']:.2f}",
                help="Sum of all DeepSeek balances"
            )
        
        with col2:
            st.metric(
                label="DeepSeek Keys",
                value=f"{stats['deepseek']['active_keys']}/{stats['deepseek']['total_keys']}",
                help="Active DeepSeek keys"
            )
        
        with col3:
            gemini_active = stats['gemini']['active']
            gemini_status_text = "Active" if gemini_active else "Inactive"
            st.metric(
                label="Gemini Status", 
                value=gemini_status_text,
                help="Google Gemini API key status"
            )
        
        with col4:
            st.metric(
                label="Total APIs",
                value=f"{stats['overall']['active_apis']}/{stats['overall']['total_apis']}",
                help="Active APIs out of total configured"
            )
        
        # API Status Table
        st.markdown("## API Services Status")
        
        # Convert results to DataFrame
        df_apis = pd.DataFrame(api_results)
        
        # Remove hidden fields from display
        display_columns = [col for col in df_apis.columns if not col.startswith('_')]
        df_display = df_apis[display_columns].copy()
        
        # Status is already formatted in _format_result, no need to reformat
        
        # Display table with custom styling
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Service": st.column_config.TextColumn("Service", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Total Balance": st.column_config.TextColumn("Balance", width="small"),
                "Granted": st.column_config.TextColumn("Granted", width="small"),
                "Topped Up": st.column_config.TextColumn("Topped Up", width="small"),
                "Ping Test": st.column_config.TextColumn("Ping Test", width="small"),
                "Error": st.column_config.TextColumn("Error", width="medium")
            }
        )
        
        # Gemini details only (simplified)
        gemini_results = [r for r in api_results if r.get("_api_type") == "gemini"]
        if gemini_results and gemini_results[0].get("Status") != "not_configured":
            with st.expander("ℹ️ Google Gemini Notes", expanded=False):
                gemini = gemini_results[0]
                st.info("""
                **Limited Monitoring** - Google Gemini doesn't provide APIs for:
                - Account balance
                - Usage quotas  
                - Cost tracking
                
                We can only validate API key status and run ping tests.
                """)
                if gemini.get("_dashboard_url"):
                    st.markdown(f"For detailed monitoring use: [Google Cloud Console]({gemini['_dashboard_url']})")
        
    except Exception as e:
        st.error(f"**[ERROR]** Failed to check API balances: {str(e)}")
        st.info("Make sure you have configured your API keys in the .env file")