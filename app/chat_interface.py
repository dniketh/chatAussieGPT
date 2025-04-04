import streamlit as st
from utils.llm_service import generate_response
from utils.skills_extractor import extract_skills_from_text


def render_chat_interface(st):
    """
    Render the chat interface in the provided container.

    Args:
        st: Streamlit container to render in
    """
    with st.container():
        st.subheader("Chat with your Career Guide")

        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat input
    user_input = st.chat_input("Tell me about your skills or ask about career options...")

    if user_input:
        process_user_input(user_input)


def process_user_input(user_input):
    """
    Process user input from the chat interface.

    """
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Checking..."):
        # Extract any skills mentioned in the message (just to maintain the skills list)
        extracted_skills = extract_skills_from_text(user_input)
        if "skills" not in st.session_state:
            st.session_state.skills = []
        if extracted_skills:
            for skill in extracted_skills:
                if skill not in st.session_state.skills:
                    st.session_state.skills.append(skill)

        # Simply pass the user query and let the LLM handle it
        response = generate_response(user_input)

        # Add response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display response
        with st.chat_message("assistant"):
            st.markdown(response)

        # Update conversation stage based on content
        update_conversation_stage(user_input)


def update_conversation_stage(user_input):
    """
    Update the conversation stage based on current state and user input.

    Args:
        user_input: The user's latest input
    """
    if st.session_state.conversation_stage == "initial" and len(st.session_state.skills) >= 3:
        st.session_state.conversation_stage = "skills_collected"
    elif "career_matches" in st.session_state and st.session_state.career_matches:
        st.session_state.conversation_stage = "recommendations_provided"