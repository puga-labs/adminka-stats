import streamlit as st
from datetime import datetime
from auth import check_password

# Page configuration
st.set_page_config(
    page_title="Crypto Analytics Admin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Check authentication
if check_password():
    # Header with title and logout
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("🚀 Crypto Analytics Admin Panel")
    with col2:
        st.markdown("")  # Empty line for alignment
        if st.button("🚪 Logout", help="Click to logout"):
            from auth import cookie_controller
            st.session_state["password_correct"] = False
            cookie_controller.remove("auth_token")
            st.rerun()
    
    st.markdown("---")

    # Welcome message
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("**[OK]** System Status: Online")
        
    with col2:
        st.info(f"**[INFO]** Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
    with col3:
        st.info("**[*]** Version: 0.1.0")

    st.markdown("## Navigation")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔑 API Keys Monitor", use_container_width=True, help="Monitor API usage and costs"):
            st.switch_page("pages/2_🔑_API_Keys.py")
    
    with col2:
        if st.button("⚙️ Processing Stats", use_container_width=True, help="Database statistics and processing status"):
            st.switch_page("pages/3_⚙️_Processing.py")

    # Placeholder for connection status
    st.markdown("## Quick Stats")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Messages Today", "N/A", help="Connect DB to see data")
        
    with col2:
        st.metric("Active Sources", "N/A", help="Connect DB to see data")
        
    with col3:
        st.metric("Processing Speed", "N/A msg/min", help="Connect DB to see data")
        
    with col4:
        st.metric("Error Rate", "N/A%", help="Connect DB to see data")

    # Footer
    st.markdown("---")
    st.caption("Crypto Analytics Monitoring System v0.1.0")
else:
    st.stop()