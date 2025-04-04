import streamlit as st
from utils.resume_parser import extract_text_from_resume, extract_skills_from_resume
from utils.visualizer import create_simple_skills_visualization


# app/sidebar_components.py (update render_sidebar function)

def render_sidebar(st):
    """
    Render the sidebar components in the provided container.

    Args:
        st: Streamlit container to render in
    """
    with st.container():
        st.subheader("Quick Actions")

        # Resume upload component
        render_resume_upload()

        # Add link to core competencies assessment
        if st.button("Assess Core Competencies (ASC)"):
            st.session_state.show_competencies = True

        # Skills display component
        render_skills_display()

        # Career matches component (if available)
        if st.session_state.career_matches:
            render_career_matches()

        # Quick prompt suggestions
        render_prompt_suggestions()

def render_resume_upload():
    """Render the resume upload component."""
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])

    if uploaded_file:
        with st.spinner("Analyzing your resume..."):
            # Extract text from resume
            resume_text = extract_text_from_resume(uploaded_file)

            # Extract skills from resume text
            resume_skills = extract_skills_from_resume(resume_text)

            # Update skills list
            new_skills_count = 0
            for skill in resume_skills:
                if skill not in st.session_state.skills:
                    st.session_state.skills.append(skill)
                    new_skills_count += 1

            # Confirm to user
            st.success(f"Found {len(resume_skills)} skills in your resume! ({new_skills_count} new)")

            # Add message to chat if conversation just started
            if len(st.session_state.messages) <= 2:
                skill_list = resume_skills[:5]
                skill_message = f"Based on your resume, I can see you have skills in: {', '.join(skill_list)}"
                if len(resume_skills) > 5:
                    skill_message += f" and {len(resume_skills) - 5} more."

                recommendation_message = "What kind of career are you interested in exploring?"

                full_message = f"{skill_message}\n\n{recommendation_message}"
                st.session_state.messages.append({"role": "assistant", "content": full_message})


def render_skills_display():
    """Render the skills display component."""
    st.subheader("Your Skills")

    if st.session_state.skills:
        # Create a layout for skills as tags
        skills_html = "<div style='display: flex; flex-wrap: wrap;'>"
        for skill in st.session_state.skills:
            skills_html += f"<div class='skill-tag'>{skill}</div>"
        skills_html += "</div>"

        st.markdown(skills_html, unsafe_allow_html=True)

        # Add a button to visualize skills
        if st.button("Visualize My Skills"):
            st.session_state.show_skills_map = not st.session_state.show_skills_map
    else:
        st.info("No skills identified yet. Upload your resume or mention your skills in the chat.")

    # Skills visualization (toggled by button)
    if st.session_state.show_skills_map and st.session_state.skills:
        st.subheader("Skills Map")
        # Generate a simple visual representation of skills
        viz_html = create_simple_skills_visualization(st.session_state.skills)
        st.components.v1.html(viz_html, height=400)


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
    """Render prompt suggestion buttons."""
    st.subheader("Try asking:")

    # Create suggestion buttons
    create_suggestion("What careers match my skills?")
    create_suggestion("What skills should I develop?")
    create_suggestion("What are the top tech careers?")

    # Conversation stage-specific suggestions
    if st.session_state.conversation_stage == "skills_collected":
        create_suggestion("What industry is growing fastest?")
    elif st.session_state.conversation_stage == "recommendations_provided":
        create_suggestion("What education do I need for this career?")



def create_suggestion(text):
    """
    Create a suggestion button that acts like user input.

    Args:
        text: The suggestion text
    """
    if st.button(text, key=f"suggestion_{text}", help=f"Click to ask: {text}"):
        # Add to messages and trigger rerun
        st.session_state.messages.append({"role": "user", "content": text})
        st.experimental_rerun()