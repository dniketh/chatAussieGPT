import PyPDF2
import docx2txt
import re
import streamlit as st
import spacy
from openai import OpenAI
import ast
from utils.supabase_data_utils import save_user_skills_to_supabase


@st.cache_resource
def load_spacy_model():
    return spacy.load("en_core_web_sm")

nlp = load_spacy_model()


def parse_resume(uploaded_file, api_key=None, supabase=None, user=None):
    resume_text = extract_text_from_resume(uploaded_file)

    masked_text = mask_pii_spacy_au(resume_text)
    st.markdown("### 🔍 Masked Resume Text:")
    st.code(masked_text)

    skills = extract_skills_from_resume(masked_text, api_key)

    if "resume_skills" not in st.session_state:
        st.session_state.resume_skills = []

    for skill in skills:
        if skill not in st.session_state.resume_skills:
            st.session_state.resume_skills.append(skill)

    status, num_saved = save_user_skills_to_supabase(supabase, user, st.session_state.resume_skills)

    if status == "saved":
        st.success(f"✅ {num_saved} new skills saved to your Database profile!")
    elif status == "already_exists":
        st.info("ℹ️ All extracted skills already exist in your profile.")
    else:
        st.error("❌ An error occurred while saving your skills.")

    st.session_state.resume_text = resume_text

    return {
        "skills": skills,
        "text": resume_text
    }


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
        return clean_text(text)
    except Exception as e:
        st.error(f"Error extracting text from resume: {str(e)}")
        return ""


def mask_pii_spacy_au(text):
    doc = nlp(text)
    masked_text = text

    # --------- EMAIL ---------
    masked_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', masked_text)

    # --------- PHONE (Australian Mobile & General) ---------
    masked_text = re.sub(r'(\+61[\s\-]?|0)?4\d{2}[\s\-]?\d{3}[\s\-]?\d{3}', '[PHONE]', masked_text)

    # --------- FULL ADDRESSES ---------
    masked_text = re.sub(
        r'\b\d+\s[\w\s]+,\s*[\w\s]+,\s*(NSW|VIC|QLD|SA|WA|TAS|ACT|NT)[\s\-]*\d{4}\b',
        '[ADDRESS]', masked_text, flags=re.IGNORECASE)

    # --------- PARTIAL ADDRESSES (street + suburb, no postcode) ---------
    masked_text = re.sub(
        r'\b\d+\s[\w\s]+,\s*[\w\s]+',
        '[ADDRESS]', masked_text, flags=re.IGNORECASE)

    # --------- CITY NAMES ---------
    cities = ['sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'hobart', 'canberra', 'darwin']
    for city in cities:
        masked_text = re.sub(rf'\b{city}\b', '[CITY]', masked_text, flags=re.IGNORECASE)

    # --------- STATE NAMES ---------
    states = ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'ACT', 'NT']
    for state in states:
        masked_text = re.sub(rf'\b{state}\b', '[STATE]', masked_text, flags=re.IGNORECASE)


    return masked_text


def extract_skills_from_resume(masked_text, api_key):
    return extract_skills_with_agent(masked_text, api_key)

def extract_skills_with_agent(resume_text, api_key):
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a resume parsing assistant.

Extract only technical skills listed under the "Technologies" section of the resume. Focus only on lines under headings like "Proficient", "Familiar", or similar. Do not infer any soft skills or personality traits unless explicitly listed under a skills heading.
Include only:
- Programming languages
- Tools and libraries
- Frameworks and platforms
- Cloud technologies

Ignore:
- Any skills not under 'Technologies', 'Skills', or 'Technical Skills' sections
- Descriptive phrases, soft skills, business terms, or general qualities
- Any duplicate or redundant terms
- Don't include anything from extra sections like "Experience", "Education", or "Projects"
Return the result as a **valid Python list of lowercase strings**.

Resume:
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

        try:
            skills = ast.literal_eval(content)
            if isinstance(skills, list):
                return [s.strip().lower() for s in skills if isinstance(s, str)]
            else:
                return []
        except:
            lowered = content.lower()
            if "no skills can be extracted" in lowered or "no valid skill section" in lowered:
                return []
            else:
                skills = [s.strip().lower() for s in re.findall(r"'(.*?)'", content)]
                return skills if skills else []

    except Exception as e:
        st.warning(f"Agent skill extraction failed: {str(e)}")
        return []



def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ')
    return text.strip()