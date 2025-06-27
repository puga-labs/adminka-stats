import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
from typing import List, Tuple, Optional, Dict
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import check_password

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Processing", page_icon="⚙️", layout="wide")

# Check authentication
if not check_password():
    st.stop()

# Header with navigation and refresh
col1, col2, col3, col4 = st.columns([1, 3, 1, 1])

with col1:
    if st.button("🏠 Home", use_container_width=True, help="Return to main page"):
        st.switch_page("app.py")

with col2:
    st.title("⚙️ Processing")
    st.markdown("Processing statistics for social media platforms")

with col3:
    if st.button("🔄 Refresh", use_container_width=True, help="Reload data from databases"):
        st.rerun()

with col4:
    if st.button("🚪 Logout", use_container_width=True, help="Click to logout"):
        from auth import cookie_controller
        st.session_state["password_correct"] = False
        cookie_controller.remove("auth_token")
        st.rerun()

# Show last update time
last_update = datetime.now()
st.caption(f"Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

# Database connection functions
def get_youtube_data() -> Dict:
    """Get YouTube data from database"""
    try:
        conn = psycopg2.connect(os.getenv("YOUTUBE_DATABASE_URL"))
        cur = conn.cursor()
        
        # Get distinct channel names
        cur.execute("""
            SELECT DISTINCT channel_name 
            FROM videos 
            WHERE channel_name IS NOT NULL 
            ORDER BY channel_name
        """)
        channels = [row[0] for row in cur.fetchall()]
        
        # Get total processing days count
        cur.execute("""
            SELECT COUNT(*) as total_days
            FROM videos 
            WHERE date IS NOT NULL
        """)
        total_days = cur.fetchone()[0]
        
        # Get processed dates for display
        cur.execute("""
            SELECT DISTINCT DATE(date) as process_date
            FROM videos 
            WHERE date IS NOT NULL 
            ORDER BY process_date DESC
        """)
        dates = [row[0] for row in cur.fetchall()]
        
        # Get channel statistics
        cur.execute("""
            SELECT channel_name, COUNT(*) as video_count
            FROM videos 
            WHERE channel_name IS NOT NULL
            GROUP BY channel_name
            ORDER BY video_count DESC
        """)
        channel_stats = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        return {
            "channels": channels,
            "dates": dates,
            "total_days": total_days,
            "channel_stats": channel_stats,
            "error": None
        }
    except Exception as e:
        return {
            "channels": [],
            "dates": [],
            "total_days": 0,
            "channel_stats": {},
            "error": f"Connection error: {str(e)}"
        }

def get_twitter_data() -> Dict:
    """Get Twitter data from database"""
    try:
        conn = psycopg2.connect(os.getenv("TWITTER_DATABASE_URL"))
        cur = conn.cursor()
        
        # Get distinct twitter names
        cur.execute("""
            SELECT DISTINCT twitter_name 
            FROM daily_summaries 
            WHERE twitter_name IS NOT NULL 
            ORDER BY twitter_name
        """)
        users = [row[0] for row in cur.fetchall()]
        
        # Get total processing days count
        cur.execute("""
            SELECT COUNT(*) as total_days
            FROM daily_summaries 
            WHERE summary_date IS NOT NULL
        """)
        total_days = cur.fetchone()[0]
        
        # Get processed dates for display
        cur.execute("""
            SELECT DISTINCT DATE(summary_date) as process_date
            FROM daily_summaries 
            WHERE summary_date IS NOT NULL 
            ORDER BY process_date DESC
        """)
        dates = [row[0] for row in cur.fetchall()]
        
        # Get user statistics
        cur.execute("""
            SELECT twitter_name, COUNT(*) as tweet_count
            FROM daily_summaries 
            WHERE twitter_name IS NOT NULL
            GROUP BY twitter_name
            ORDER BY tweet_count DESC
        """)
        user_stats = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        return {
            "users": users,
            "dates": dates,
            "total_days": total_days,
            "user_stats": user_stats,
            "error": None
        }
    except Exception as e:
        return {
            "users": [],
            "dates": [],
            "total_days": 0,
            "user_stats": {},
            "error": f"Connection error: {str(e)}"
        }

def get_telegram_data() -> Dict:
    """Get Telegram data from database"""
    try:
        conn = psycopg2.connect(os.getenv("TELEGRAM_DATABASE_URL"))
        cur = conn.cursor()
        
        # Get distinct group names
        cur.execute("""
            SELECT DISTINCT group_name 
            FROM daily_summaries 
            WHERE group_name IS NOT NULL 
            ORDER BY group_name
        """)
        groups = [row[0] for row in cur.fetchall()]
        
        # Get total processing days count
        cur.execute("""
            SELECT COUNT(*) as total_days
            FROM daily_summaries 
            WHERE summary_date IS NOT NULL
        """)
        total_days = cur.fetchone()[0]
        
        # Get processed dates for display
        cur.execute("""
            SELECT DISTINCT DATE(summary_date) as process_date
            FROM daily_summaries 
            WHERE summary_date IS NOT NULL 
            ORDER BY process_date DESC
        """)
        dates = [row[0] for row in cur.fetchall()]
        
        # Get group statistics
        cur.execute("""
            SELECT group_name, COUNT(*) as message_count
            FROM daily_summaries 
            WHERE group_name IS NOT NULL
            GROUP BY group_name
            ORDER BY message_count DESC
        """)
        group_stats = {row[0]: row[1] for row in cur.fetchall()}
        
        cur.close()
        conn.close()
        
        return {
            "groups": groups,
            "dates": dates,
            "total_days": total_days,
            "group_stats": group_stats,
            "error": None
        }
    except Exception as e:
        return {
            "groups": [],
            "dates": [],
            "total_days": 0,
            "group_stats": {},
            "error": f"Connection error: {str(e)}"
        }

# Get data from databases
youtube_data = get_youtube_data()
twitter_data = get_twitter_data()
telegram_data = get_telegram_data()

# Summary section with compact cards
st.subheader("Summary")
col1, col2, col3 = st.columns(3)

# YouTube card
with col1:
    with st.container(border=True):
        st.subheader("YouTube")
        
        if youtube_data["error"]:
            st.error(youtube_data["error"])
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(label="Channels", value=len(youtube_data["channels"]))
            with col_b:
                st.metric(label="Days", value=youtube_data["total_days"])
            
            if not youtube_data["channels"]:
                st.info("No data yet")

# Twitter card
with col2:
    with st.container(border=True):
        st.subheader("Twitter")
        
        if twitter_data["error"]:
            st.error(twitter_data["error"])
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(label="Users", value=len(twitter_data["users"]))
            with col_b:
                st.metric(label="Days", value=twitter_data["total_days"])
            
            if not twitter_data["users"]:
                st.info("No data yet")

# Telegram card
with col3:
    with st.container(border=True):
        st.subheader("Telegram")
        
        if telegram_data["error"]:
            st.error(telegram_data["error"])
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(label="Groups", value=len(telegram_data["groups"]))
            with col_b:
                st.metric(label="Days", value=telegram_data["total_days"])
            
            if not telegram_data["groups"]:
                st.info("No data yet")

# Detailed sections
st.markdown("---")
st.subheader("Detailed Information")

# YouTube details
with st.expander("YouTube Details", expanded=True):
    if youtube_data["error"]:
        st.error(youtube_data["error"])
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Processed Dates")
            if youtube_data["dates"]:
                st.markdown(f"**Date range:** {youtube_data['dates'][-1]} to {youtube_data['dates'][0]}")
                st.markdown(f"**Total days:** {youtube_data['total_days']}")
                
                # Show recent dates
                st.markdown("**Recent dates:**")
                for date in youtube_data["dates"][:5]:
                    st.markdown(f"- {date}")
                if len(youtube_data["dates"]) > 5:
                    st.caption(f"... and {len(youtube_data['dates']) - 5} more")
            else:
                st.info("No processed dates yet")
        
        with col2:
            st.markdown("### Channel Statistics")
            if youtube_data["channel_stats"]:
                # Create DataFrame for display
                import pandas as pd
                df = pd.DataFrame(
                    [(k, v) for k, v in youtube_data["channel_stats"].items()],
                    columns=["Channel", "Videos"]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No channel data yet")

# Twitter details
with st.expander("Twitter Details", expanded=True):
    if twitter_data["error"]:
        st.error(twitter_data["error"])
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Processed Dates")
            if twitter_data["dates"]:
                st.markdown(f"**Date range:** {twitter_data['dates'][-1]} to {twitter_data['dates'][0]}")
                st.markdown(f"**Total days:** {twitter_data['total_days']}")
                
                # Show recent dates
                st.markdown("**Recent dates:**")
                for date in twitter_data["dates"][:5]:
                    st.markdown(f"- {date}")
                if len(twitter_data["dates"]) > 5:
                    st.caption(f"... and {len(twitter_data['dates']) - 5} more")
            else:
                st.info("No processed dates yet")
        
        with col2:
            st.markdown("### User Statistics")
            if twitter_data["user_stats"]:
                # Create DataFrame for display
                import pandas as pd
                df = pd.DataFrame(
                    [(k, v) for k, v in twitter_data["user_stats"].items()],
                    columns=["User", "Summaries"]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No user data yet")

# Telegram details
with st.expander("Telegram Details", expanded=True):
    if telegram_data["error"]:
        st.error(telegram_data["error"])
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Processed Dates")
            if telegram_data["dates"]:
                st.markdown(f"**Date range:** {telegram_data['dates'][-1]} to {telegram_data['dates'][0]}")
                st.markdown(f"**Total days:** {telegram_data['total_days']}")
                
                # Show recent dates
                st.markdown("**Recent dates:**")
                for date in telegram_data["dates"][:5]:
                    st.markdown(f"- {date}")
                if len(telegram_data["dates"]) > 5:
                    st.caption(f"... and {len(telegram_data['dates']) - 5} more")
            else:
                st.info("No processed dates yet")
        
        with col2:
            st.markdown("### Group Statistics")
            if telegram_data["group_stats"]:
                # Create DataFrame for display
                import pandas as pd
                df = pd.DataFrame(
                    [(k, v) for k, v in telegram_data["group_stats"].items()],
                    columns=["Group", "Summaries"]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No group data yet")