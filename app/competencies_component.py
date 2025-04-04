import streamlit as st
from utils.asc_data import get_asc_core_competencies
from utils.career_matching import generate_career_matches_with_competencies

def render_competencies_assessment(st):
    """
    Render the core competencies assessment interface.

    Args:
        container: Streamlit container to render in
    """
    with st.container():
        st.subheader("ASC Core Competencies")


        core_competencies = get_asc_core_competencies()

        # Display info
        st.info(
            "Rate your proficiency in these core competencies from the Australian Skills Classification (ASC) dataset.")

        # Initialize competencies ratings in session state if not present
        if "core_competencies_ratings" not in st.session_state:
            st.session_state.core_competencies_ratings = {}


        for comp_name, comp_desc in core_competencies.items():
            # Get current rating from session state or default to 0
            current_rating = st.session_state.core_competencies_ratings.get(comp_name, 0)

            # Create expander for competency details
            with st.expander(f"{comp_name}"):
                st.markdown(f"**{comp_name}**: {comp_desc}")

                # Add slider for rating
                rating = st.slider(
                    f"Rate your {comp_name}",
                    min_value=0,
                    max_value=5,
                    value=current_rating,
                    step=1,
                    help="0 = Not applicable, 1 = Beginner, 5 = Expert",
                    key=f"slider_{comp_name}"
                )

                # Save rating to session state
                st.session_state.core_competencies_ratings[comp_name] = rating

        # Button to submit ratings
        if st.button("Submit Core Competency Ratings"):
            st.success("Core competency ratings saved! These will be considered in your career recommendations.")

            # Now you can use the competencies in career matching
            update_career_recommendations()


def update_career_recommendations():
    """Update career recommendations based on skills and competencies."""
    # If no skills defined yet, use empty list
    skills = st.session_state.get("skills", [])

    # Get competencies with non-zero ratings
    competencies = {
        name: rating for name, rating in st.session_state.get("core_competencies_ratings", {}).items()
        if rating > 0
    }
    # Update career matches in session state
    st.session_state.career_matches = generate_career_matches_with_competencies(skills, competencies)