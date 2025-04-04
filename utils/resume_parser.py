import io
import re
import PyPDF2
import docx2txt
import streamlit as st


def extract_text_from_resume(uploaded_file):
    """
    Extract text from a resume file (PDF or DOCX).

    Args:
        uploaded_file: The file uploaded through Streamlit's file_uploader

    Returns:
        str: Extracted text from the resume
    """
    text = ""

    try:
        # Check file type and extract text accordingly
        file_type = uploaded_file.type

        if "pdf" in file_type:
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text() + "\n"

        elif "docx" in file_type or "doc" in file_type:
            # Extract text from DOCX
            text = docx2txt.process(io.BytesIO(uploaded_file.getvalue()))

        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Clean the extracted text
        text = clean_text(text)

    except Exception as e:
        st.error(f"Error extracting text from resume: {str(e)}")
        return ""

    return text


def clean_text(text):
    """
    Clean the extracted text by removing extra whitespace, special characters, etc.

    Args:
        text: Raw text extracted from resume

    Returns:
        str: Cleaned text
    """
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)

    # Replace non-breaking spaces and other special whitespace
    text = text.replace('\xa0', ' ')

    return text.strip()


def extract_skills_from_resume(resume_text):
    """
    Extract skills from resume text.
    In a real implementation, this would use NLP or a skills taxonomy.

    Args:
        resume_text: Text extracted from resume

    Returns:
        list: List of identified skills
    """
    # This is a simplified implementation
    # In a real system, you would use NLP models trained on the ASC dataset

    # Common skills to look for
    common_skills = [
        # Technical skills
        "Python", "JavaScript", "Java", "C++", "C#", "SQL", "AWS", "Azure",
        "Docker", "Kubernetes", "React", "Angular", "Vue", "Node.js", "Django",
        "Flask", "Machine Learning", "Data Analysis", "Excel", "PowerBI", "Tableau",

        # Soft skills
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management", "Project Management",

        # Business skills
        "Marketing", "Sales", "Business Development", "Strategy", "Finance",
        "Accounting", "Human Resources", "Customer Service"
    ]

    # Extract skills by direct matching
    # In a real implementation, you would use a more sophisticated approach
    found_skills = []

    for skill in common_skills:
        # Use word boundary to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, resume_text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills