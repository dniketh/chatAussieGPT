# utils/llm_service.py
import os
import streamlit as st
from utils.agents.agent_manager import AgentManager


def generate_response(user_query):
    """
    Generate a response using the agent system.

    Args:
        user_query: User's query string

    Returns:
        str: Generated response text
    """
    # Get API key from session state
    api_key = st.session_state.get("openai_api_key")

    # Check if API key is available
    if not api_key:
        return "Please provide an OpenAI API key in the sidebar to use advanced features."

    # Create agent manager with API key
    try:
        agent_manager = AgentManager(api_key=api_key)

        # Initialize the agents with the API key
        triage_agent = agent_manager.initialize_agents()

        # Check if agents were successfully initialized
        if not triage_agent:
            return "Failed to initialize the agent system. Please check your API key and try again."

        # Process the user query
        return agent_manager.process_user_query(user_query)
    except Exception as e:
        error_msg = str(e)
        print(f"Error in generate_response: {error_msg}")  # Log the error
        return f"I encountered an issue processing your request: {error_msg}. Please try again or check your API key."