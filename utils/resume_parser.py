import PyPDF2
import docx2txt
import re
import streamlit as st
import openai
from openai import OpenAI
import ast

# ------------------------ MAIN PARSER ------------------------

def parse_resume(uploaded_file, api_key=None):
    """
    Parse resume file and store extracted skills in session state.
    """
    resume_text = extract_text_from_resume(uploaded_file)

    # Step 1: Use agent to extract skills from the resume
    skills = extract_skills_from_resume(resume_text, api_key)

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

# ------------------------ SKILL PARSER USING AGENT ------------------------

def extract_skills_from_resume(resume_text, api_key):
    """
    Use GPT-based agent to extract skills from the resume text.
    """
    return extract_skills_with_agent(resume_text, api_key)

def extract_skills_with_agent(resume_text, api_key):
    """
    Use OpenAI to extract skills (both technical and soft skills) from resume text.
    """
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a resume parsing assistant.

Only extract skills that are explicitly mentioned in the resume **under headings such as 'Skills', 'Technical Skills', 'Key Skills', or similar skill sections**.

DO NOT extract skills or terms mentioned in the job descriptions, projects, or experience sections — only include what is listed under the designated skills section.

Only include:
- Programming languages (e.g., Python, SQL)
- Tools and software (e.g., Tableau, Power BI, Excel, Git)
- Platforms or frameworks (e.g., TensorFlow, AWS)
- Soft skills (e.g., communication, leadership) **only if listed in the skills section**

❌ Exclude:
- Algorithms (e.g., random forest, logistic regression)
- Evaluation metrics (e.g., accuracy, F1-score)
- Methods (e.g., hyperparameter tuning, EDA)
- Anything not listed in the skills/key skills section

Return the result as a valid **Python list of lowercase strings** like:
["python", "sql", "tableau", "power bi", "communication"]

Here is the resume text:
\"\"\"
{resume_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful resume parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()

        # Safely parse output as list
        try:
            skills = ast.literal_eval(content)
        except:
            skills = [s.strip().lower() for s in content.split(",")]

        return [s for s in skills if isinstance(s, str) and s]
    except Exception as e:
        st.warning(f"Agent skill extraction failed: {str(e)}")
        return []

# ------------------------ TEXT CLEANING ------------------------

def clean_text(text):
    """
    Clean and preprocess resume text (removing unnecessary spaces, newlines, etc.).
    """
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ')
    return text.strip()
