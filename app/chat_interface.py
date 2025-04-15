import streamlit as st
from utils.llm_service import generate_response


def render_chat_interface(supabase, user):
    """
    Render the chat interface in the provided container.

    Args:
        st: Streamlit container to render in
    """
    with st.container():
        st.subheader("Chat with our Assistant !")


        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])


    user_input = st.chat_input("Tell me about your skills or ask about career options...")

    if user_input:
        process_user_input(supabase, user, user_input)


def process_user_input(supabase, user, user_input):
    """
    Process user input from the chat interface.

    """

    st.session_state.messages.append({"role": "user", "content": user_input})


    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner(".."):

        response = generate_response(supabase, user, user_input)

        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)




