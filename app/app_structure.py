import streamlit as st


# def setup_page_config():
#     """Configure the Streamlit page settings."""
#     st.set_page_config(
#         page_title="chatAussieGPT",
#         page_icon="🧭",
#         layout="wide",
#         initial_sidebar_state="collapsed"
#     )

def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="chatAussieGPT",
        page_icon="🇦🇺",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    """Apply custom CSS styling to the application."""
    st.markdown("""
    <style>
        .main {padding-top: 1rem;}
        .stTextInput {margin-bottom: 0.5rem;}
        .chat-message {padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;}
        .user-message {background-color: #e6f7ff;}
        .assistant-message {background-color: #f0f0f0;}
        .stButton button {width: 100%;}
        .skill-tag {
            display: inline-block;
            background-color: #f0f7fa;
            border: 1px solid #cfe2f3;
            border-radius: 16px;
            padding: 4px 12px;
            margin: 4px;
            font-size: 14px;
        }
        .suggestion-button button {
            text-align: left;
            background-color: #f9f9f9;
            border: 1px solid #e0e0e0;
        }
        .career-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .stProgress > div > div > div > div {
            background-color: #4e8cff;
        }
    </style>
    """, unsafe_allow_html=True)


def is_mobile():
    """
    Check if user is on a mobile device.

    Returns:
        bool: True if on mobile, False otherwise
    """
    try:
        # This is a simplified check - in production you would use a more reliable method
        return st.session_state.get("screen_width", 1200) < 768
    except AttributeError:
        return False


def get_layout():
    """
    Determine the appropriate layout based on device.

    Returns:
        tuple: Main column and side column
    """
    is_mobile_device = is_mobile()

    if is_mobile_device:
        # Mobile-friendly layout (stacked)
        main_col = st.container()
        side_col = st.container()
    else:
        # Desktop layout (side-by-side)
        main_col, side_col = st.columns([2, 1])

    return main_col, side_col