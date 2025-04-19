import streamlit as st
from utils.resume_parser import extract_text_from_resume, extract_skills_from_resume, parse_resume
from utils.visualizer import create_svg_skills_visualization
from utils.supabase_client import supabase

def render_sidebar(supabase, user_id):
    """
    Render the sidebar components.
    Args:
        supabase: Supabase client object
        user_id: Authenticated user ID
    """
    with st.container():
        st.subheader("Quick Actions")

        # API key input section
        render_api_key_input()

        # Resume upload component
        render_resume_upload(user_id)

        # Add link to core competencies assessment
        if st.button("Assess Core Competencies (ASC)"):
            st.session_state.show_competencies = True

        # Skills display component
        render_skills_display()

        # Career matches component (if available)
        if st.session_state.get("career_matches"):
            render_career_matches()

        # Quick prompt suggestions
        render_prompt_suggestions()


def render_api_key_input():
    """Render the OpenAI API key input section in the sidebar."""
    with st.expander("API Key Settings", expanded=False):
        st.info("Your API key is needed to use the features. It's stored only in your session and never saved on our servers.")

        current_key = st.session_state.get("openai_api_key", "")
        mask_key = "•" * len(current_key) if current_key else ""

        if current_key:
            st.success(f"API Key set: {mask_key}")
            if st.button("Clear API Key"):
                st.session_state.openai_api_key = ""
                st.rerun()
        else:
            api_key = st.text_input("Enter OpenAI API Key", type="password")
            if api_key:
                if api_key.startswith("sk-") and len(api_key) > 20:
                    st.session_state.openai_api_key = api_key
                    st.success("API Key saved to session!")
                    st.rerun()
                else:
                    st.error("Invalid API key format. Keys should start with 'sk-'")


def render_resume_upload(user):
    """Render the resume upload component."""
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])

    if uploaded_file:
        file_hash = hash(uploaded_file.getvalue())
        previous_hash = st.session_state.get("uploaded_resume_hash")

        # Parse only if new resume or hasn't been processed
        if file_hash != previous_hash:
            with st.spinner("Analyzing your resume..."):
                api_key = st.session_state.get("openai_api_key", "")
                parsed_resume = parse_resume(uploaded_file, api_key, supabase=supabase, user=user)

                st.session_state.uploaded_resume_hash = file_hash
                st.session_state.resume_text = parsed_resume.get("text", "")
                st.session_state.skills = parsed_resume.get("skills", [])

                if st.session_state.skills:
                    st.success(f"Found {len(st.session_state.skills)} skills in your resume!")
                    if len(st.session_state.messages) <= 2:
                        skill_list = st.session_state.skills[:5]
                        skill_message = f"Based on your resume, I can see you have skills in: {', '.join(skill_list)}"
                        if len(st.session_state.skills) > 5:
                            skill_message += f" and {len(st.session_state.skills) - 5} more."
                        full_message = f"{skill_message}\n\nWhat kind of career are you interested in exploring?"
                        st.session_state.messages.append({"role": "assistant", "content": full_message})
                else:
                    st.warning("No skills could be extracted from the resume. Try uploading a different file or check formatting.")

        else:
            st.info("Resume already processed. Showing previous results.")

        


def render_skills_display():
    """Render the skills display component."""
    st.subheader("Your Skills")

    if st.session_state.skills:
        skills_html = """
        <style>
            .skill-tag {
                background-color: #f1f1f1;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px 10px;
                margin: 5px;
                color: black;
            }
        </style>
        <div style='display: flex; flex-wrap: wrap;'>
        """
        for skill in st.session_state.skills:
            skills_html += f"<div class='skill-tag'>{skill}</div>"
        skills_html += "</div>"

        st.markdown(skills_html, unsafe_allow_html=True)

        # Toggle visualization popup
        if st.button("Visualize My Skills"):
            st.session_state.show_skills_popup = True
    else:
        st.info("No skills identified yet. Upload your resume or mention your skills in the chat.")


def render_career_matches():
    """Render the career matches component."""
    st.subheader("Career Matches")
    for i, match in enumerate(st.session_state.career_matches[:3]):
        with st.container():
            st.markdown(f"""
            <div class='career-card'>
                <h4>{match['title']}</h4>
                <p><strong>Match:</strong> {match['match_score']}%</p>
            </div>
            """, unsafe_allow_html=True)

    if len(st.session_state.career_matches) > 3:
        st.button("View All Matches", key="view_all_matches")


def render_prompt_suggestions():
    """Render prompt suggestions."""
    st.subheader("Try asking:")

    create_suggestion("What careers match my skills?")
    create_suggestion("What skills should I develop?")
    create_suggestion("What are the top tech careers?")

    if st.session_state.conversation_stage == "skills_collected":
        create_suggestion("What industry is growing fastest?")
    elif st.session_state.conversation_stage == "recommendations_provided":
        create_suggestion("What education do I need for this career?")


def create_suggestion(text):
    """Create prompt suggestion button."""
    if st.button(text, key=f"suggestion_{text}", help=f"Click to ask: {text}"):
        st.session_state.messages.append({"role": "user", "content": text})
        st.rerun()
