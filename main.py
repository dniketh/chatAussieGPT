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


def get_user_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    client = create_client(url, key)

    if "supabase_session" in st.session_state:
        client.auth.set_session(
            st.session_state.supabase_session["access_token"],
            st.session_state.supabase_session["refresh_token"]
        )
    return client


def initialize_session_state():
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

    try:
        supabase = get_user_supabase()
    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        return

    try:
        session = supabase.auth.get_session()
        user_response = supabase.auth.get_user() if session else None
    except Exception as e:
        st.error(f"Error checking Supabase session: {e}")
        user_response = None

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
                        supabase = get_user_supabase()
                        session = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.supabase_session = {
                            "access_token": session.session.access_token,
                            "refresh_token": session.session.refresh_token
                        }
                        st.success("Login successful!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")

        elif choice == "Register":
            with st.form("register_form"):
                name = st.text_input("Your Name")
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
                            supabase = get_user_supabase()
                            res = supabase.auth.sign_up({
                                "email": email,
                                "password": password,
                                "options": {
                                    "data": {
                                        'name': name
                                    }
                                }
                            })
                            st.success("Registration successful! Check your email for verification.")
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
                st.session_state.clear()
                st.rerun()
            st.divider()
            render_sidebar(supabase, user)


if __name__ == "__main__":
    main()

