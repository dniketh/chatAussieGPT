import streamlit as st
from app.app_structure import setup_page_config, apply_custom_css
setup_page_config()
from app.chat_interface import render_chat_interface
from app.sidebar_components import render_sidebar
from app.competencies_component import render_competencies_assessment
from utils.supabase_client import supabase
from dotenv import load_dotenv
from utils.visualizer import create_svg_skills_visualization, categorize_skills_with_gpt

# Setup
load_dotenv()


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
    if "show_skills_popup" not in st.session_state:
        st.session_state.show_skills_popup = False

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

        # ✅ Show skills popup (visualization)
        if st.session_state.get("show_skills_popup", False) and st.session_state.skills:
            st.markdown("""
        <style>
            /* Disable background scroll */
            html, body {
            overflow: hidden !important;
        }

        /* Dimmed background overlay */
        .popup-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.6);
            z-index: 10000;
        }

        /* Actual popup content */
        .popup-content {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            max-width: 1000px;
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            z-index: 10001;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            overflow-y: auto;
            max-height: 90vh;
        }
        </style>
        """, unsafe_allow_html=True)

            
            st.subheader("Skills Visualization")

            api_key = st.session_state.get("openai_api_key", "")
            if not api_key:
                st.warning("Please provide your OpenAI API key to generate skill visualization.")
            else:
                # Categorize skills using GPT
                categorized_skills = categorize_skills_with_gpt(st.session_state.skills, api_key)
                svg = create_svg_skills_visualization(categorized_skills)
                height = svg.count('<circle') * 100 + 400
                # After the SVG chart code
                st.components.v1.html(svg, height=800, width=1200, scrolling=True)

            # Place the "Close Visualization" button directly after the chart
            if st.button("Close Visualization"):
                st.session_state.show_skills_popup = False
                # Re-enable body scroll after closing the popup
                st.markdown("<style>html, body { overflow: auto !important; }</style>", unsafe_allow_html=True)
                st.rerun()
            
            st.markdown("<style>html, body { overflow: auto !important; }</style>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
