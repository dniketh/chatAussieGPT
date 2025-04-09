# utils/agents/agent_manager.py
from openai import OpenAI
from agents import Agent, Runner, function_tool, FileSearchTool, WebSearchTool
import streamlit as st
import json
import os

class AgentManager:
    def __init__(self, api_key=None):
        """Initialize the agent manager"""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = None
        self.triage_agent = None
        self.agents = {}


    def _ensure_client(self):
        if not self.client and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

        if not self.client:
            st.error("OpenAI API key must be provided to use this functionality")

        return self.client


    def initialize_agents(self):
        """Initialize all agents in the system"""

        self._ensure_client()

        
        if self.triage_agent:
            return self.triage_agent

        # Initialize specialized agents
        self.agents["asc_retrieval"] = self._create_asc_retrieval_agent()
        self.agents["job_search"] = self._create_job_search_agent()

        # Create triage agent with access to specialized agents
        self.triage_agent = self._create_triage_agent([
            self.agents["asc_retrieval"],
            self.agents["job_search"]
        ])

        return self.triage_agent

    def _create_asc_retrieval_agent(self):
        """Create agent for ASC knowledge retrieval"""
        # Get retrieval tool for ASC knowledge base
        retrieval_tool = self._get_asc_retrieval_tool()

        # Create agent with retrieval tool
        return Agent(
            name="ASC Career Recommendations",
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
        """Create agent for searching live job listings"""
        return Agent(
            name="Job Search Assistant",
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
            name="Career Guide",
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
            
            IMPORTANT: Before making recommendations, always check if you have access to the user's skills and competencies.
            If not, ask the user about their skills or suggest uploading a resume before providing specific recommendations.
            
            Maintain a conversational and helpful tone throughout the interaction.
            """,
            handoffs=specialized_agents,
            tools=[self._get_user_profile_tool]
        )

    def _get_asc_retrieval_tool(self):
        """Get retrieval tool for ASC knowledge base"""
        # Check if file ID exists in session state
        self._ensure_client()
        file_id = st.session_state.get("kb_file_id")

        if not file_id:
            # Convert knowledge base if needed
            kb_text_path = "data/asc_knowledge_base.txt"
            if not os.path.exists(kb_text_path):
                self._convert_json_to_text_kb("data/asc_knowledge_base.json", kb_text_path)

            # Upload to OpenAI
            with open(kb_text_path, "rb") as file:
                response = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
                file_id = response.id
                st.session_state["kb_file_id"] = file_id

        # Create retrieval tool with file ID
        return FileSearchTool(max_num_results=5,include_search_results=True, vector_store_ids=[file_id])

    @function_tool()
    def _get_user_profile_tool(self):
        """Get user skills and competencies from session state"""
        profile = {
            "skills": [],
            "resume_skills": [],
            "competencies": {}
        }

        # Get skills from conversation
        if "skills" in st.session_state:
            profile["skills"] = st.session_state.skills

        # Get skills from resume
        if "resume_skills" in st.session_state:
            profile["resume_skills"] = st.session_state.resume_skills

        # Get core competencies
        if "core_competencies_ratings" in st.session_state:
            profile["competencies"] = st.session_state.core_competencies_ratings

        # Get all unique skills
        all_skills = set(profile["skills"]) | set(profile["resume_skills"]) | set(profile['competencies'])
        profile["all_skills"] = list(all_skills)

        return profile

    def _convert_json_to_text_kb(self, json_path, output_path):
        """Convert JSON knowledge base to text format"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    kb_entries = [data]
                else:
                    kb_entries = data
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return

        # Convert entries to text format
        text_entries = []
        for entry in kb_entries:
            metadata = entry.get("metadata", {})
            anzsco_code = metadata.get("anzsco_code", "Unknown")
            title = metadata.get("title", "Unknown Title")
            description = metadata.get("description", "")

            competencies = metadata.get("core_competencies", [])
            comp_text = []
            for comp in competencies:
                name = comp.get("name", "")
                level = comp.get("level", "")
                score = comp.get("score", "")
                if name and (level or score):
                    comp_text.append(f"{name}: {level} (score: {score})")

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

        # Combine and save
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
        # Initialize agents if needed
        if not self.triage_agent:
            self.initialize_agents()

        try:
            # Run the query through the triage agent
            output = Runner.run_sync(
                starting_agent=self.triage_agent,
                input=user_query
            )

            return output.final_output
        except Exception as e:
            return f"I encountered an issue processing your request: {str(e)}"