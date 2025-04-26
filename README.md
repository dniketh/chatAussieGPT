# chatAussieGPT - ASC-based Career Guidance System 

## Project Overview

chatAussieGPT is a  Agentic career guidance system that uses the Australian Skills Classification (ASC) dataset to help users with career planning and job seeking. The system:

- Helps students assess how well their skills and passions align with potential careers
- Supports job seekers in vertical and horizontal career growth
- Suggests ANZSCO job titles that match user competencies
- Provides data-driven career recommendations based on skills analysis

## Features

- **Skills Extraction**: Automatically extracts skills from user input and uploaded resumes
- **Core Competency Assessment**: Allows users to self-assess against ASC core competencies
- **Career Matching**: Provides career recommendations based on skills and competencies from the ASC taxonomy
- **Live Job Search**: Connects to web search to find current job openings that match user profiles
- **Interactive Chat Interface**: Offers a natural language interface for career guidance

## Architecture

The system uses an agent-based architecture with specialized components:

1. **Triage Agent**: Main interface that directs user queries to specialized agents
2. **ASC Retrieval Agent**: Specialized in the Australian Skills Classification system
3. **Job Search Agent**: Focuses on finding current job opportunities

## Installation

### Prerequisites

- Python 3.9 version is *IMPORTANT*
- OpenAI API key
- Supabase Project url and keys

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/dniketh/chatAussieGPT.git
   cd chatAussieGPT
   ```

2. Create and activate a virtual environment:
   ```
   python3.9 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit app:
   ```
   streamlit run main.py
   ```

2. Open your browser to the provided URL (eg http://localhost:8501)

3. Enter your OpenAI API key in the sidebar (required for advanced features)

4. You can:
   - Chat with the career guidance system
   - Upload your resume for skill extraction
   - Assess your core competencies
   - Get career recommendations
   - Search for job opportunities
  
## Docker Setup

### Build the Docker Image

1. Make sure you have Docker installed and running and clone the repo
2. Build the Docker image using the following command:
   ```
   docker build -t chat-aussie-gpt-docker .
   
   ```
### Run the Docker Container

1. After building the image, run the container with:
   ```
   docker run -p 8501:8501 chat-aussie-gpt-docker
   ```
2. Once the container is running, open your browser and go to: http://localhost:8501
   


## Project Structure

```
├── main.py                     # Entry point for the Streamlit app
├── data/                       # Data files
│   └── asc_knowledge_base.json # ASC dataset knowledge base
├── utils/
|   |---__init__.py                   # Utility modules
│   ├── agents/
|   |   |-- __init__py                 # Agent system
│   │   └── agent_manager.py    # Manages agent interactions
│   ├── asc_data.py             # ASC dataset utilities
│   |
│   ├── llm_service.py          # File to call AgentManager.py
│   ├── resume_parser.py        # Resume parsing utilities
│   |
│   └── visualizer.py           # Visualization utilities
└── app/                        # App interface components
    ├── app_structure.py        # Page layout
    ├── chat_interface.py       # Chat UI
    ├── competencies_component.py # Competency assessment UI
    └── sidebar_components.py   # Sidebar UI elements
```

## Development Notes

- The ASC knowledge base is stored as a json file which will be converted to text files for each occupation and uploaded to OpenAI for vector search
- Skills extraction currently uses pattern matching and NER, with plans to implement advanced NLP models
- Visualizations use simplified SVG format with plans to implement more advanced data visualization libraries

## API Key Management

- API keys are stored only in the session state and never saved to disk
- You can provide an API key through the UI side bar component

## Important Implementation Details

1. Register by creating an account and confirm your email
2. Login with your username and password
3. Add your openAI API Key in the sidebar
3. The core agent system is fully functional with real OpenAI integration

## Future Enhancements

- Integration with job posting APIs
- Enhanced skills visualization
- More detailed career path planning
- Resume improvement suggestions
- Integration with education and training resources

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

