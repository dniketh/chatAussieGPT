from utils.asc_data import get_asc_core_competencies
from utils.supabase_data_utils import save_user_competencies

def render_competencies_assessment(st, supabase, user):
    """
    Render the core competencies assessment interface.

    """
    with st.container():
        st.subheader("ASC Core Competencies")


        core_competencies = get_asc_core_competencies()

        # Display info
        st.info(
            "Rate your proficiency in these core competencies from the Australian Skills Classification (ASC) dataset.")

        if "core_competencies_ratings" not in st.session_state:
            st.session_state.core_competencies_ratings = {}


        for comp_name, comp_desc in core_competencies.items():
            current_rating = st.session_state.core_competencies_ratings.get(comp_name, 0)

            with st.expander(f"{comp_name}"):
                st.markdown(f"**{comp_name}**: {comp_desc}")

                rating = st.slider(
                    f"Rate your {comp_name}",
                    min_value=0,
                    max_value=10,
                    value=current_rating,
                    step=1,
                    help="0 = Not applicable, 1 = Beginner, 5= Intermediate , 10 = Expert",
                    key=f"slider_{comp_name}"
                )

                st.session_state.core_competencies_ratings[comp_name] = rating

        if st.button("Submit Core Competency Ratings"):
            status, count = save_user_competencies(supabase, user, st.session_state.core_competencies_ratings)

            if status == "updated":
                st.success(f"✅ {count} competencies updated.")
            elif status == "already_exists":
                st.info("ℹ️ All competencies already exist with the same ratings.")
            else:
                st.error("❌ Something went wrong while saving competencies.")