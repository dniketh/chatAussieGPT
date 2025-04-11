import streamlit as st
import os
# Import app modules
from app.app_structure import (
    setup_page_config,
    apply_custom_css,
    get_layout
)
from app.chat_interface import render_chat_interface
from app.sidebar_components import render_sidebar
from app.competencies_component import render_competencies_assessment








def initialize_session_state():
    """Initialize all session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi there! Welcome to chatAussieGPT. Tell me about your skills and interests, or upload your resume to get personalized career recommendations."}
        ]
    if "skills" not in st.session_state:
        st.session_state.skills = []
    if "career_matches" not in st.session_state:
        st.session_state.career_matches = []
    if "conversation_stage" not in st.session_state:
        st.session_state.conversation_stage = "initial"
    if "show_skills_map" not in st.session_state:
        st.session_state.show_skills_map = False
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""






def main():
    """Main entry point"""
    # Initialize session state first
    initialize_session_state()
    setup_page_config()
    apply_custom_css()

    # App header
    st.title("chatAussieGPT")
    st.markdown("#### Discover your career path in Australia based on your skills and interests")

    # Determine if we should show competencies assessment
    show_competencies = st.session_state.get("show_competencies", False)

    if show_competencies:
        # Render competencies assessment
        render_competencies_assessment(st)

        # Add button to return to main view
        if st.button("Back to Main View"):
            st.session_state.show_competencies = False
            st.experimental_rerun()
    else:
        # Render chat interface
        render_chat_interface(st)

        # Render sidebar
        with st.sidebar:
            render_sidebar(st)


if __name__ == "__main__":
    main()