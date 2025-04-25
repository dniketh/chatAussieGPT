# main.py
import streamlit as st
from app.app_structure import setup_page_config, apply_custom_css
setup_page_config()
from app.chat_interface import render_chat_interface
from app.sidebar_components import render_sidebar
from app.competencies_component import render_competencies_assessment
from supabase import create_client
from dotenv import load_dotenv
import os
from utils.supabase_data_utils import fetch_saved_skills
from utils.visualizer import create_svg_skills_visualization,categorize_skills

load_dotenv()

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
    defaults = {
        "messages": [{
            "role": "assistant",
            "content": "Hi there! Welcome to chatAussieGPT. Tell me about your skills and interests, or upload your resume to get personalized career recommendations."
        }],
        "skills": [],
        "career_matches": [],
        "conversation_stage": "initial",
        "show_skills_map": False,
        "openai_api_key": "",
        "show_skills_popup": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

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
                if st.form_submit_button("Login"):
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
                if st.form_submit_button("Register"):
                    if not all([name, email, password, password_confirm]):
                        st.warning("Please fill all fields.")
                    elif password != password_confirm:
                        st.error("Passwords do not match.")
                    elif len(password) < 8:
                        st.warning("Password must be at least 8 characters.")
                    else:
                        try:
                            supabase = get_user_supabase()
                            supabase.auth.sign_up({
                                "email": email,
                                "password": password,
                                "options": {
                                    "data": {'name': name}
                                }
                            })
                            st.success("Registration successful! Check your email for verification.")
                        except Exception as e:
                            st.error(f"Registration failed: {e}")
    else:
        st.session_state['user'] = user_response
        user = user_response.user
        user_name = user.user_metadata.get('name', user.email)

        if not st.session_state.skills:
            try:
                saved_skills = fetch_saved_skills(supabase, user.id)
                if saved_skills:
                    st.session_state.skills = saved_skills
            except Exception as e:
                st.warning(f"Could not load saved skills: {e}")

        st.title("chatAussieGPT")
        st.markdown(f"#### Welcome, {user_name}!")

        if st.session_state.get("show_competencies", False):
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

        if st.session_state.get("show_skills_popup", False) and st.session_state.skills:
            st.markdown("<style>html, body { overflow: hidden !important; }</style>", unsafe_allow_html=True)
            st.subheader("Skills Visualization")

            api_key = st.session_state.get("openai_api_key", "")
            if not api_key:
                st.warning("Please provide your OpenAI API key to generate skill visualization.")
            else:
                categorized_skills = categorize_skills(supabase, user.id)
                svg = create_svg_skills_visualization(categorized_skills)
                st.components.v1.html(svg, height=800, width=1200, scrolling=True)
            if st.button("Close Visualization"):
                st.session_state.show_skills_popup = False
                st.markdown("<style>html, body { overflow: auto !important; }</style>", unsafe_allow_html=True)
                st.rerun()

if __name__ == "__main__":
    main()
