
import streamlit as st
from utils.resume_parser import parse_resume
from utils.visualizer import create_svg_skills_visualization, categorize_skills
from utils.supabase_data_utils import fetch_saved_competencies


def render_sidebar(supabase, user):
    user_id = user.id
    

    with st.container():
        st.subheader("Quick Actions")

        render_api_key_input()
        render_resume_upload(supabase, user)

        if st.button("Assess Core Competencies (ASC)"):
            st.session_state.show_competencies = True

        render_skills_display(supabase, user_id)
        render_user_competencies(supabase, user_id)

        if st.session_state.get("career_matches"):
            render_career_matches()


        agent_manager = st.session_state.get("agent_manager")
        if agent_manager:
            render_prompt_suggestions(agent_manager)
        else:
            st.sidebar.info("Prompt suggestions will appear after your first query.")


def render_api_key_input():
    with st.expander("API Key Settings", expanded=False):
        st.info("Your API key is stored only in this session.")
        current_key = st.session_state.get("openai_api_key", "")
        if current_key:
            st.success(f"API Key set: {'•' * len(current_key)}")
            if st.button("Clear API Key"):
                st.session_state.openai_api_key = ""
                st.rerun()
        else:
            key = st.text_input("Enter OpenAI API Key", type="password")
            if key and key.startswith("sk-") and len(key) > 20:
                st.session_state.openai_api_key = key
                st.success("API Key saved!")
                st.rerun()
            elif key:
                st.error("Invalid API key format.")


def render_resume_upload(supabase, user):
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    if uploaded_file:
        file_hash = hash(uploaded_file.getvalue())
        if file_hash != st.session_state.get("uploaded_resume_hash"):
            with st.spinner("Analyzing resume..."):
                api_key = st.session_state.get("openai_api_key", "")
                parsed = parse_resume(uploaded_file, api_key, supabase, user)
                st.session_state.uploaded_resume_hash = file_hash
                st.session_state.resume_text = parsed.get("text", "")
                st.session_state.skills = parsed.get("skills", [])

                if st.session_state.skills:
                    st.success(f"Found {len(st.session_state.skills)} skills!")
                    if len(st.session_state.messages) <= 2:
                        short_list = st.session_state.skills[:5]
                        msg = f"Based on your resume, you have skills in: {', '.join(short_list)}"
                        msg += "\n\nWhat kind of career are you interested in exploring?"
                        st.session_state.messages.append({"role": "assistant", "content": msg})
                else:
                    st.warning("No skills found. Try a different file.")
        else:
            st.info("Resume already processed.")


def render_skills_display(supabase, user_id):
    st.subheader("Your Skills")



    if st.session_state.get("skills"):
        skill_html = "<div style='display: flex; flex-wrap: wrap;'>"
        for skill in st.session_state.skills:
            skill_html += f"<div class='skill-tag'>{skill}</div>"
        skill_html += "</div>"

        st.markdown("""
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
        """, unsafe_allow_html=True)
        st.markdown(skill_html, unsafe_allow_html=True)

        if st.button("Visualize My Skills"):
            st.session_state.show_skills_popup = True
            competencies = fetch_saved_competencies(supabase, user_id)
            technical_skills = st.session_state.get("resume_skills", [])

            categorized = categorize_skills(supabase, user_id)
            svg = create_svg_skills_visualization(categorized)



def render_career_matches():
    st.subheader("Career Matches")
    for match in st.session_state.career_matches[:3]:
        st.markdown(f"**{match['title']}** — {match['match_score']}% match")


def render_prompt_suggestions(agent_manager):
    st.subheader("Try asking:")
    for prompt in [
        "What careers match my skills?",
        "What skills should I develop?",
        "What are the top tech careers?"
    ]:
        if st.button(prompt):
            st.session_state.messages.append({"role": "user", "content": prompt})

            response = agent_manager.process_user_query(prompt)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()



def render_user_competencies(supabase, user_id):
    st.subheader("🔍 Core Competencies")
    competencies = fetch_saved_competencies(supabase, user_id)

    if competencies:
        for comp in competencies:
            name = comp.get("competency_name")
            rating = comp.get("rating", 0)
            st.write(f"**{name}**: {rating}/10")
            st.progress(rating / 10.0)
    else:
        st.info("No core competencies found. Click 'Assess Core Competencies (ASC)' to get started.")
