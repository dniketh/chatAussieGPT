import PyPDF2
import docx2txt
import re
import streamlit as st
from gpt4all import GPT4All
from pathlib import Path

# ------------------------ MODEL INITIALIZATION ------------------------
@st.cache_resource
def load_local_llm():
    model_dir = Path.home() / "Library/Application Support/nomic.ai/GPT4All"
    model_filename = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
    model_path = model_dir / model_filename

    assert model_path.is_file(), f"Model file not found at {model_path}"

    return GPT4All(model_name=model_filename, model_path=str(model_dir), allow_download=False)

llm = load_local_llm()

# ------------------------ MAIN PARSER ------------------------

def parse_resume(uploaded_file):
    resume_text = extract_text_from_resume(uploaded_file)
    skills = extract_skills_from_resume(resume_text)

    if "resume_skills" not in st.session_state:
        st.session_state.resume_skills = []

    for skill in skills:
        if skill not in st.session_state.resume_skills:
            st.session_state.resume_skills.append(skill)

    st.session_state.resume_text = resume_text

    return {
        "skills": skills,
        "text": resume_text
    }

# ------------------------ FILE HANDLING ------------------------

def extract_text_from_resume(uploaded_file):
    text = ""
    try:
        file_type = uploaded_file.type

        if "pdf" in file_type:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif "docx" in file_type or "doc" in file_type:
            text = docx2txt.process(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        text = clean_text(text)

    except Exception as e:
        st.error(f"Error extracting text from resume: {str(e)}")

    return text

# ------------------------ SKILL PARSER USING LOCAL LLM ------------------------

def extract_skills_from_resume(resume_text):
    prompt = f"""
You are a resume parsing assistant.

Extract all skills that are **explicitly listed** under skill-related sections such as:
- "Skills"
- "Technical Skills"
- "Key Skills"
- "Core Competencies"
- "Technologies"
- "Tools & Frameworks"
- "Cloud & Data Analytics"

✅ Only extract skills from the above sections — ignore job descriptions, project work, experience, education, and general text.

✅ Do NOT make up, rewrite, or add extra words. Return the exact terms mentioned, just in lowercase.

If no valid skill-related section is found in the resume, return an empty list: []

Include only:
- Programming languages (e.g., Python, SQL, C, Java)
- Tools and software (e.g., Tableau, Power BI, Excel, Git)
- Libraries or frameworks (e.g., TensorFlow, Scikit-learn, PyTorch, LangChain)
- Cloud platforms or technologies (e.g., AWS, GCP, Azure)
- Soft skills **only if clearly listed under the skills section**

Return the result as a valid **Python list of lowercase strings** like:
["python", "sql", "power bi", "git"]

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""


    
    try:
        with llm.chat_session():
            output = llm.generate(prompt, max_tokens=300)
            print("🔎 RAW OUTPUT:\n", output)
        return parse_skill_list(output)
    except Exception as e:
        st.warning(f"Local model skill extraction failed: {str(e)}")
        return []

# ------------------------ SKILL LIST PARSER ------------------------

def parse_skill_list(text):
    try:
        # Try evaluating the list safely
        parsed = eval(text.strip(), {"__builtins__": None}, {})
        if isinstance(parsed, list):
            return [skill.lower().strip() for skill in parsed if isinstance(skill, str)]
    except:
        pass

    # Fallback regex parsing
    match = re.search(r'\[(.*?)\]', text, re.DOTALL)
    if match:
        items = re.findall(r'["\'](.*?)["\']', match.group(1))
        return list(set(item.lower().strip() for item in items))
    
    return []


# ------------------------ TEXT CLEANING ------------------------

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ')
    return text.strip()
