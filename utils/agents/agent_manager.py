# utils/agents/agent_manager.py
import re

from openai import OpenAI
from agents import Agent, Runner, function_tool, FileSearchTool, WebSearchTool, RunContextWrapper,enable_verbose_stdout_logging

import streamlit as st
import json
import os
import asyncio
import concurrent.futures
from utils.supabase_data_utils import get_user_skills, get_user_competencies

enable_verbose_stdout_logging()


class AgentManager:
    def __init__(self, api_key=None, supabase = None, user =None):
        """Initialize the agent manager"""
        self.api_key = api_key

        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        self.client = None
        self.triage_agent = None
        self.agents = {}
        self.supabase_client =  supabase
        self.user = user




    def get_user_profile(self, context: RunContextWrapper) -> str:
        """Get user skills and competencies from the  database."""
        profile_text = "User Profile Data:\n"
        skills = []
        competencies = {}

        if not self.supabase_client or not self.user:
            return "Error: Unable to access user database context."

        try:
            skills = get_user_skills(self.supabase_client, self.user)
            competencies = get_user_competencies(self.supabase_client, self.user)

            profile_text += f"- Skills: {', '.join(skills) if skills else 'No skills found.'}\n"
            profile_text += "- Core Competencies:\n"
            if competencies:
                for comp, rating in competencies.items():
                    profile_text += f"  - {comp}: {rating}/5\n"
            else:
                profile_text += "  No competency ratings found.\n"

        except Exception as e:
            print(f"Error fetching profile data from Supabase: {e}")
            profile_text += "Error fetching profile data."

        return profile_text

    def _ensure_client(self):
        """Ensure the OpenAI client is initialized with the API key"""
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
        if not self._ensure_client():
            return None
        self.set_asc_vector_store()

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


        return Agent(
            name="ASC Career Recommendations",
            model="gpt-4o",
            instructions="""You are a specialized agent with expertise in the Australian Skills Classification (ASC) system.

Your purpose is to provide ONLY accurate and verified career recommendations based on users' skills and competencies. You must NEVER generate or recommend careers that are not explicitly found in the ASC knowledge base.

When using the FileSearchTool:
1. Search for detailed information about occupations from the ASC database
2. ONLY recommend occupations that you can directly cite from search results
3. If search returns no relevant results, explicitly state "I couldn't find matching occupations in the ASC knowledge base" rather than creating approximations
4. For each recommendation, include the exact ANZSCO code as shown in the source document
5. Directly quote or closely paraphrase ASC information - do not elaborate beyond what's in the source

When responding:
- Begin each job recommendation with "According to the ASC knowledge base..."
- Include ANZSCO codes with all career titles
- Explain specifically how user's skills match the documented career requirements
- Reference verifiable core competency information
- Maintain clear distinction between ASC information and general advice

IMPORTANT: Accuracy is more important than providing many options. It is far better to recommend fewer jobs with solid evidence than to suggest jobs not found in the ASC database. If you can't find appropriate matches in the ASC knowledge base, acknowledge this limitation directly.

When there are no jobs related to the user's query, clearly state that you could not find relevant occupations in the ASC knowledge base that match their skills or interests. NEVER invent or approximate job titles, ANZSCO codes, or requirements that aren't explicitly documented.
            """,
            tools=[
                function_tool(self.get_user_profile),
                FileSearchTool(vector_store_ids=[st.session_state.vector_store.id])
            ]

        )


    def _create_job_search_agent(self):
        return Agent(
            name="Job Search Assistant",
            model="gpt-4o",
            instructions="""
        You are a specialised agent for finding **real, current job opportunities** based on the user's skills and interests.

        ---

        ### Your responsibilities:

        - Use `get_user_profile` to understand the user's skills and preferred roles.
        - Search for **live, unexpired job listings** that match the user's skills.
        - NEVER fabricate job titles, companies, or summaries. Only include what you can find in the search results.
        - Only quote or summarise jobs actually found in the search results. Do not guess or assume the source platform.
        - If no relevant jobs are found, be honest about it. Finding no jobs is fine.
        - Always prefer jobs that are marked as “Open”, “Hiring now”, “Apply now”, or “Accepting applications”.
        - **Do not include** expired, closed, or archived job posts. Skip any that mention: “Closed”, “No longer advertised”, or “Expired”.

        ---

        ### Location Filtering:

        - If the user provides a location, only include jobs from that location.
        - If no location is mentioned, show jobs located **within Australia**.

        ---

        ### What to include for each job:

        - Job title  
        - Company name  
        - Location  
        - 1–2 sentence summary of key responsibilities or requirements  
        - Salary, if available
        - If available, a general link to apply or learn more (optional)

        ---

        ### Additional Guidance:

        - Provide practical advice for applying to the listed roles, if appropriate.
        - If asked, help the user prepare for interviews or suggest application tips tailored to specific companies.
        - Be honest about current job market conditions and transparent if no results are found.

        ---

        Your tone should be professional, supportive, and grounded in real opportunities.
        Use the web search tool to look for live job openings from reputable sources like Seek, LinkedIn, Indeed, and others.
        """,
        tools=[
            function_tool(self.get_user_profile),
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
               - Users want to know which careers match their competencies and skils
               - Queries are about career paths, requirements, or qualifications

            2. Job Search Assistant - Use this agent when:
               - Users want to find actual job listings
               - Questions are about current job market conditions
               - Users want to know which companies are hiring
               - Queries are about job application advice
               - Queries that seek advice on interview preparation for specific companies 

            For general questions, answer directly without using specialized agents.

            IMPORTANT: Before making recommendations, always check if you have access to the user's skills and competencies using the get user profile tool function. Additionally check the context i.e previous chat history before responding too
            If not, ask the user about their skills or suggest uploading a resume before providing specific recommendations.

            Maintain a conversational and helpful tone throughout the interaction.
            """,
            handoffs=specialized_agents,
            tools=[function_tool(self.get_user_profile)]

        )

    def set_asc_vector_store(self):
        """Setting ASC knowledge base"""
        print("In set_asc_vector_store ")

        if not self._ensure_client():
            return None

        vector_store = st.session_state.get("vector_store", None)

        try:
            if not vector_store:
                print("Checking vector stores... ")
                vector_stores = self.client.vector_stores.list()

                if vector_stores and vector_stores.data:
                    print("Vector Stores Present... ")
                    for vs in vector_stores.data:
                        if vs.name == 'ASC Knowledge Base V2':
                            print("ASC Occupation Knowledge Base Vector Found.")
                            vector_store = vs
                            st.session_state["vector_store"] = vector_store
                            break

                if not vector_store:
                    print("No existing ASC Occupation Knowledge Base vector store found. Creating new one...")
                    vector_store = self.client.vector_stores.create(name="ASC Knowledge Base V2")
                    st.session_state["vector_store"] = vector_store
                    print(f"Created vector store with ID: {vector_store.id}")

            vector_store = st.session_state["vector_store"]

            existing_files = self.client.vector_stores.files.list(vector_store_id=vector_store.id)
            print("Existing Files in Vector Store  - ", existing_files)


            if not existing_files or len(existing_files.data) <= 2:
                print("No files found or less than 3 files found in vector store. Uploading...")

                kb_text_path = 'data/files'
                os.makedirs(kb_text_path, exist_ok=True)

                if not os.path.exists(kb_text_path) or not any(
                        os.path.isfile(os.path.join(kb_text_path, f)) for f in os.listdir(kb_text_path)):
                    print("Converting JSON to text files...")
                    self._convert_json_to_text_kb("data/asc_knowledge_base.json")

                files_to_upload = []
                file_count = 0
                for filename in os.listdir(kb_text_path):
                    file_path = os.path.join(kb_text_path, filename)
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as file:
                            # Upload the file to the vector store
                            print(f"Uploading file: {filename} to Vector Store: {vector_store.name}")
                            file_batch = self.client.vector_stores.file_batches.upload_and_poll(
                                vector_store_id=vector_store.id,
                                files=[file]
                            )
                            file_count += 1
                            print(f"File upload completed: {filename}")
                            print(f"Total files uploaded: {file_count}")
                            print(file_batch.status)
                            print(file_batch.file_counts)

                print(f"Upload complete. Total files uploaded: {file_count}")


            else:
                print(f"Vector store already has more than {len(existing_files.data)} file(s). Skipping upload.")

        except Exception as e:
            print(f"Error creating/checking for vector store: {e}")
            st.error(f"Failed to create/check vector store: {str(e)}")
            return None






    @staticmethod
    def _convert_json_to_text_kb(json_path):
        """Convert JSON knowledge base to text format for each occupation and save it in data folder"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                kb_entries = data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return

        os.makedirs("data/files", exist_ok=True)
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

            safe_title = re.sub(r'[\\/:"*?<>|]+', '_', title)
            output_path = f"data/files/{safe_title}_{anzsco_code}.txt"
            if os.path.exists(output_path):
                print(f"Skipping file creation, file already exists: {output_path}")
                continue
            with open(output_path, 'w') as f:
                f.write(text_entry)


    def process_user_query(self, user_query):
        """
        Process user query through the agent system and return the response.

        Args:
            user_query: User's input text

        Returns:
            str: Generated response
        """
        os.environ["OPENAI_API_KEY"] = self.api_key
        chat_context = {"messages": st.session_state.messages}
        if not self.triage_agent:
            if not self.initialize_agents():
                return "I couldn't initialize the career guidance system. Please check your API key in the sidebar."

        if not self._ensure_client():
            return "Error: Unable to process your request. Please make sure you've entered a valid OpenAI API key in the sidebar."

        def run_async_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    Runner.run(
                        starting_agent=self.triage_agent,
                        input=user_query,
                        context= chat_context,
                    )
                )
                return result.final_output
            except Exception as e:
                error_msg = str(e)
                print(f"Error in thread: {error_msg}")
                if "insufficient_quota" in error_msg:
                    return "Sorry, I can't process your request right now. The API quota has been reached. Please update your API key in settings or try again later."
                return f"I encountered an issue while processing your request: {error_msg}"
            finally:
                loop.close()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_async_in_thread)
            return future.result()
