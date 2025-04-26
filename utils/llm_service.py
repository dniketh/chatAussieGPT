# utils/llm_service.py
import os
import streamlit as st
from utils.agents.agent_manager import AgentManager


def generate_response(supabase, user, user_query):
    """
    Generate a response using the agent system.
    """

    api_key = st.session_state.get("openai_api_key")

    if not api_key:
        return "Please provide an OpenAI API key in the sidebar to use advanced features."

    try:
        if "agent_manager" not in st.session_state:
            st.session_state.agent_manager = AgentManager(api_key=api_key, supabase=supabase, user=user)

        agent_manager = st.session_state.agent_manager

        if "triage_agent" not in st.session_state:
            triage_agent = agent_manager.initialize_agents()
            if not triage_agent:
                return "Failed to initialize the agent system. Please check your API key and try again."
            st.session_state.triage_agent = triage_agent

        return agent_manager.process_user_query(user_query)

    except Exception as e:
        error_msg = str(e)
        print(f"Error in generate_response: {error_msg}")
        return f"I encountered an issue processing your request: {error_msg}. Please try again or check your API key."