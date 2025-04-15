import streamlit as st
from app.app_structure import (
    setup_page_config,
    apply_custom_css
)
from app.chat_interface import render_chat_interface
from app.sidebar_components import render_sidebar
from app.competencies_component import render_competencies_assessment
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

setup_page_config()


@st.cache_resource
def init_supabase_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    try:
        client = create_client(url, key)
        st.success("Connected to Supabase!")
        return client
    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        return None
supabase = init_supabase_connection()



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
    initialize_session_state()
    apply_custom_css()

    if not supabase:
         st.error("Database connection failed. Please check secrets or Supabase status.")
         return
    try:
        session = supabase.auth.get_session()
        user_response = supabase.auth.get_user() if session else None
    except Exception as e:
        st.error(f"Error checking Supabase session: {e}")
        user_response = None
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Discover your career path in Australia based on your skills and interests"}]

    if not user_response:
        st.title("Welcome to chatAussieGPT")
        st.markdown("#### Log in or register to continue")

        choice = st.radio("Select Action", ["Login", "Register"], horizontal=True)

        if choice == "Login":
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    try:
                        session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.success("Login successful!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")

        elif choice == "Register":
             with st.form("register_form"):
                name = st.text_input("Your Name") # Optional, for profile
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                password_confirm = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Register")
                if submitted:
                    if not all([name, email, password, password_confirm]):
                         st.warning("Please fill all fields.")
                    elif password != password_confirm:
                         st.error("Passwords do not match.")
                    elif len(password) < 8:
                        st.warning("Password must be at least 8 characters.")
                    else:
                         try:
                             res = supabase.auth.sign_up({
                                 "email": email,
                                 "password": password,
                                 "options": {
                                     "data": {
                                         'name': name
                                     }
                                 }
                             })
                             st.success("Registration successful! Check your email for verification (if enabled). Please log in.")
                         except Exception as e:
                             st.error(f"Registration failed: {e}")

    else:
        st.session_state['user'] = user_response
        user = user_response.user
        user_name = user.user_metadata.get('name', user.email)
        st.title("chatAussieGPT")
        st.markdown(f"#### Welcome, {user_name}!")

        show_competencies = st.session_state.get("show_competencies", False)

        if show_competencies:
            render_competencies_assessment(st, supabase, user)
            if st.button("Back to Chat"):
                st.session_state.show_competencies = False
                st.rerun()
        else:
            render_chat_interface(supabase, user)


        with st.sidebar:
             st.write(f"Logged in as: {user_name}")
             if st.button("Logout"):
                  supabase.auth.sign_out()
                  st.session_state.pop('user', None)
                  st.rerun()
             st.divider()
             render_sidebar(supabase, user)

if __name__ == "__main__":
    main()