# utils/agents/agent_manager.py
from openai import OpenAI
from agents import Agent, Runner, function_tool, FileSearchTool, WebSearchTool
import streamlit as st
import json
import os
import asyncio




class AgentManager:
    def __init__(self, api_key=None):
        """Initialize the agent manager"""
        self.api_key = api_key
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        self.client = None
        self.triage_agent = None
        self.agents = {}

    def _ensure_client(self):
        """Ensure the OpenAI client is initialized with the API key"""
        # Check if we have a valid API key
        if not self.api_key:
            st.error("OpenAI API key must be provided to use this functionality")
            return None


        if not self.client:
            try:

                os.environ["OPENAI_API_KEY"] = self.api_key
                self.client = OpenAI(api_key=self.api_key)
                print(f"OpenAI client initialized successfully with API key starting with: {self.api_key[:5]}...")
            except Exception as e:
                st.error(f"Failed to initialize OpenAI client: {str(e)}")
                return None

        return self.client

    def initialize_agents(self):
        """Initialize all agents in the system"""
        # Ensure client is initialized before creating agents
        if not self._ensure_client():
            return None

        if self.triage_agent:
            return self.triage_agent


        try:
            self.agents["asc_retrieval"] = self._create_asc_retrieval_agent()
            self.agents["job_search"] = self._create_job_search_agent()

            self.triage_agent = self._create_triage_agent([
                self.agents["asc_retrieval"],
                self.agents["job_search"]
            ])

            print("All agents initialized successfully")
            return self.triage_agent
        except Exception as e:
            error_msg = f"Error initializing agents: {str(e)}"
            print(error_msg)
            st.error(error_msg)
            return None

    def _create_asc_retrieval_agent(self):
        """Create agent for ASC knowledge retrieval"""
        retrieval_tool = self._get_asc_retrieval_tool()

        return Agent(
            name="ASC Career Recommendations",
            model="gpt-4o",
            instructions="""
            You are a specialized agent with expertise in the Australian Skills Classification (ASC) system.

            Your purpose is to provide accurate career recommendations based on users' skills and competencies.

            When responding:
            - Always include ANZSCO codes with career titles
            - Explain how skills match specific career requirements
            - Reference core competency ratings when available
            - Provide specific information from the ASC knowledge base
            - Suggest skills to develop for career advancement

            Use the retrieval tool to access detailed information about occupations, required skills, 
            competency levels, and specialized tasks from the ASC database.

            Be precise, informative, and helpful in your recommendations.
            """,
            tools=[
                self._get_user_profile_tool,
                retrieval_tool
            ]
      

        )

    def _create_job_search_agent(self):
        return Agent(
            name="Job Search Assistant",
            model="gpt-4o",
            instructions="""
            You are a specialized agent for finding current job opportunities.

            Your purpose is to search for and provide information about actual job openings that match 
            the user's skills and interests.

            When responding:
            - Search for current job listings relevant to the user's skills
            - Provide specific job titles, companies, and key requirements
            - Focus on jobs that match the user's skill profile
            - Offer practical advice about job application strategies
            - Be honest about the current job market conditions

            Use web search to find current job opportunities and market information.

            Be practical, specific, and helpful in your recommendations.
            """,
            tools=[
                self._get_user_profile_tool,
                WebSearchTool()
            ]


        )

    def _create_triage_agent(self, specialized_agents):
        """Create the main triage agent"""
        return Agent(
            name="Career Guide for ASC",
            model="gpt-4o",
            instructions="""
            You are a career guidance assistant that helps users explore career paths in Australian Skill Classification System based on their skills and interests.

            You have access to these specialized agents:

            1. ASC Career Recommendations - Use this agent when:
               - Users want career recommendations based on their skills
               - Questions relate to the Australian Skills Classification system
               - Users want to know which careers match their competencies
               - Queries are about career paths, requirements, or qualifications

            2. Job Search Assistant - Use this agent when:
               - Users want to find actual job listings
               - Questions are about current job market conditions
               - Users want to know which companies are hiring
               - Queries are about job application advice

            For general questions, answer directly without using specialized agents.

            IMPORTANT: Before making recommendations, always check if you have access to the user's skills and competencies using the get user profile tool function.
            If not, ask the user about their skills or suggest uploading a resume before providing specific recommendations.

            Maintain a conversational and helpful tone throughout the interaction.
            """,
            handoffs=specialized_agents,
            tools=[self._get_user_profile_tool]
           

        )

    def _get_asc_retrieval_tool(self):
        """Get retrieval tool for ASC knowledge base"""
        if not self._ensure_client():
            return None

        file_id = st.session_state.get("kb_file_id")

        if not file_id:
            kb_text_path = "data/asc_knowledge_base.txt"
            if not os.path.exists(kb_text_path):
                self._convert_json_to_text_kb("data/asc_knowledge_base.json", kb_text_path)

            with open(kb_text_path, "rb") as file:
                response = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
                file_id = response.id
                st.session_state["kb_file_id"] = file_id

        return FileSearchTool(max_num_results=5, include_search_results=True, vector_store_ids=[file_id])

    @function_tool(
        name_override="_get_user_profile_tool",
        description_override="Get user skills and competencies from session state.",
        docstring_style="google"
    )

    def _get_user_profile_tool(self) -> str:
         """Get user skills and competencies from session state."""
         skills = st.session_state.get("skills", [])
         resume_skills = st.session_state.get("resume_skills", [])
         competencies = st.session_state.get("core_competencies_ratings", {})

         # Format as a human-readable string
         profile_text = "User Profile:\n"
         profile_text += f"- Skills: {', '.join(skills)}\n"
         profile_text += f"- Resume Skills: {', '.join(resume_skills)}\n"
         profile_text += "- Core Competencies:\n"
         for comp, rating in competencies.items():
             profile_text += f"  - {comp}: {rating}/5\n"
         return profile_text





    @staticmethod
    def _convert_json_to_text_kb(json_path, output_path):
        """Convert JSON knowledge base to text format"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                kb_entries = data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return

        text_entries = []
        for entry in kb_entries:
            metadata = entry.get("metadata", {})
            anzsco_code = metadata.get("anzsco_code", "Unknown")
            title = metadata.get("title", "Unknown Title")
            description = metadata.get("description", "")

            competencies = metadata.get("core_competencies", [])
            comp_text = [
                f"{comp.get('name', '')}: {comp.get('level', '')} (score: {comp.get('score', '')})"
                for comp in competencies if comp.get("name", "")
            ]

            tasks = metadata.get("specialist_tasks", [])
            tools = metadata.get("technology_tools", [])

            text_entry = f"""
