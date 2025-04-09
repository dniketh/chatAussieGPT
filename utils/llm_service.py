# utils/llm_service.py
import os
import streamlit as st
from utils.agents.agent_manager import AgentManager

# Global variable
agent_manager = None


def initialize_model():
    """Initialize the agent manager"""
    global agent_manager

    # Get API key from session state if available
    api_key = st.session_state.get("openai_api_key", None) or os.environ.get("OPENAI_API_KEY")

    # Create a new agent manager if none exists
    if agent_manager is None and api_key:
        agent_manager = AgentManager(api_key=api_key)
        agent_manager.initialize_agents()


def initialize_model_with_key(api_key):
    """Initialize the agent manager with the provided API key"""
    global agent_manager

    # Reset the agent manager to use the new key
    agent_manager = AgentManager(api_key=api_key)
    agent_manager.initialize_agents()


def generate_response(user_query, context=None, user_skills=None):
    """
    Generate a response using the agent system.

    Args:
        user_query: User's query string
        context: Unused parameter (kept for compatibility)
        user_skills: Unused parameter (kept for compatibility)

    Returns:
        str: Generated response text
    """
    global agent_manager

    # Check if we have an API key
    api_key = st.session_state.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Please provide an OpenAI API key in the sidebar to use advanced features."

    # Always initialize agent_manager if it's None - this ensures it's never None when we try to use it
    if agent_manager is None:
        agent_manager = AgentManager(api_key=api_key)
        agent_manager.initialize_agents()

    # Process the query through the agent system
    try:
        return agent_manager.process_user_query(user_query)
    except Exception as e:
        # Handle API errors gracefully
        error_msg = str(e)
        print(f"Error in generate_response: {error_msg}")  # Log the error
        return f"I encountered an issue processing your request. Please try again or check your API key."