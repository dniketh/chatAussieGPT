# utils/resume_parser.py
import PyPDF2
import docx2txt
import re
import streamlit as st



def parse_resume(uploaded_file):
    """
    Parse resume file and store extracted skills in session state
    #
    #     Args:
    #         uploaded_file: File uploaded through Streamlit
    #
    #     Returns:
    #         dict: Extracted information including skills
    #     """
    #     # Extract text from file
    resume_text = extract_text_from_resume(uploaded_file)

    # Extract skills
    skills = extract_skills_from_resume(resume_text)


    if "resume_skills" not in st.session_state:
        st.session_state.resume_skills = []

    # Add new skills without duplicates
    for skill in skills:
        if skill not in st.session_state.resume_skills:
            st.session_state.resume_skills.append(skill)

    # Store the resume text for potential future use
    st.session_state.resume_text = resume_text

    return {
        "skills": skills,
        "text": resume_text
    }


def extract_text_from_resume(uploaded_file):
    """Extract text from resume file"""
    text = ""

    try:
        file_type = uploaded_file.type

        if "pdf" in file_type:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text() + "\n"

        elif "docx" in file_type or "doc" in file_type:
            text = docx2txt.process(uploaded_file)

        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        text = clean_text(text)

    except Exception as e:
        st.error(f"Error extracting text from resume: {str(e)}")

    return text


def extract_skills_from_resume(resume_text):
    """Extract skills from resume text"""
    ## Need to extract skills from the resume text here.
    return None


def clean_text(text):
    """Clean extracted text"""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ')
    return text.strip()