# {title} (ANZSCO: {anzsco_code})

## Description
{description}

## Required Core Competencies
{', '.join(comp_text)}

## Specialized Tasks
{', '.join(tasks)}

## Technology Tools
{', '.join(tools)}
"""
            text_entries.append(text_entry)

        combined_text = "\n\n---\n\n".join(text_entries)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(combined_text)

    def process_user_query(self, user_query):
        """
        Process user query through the agent system

        Args:
            user_query: User's input text

        Returns:
            str: Generated response
        """
        # Always re-check environment variable before processing
        os.environ["OPENAI_API_KEY"] = self.api_key

        if not self.triage_agent:
            if not self.initialize_agents():
                return "I couldn't initialize the career guidance system. Please check your API key in the sidebar."

        # Double-check the client is initialized
        if not self._ensure_client():
            return "Error: Unable to process your request. Please make sure you've entered a valid OpenAI API key in the sidebar."

        try:
            # Create a new Runner with the API key
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Try to run with explicit API key
            output = loop.run_until_complete(
                Runner.run_sync(
                    starting_agent=self.triage_agent,
                    input=user_query

                )
            )
            return output.final_output
        except Exception as e:
            error_msg = str(e)
            print(f"Error in process_user_query: {error_msg}")
            return f"I encountered an issue while processing your request: {error_msg}"