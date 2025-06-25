import streamlit as st
from datetime import datetime
from auth import check_password, show_logout_button

# Page configuration
st.set_page_config(
    page_title="Crypto Analytics Admin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication
if check_password():
    # Show logout button in sidebar
    show_logout_button()
    
    # Main page
    st.title("🚀 Crypto Analytics Admin Panel")
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
    st.markdown("""
    Use the sidebar to navigate between pages:
    - **🔑 API Keys** - Monitor API usage and costs
    - **⚙️ Processing** - Database statistics and processing status
    """)

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