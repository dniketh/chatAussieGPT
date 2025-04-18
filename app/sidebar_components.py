import streamlit as st
from utils.resume_parser import extract_text_from_resume, extract_skills_from_resume
from utils.visualizer import create_simple_skills_visualization


def render_sidebar(supabase, user_id):
    """
    Render the sidebar components in the provided container.


    """
    with st.container():
        st.subheader("Quick Actions")

        # API key input section
        render_api_key_input()

        # Resume upload component
        render_resume_upload(supabase,user_id)

        # Add link to core competencies assessment
        if st.button("Assess Core Competencies (ASC)"):
            st.session_state.show_competencies = True

        # Skills display component
        render_skills_display()



def render_api_key_input():
    """Render the OpenAI API key input section in the sidebar."""
    with st.expander("API Key Settings", expanded=False):
        st.info(
            "Your API key is needed to use the features. It's stored only in your session and never saved on our servers.")

        # Get current key from session state
        current_key = st.session_state.get("openai_api_key", "")
        mask_key = "•" * len(current_key) if current_key else ""

        # Show masked key if exists
        if current_key:
            st.success(f"API Key set: {mask_key}")

            # Add button to clear key
            if st.button("Clear API Key"):
                st.session_state.openai_api_key = ""
                st.rerun()
        else:
            # Show input field for key
            api_key = st.text_input("Enter OpenAI API Key", type="password")

            if api_key:
                # Validate key format (simple check)
                if api_key.startswith("sk-") and len(api_key) > 20:
                    st.session_state.openai_api_key = api_key
                    st.success("API Key saved to session!")
                    st.rerun()
                else:
                    st.error("Invalid API key format. Keys should start with 'sk-'")

def render_resume_upload(supabase, user_id):
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

"""

def render_prompt_suggestions():
    
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

"""
###Future Implementation
"""
def create_suggestion(text):
   
    if st.button(text, key=f"suggestion_{text}", help=f"Click to ask: {text}"):
        # Add to messages and trigger rerun
        st.session_state.messages.append({"role": "user", "content": text})
        st.experimental_rerun()
    
"""