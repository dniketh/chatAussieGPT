import re


def extract_skills_from_text(text):
    """
    Extract skills from text using pattern matching.
    In a real implementation, this would use NLP techniques.

    Args:
        text: Text to extract skills from

    Returns:
        list: List of extracted skills
    """
    # This is a simplified implementation
    # In a real system, you would use NLP models trained on the ASC dataset

    # Define common skills to look for
    common_skills = {
        # Technical skills
        "programming": [
            r"\b(Python|JavaScript|Java|C\+\+|C#|PHP|Ruby|Swift|TypeScript|Go|Kotlin|Rust)\b",
            "Programming Languages"
        ],
        "web_dev": [
            r"\b(HTML|CSS|React|Angular|Vue\.js|Node\.js|Django|Flask|Laravel|Express\.js)\b",
            "Web Development"
        ],
        "data": [
            r"\b(SQL|NoSQL|MongoDB|PostgreSQL|MySQL|Oracle|Database|Data Analysis|Data Science|Data Mining|Big Data)\b",
            "Data Technologies"
        ],
        "cloud": [
            r"\b(AWS|Amazon Web Services|Azure|Google Cloud|GCP|Cloud Computing|Docker|Kubernetes|DevOps|CI/CD)\b",
            "Cloud & DevOps"
        ],
        "ai_ml": [
            r"\b(Machine Learning|Deep Learning|AI|Artificial Intelligence|Neural Networks|TensorFlow|PyTorch|NLP|Computer Vision)\b",
            "AI & Machine Learning"
        ],

        # Soft skills
        "communication": [
            r"\b(Communication|Public Speaking|Presentation|Writing|Technical Writing|Documentation)\b",
            "Communication Skills"
        ],
        "leadership": [
            r"\b(Leadership|Management|Team Management|Project Management|Agile|Scrum|Kanban|JIRA)\b",
            "Leadership & Management"
        ],
        "problem_solving": [
            r"\b(Problem Solving|Critical Thinking|Analytical|Analysis|Troubleshooting|Debugging)\b",
            "Problem Solving"
        ],

        # Business skills
        "business": [
            r"\b(Marketing|Sales|Business Development|Strategy|Finance|Accounting|Human Resources|Customer Service)\b",
            "Business Skills"
        ]
    }

    # Extract skills using regex patterns
    extracted_skills = []

    for category, (pattern, skill_type) in common_skills.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            skill = match.group(0)
            if skill not in extracted_skills:
                extracted_skills.append(skill)

    return extracted_skills


def categorize_skill(skill):
    """
    Categorize a skill into a specific type.

    Args:
        skill: Skill name to categorize

    Returns:
        str: Category name
    """
    # Technical skills
    tech_skills = [
        "Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Swift",
        "SQL", "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js",
        "Django", "Flask", "AWS", "Azure", "Docker", "Kubernetes",
        "Machine Learning", "Data Analysis", "Data Science", "AI"
    ]

    # Soft skills
    soft_skills = [
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management", "Adaptability",
        "Collaboration", "Creativity", "Emotional Intelligence"
    ]

    # Business skills
    business_skills = [
        "Project Management", "Marketing", "Sales", "Business Development",
        "Strategy", "Finance", "Accounting", "Human Resources",
        "Customer Service", "Negotiation", "Business Analysis"
    ]

    # Check which category the skill belongs to
    if skill in tech_skills:
        return "Technical Skills"
    elif skill in soft_skills:
        return "Soft Skills"
    elif skill in business_skills:
        return "Business Skills"
    else:
        return "Other Skills"


def get_related_skills(skill):
    """
    Get skills related to a given skill.
    In a real implementation, this would use the ASC dataset.

    Args:
        skill: Skill to find related skills for

    Returns:
        list: List of related skills
    """
    # This is a simplified implementation
    # In a real system, this would use the ASC dataset relationships

    related_skills = {
        "Python": ["Django", "Flask", "Data Analysis", "Machine Learning", "AI"],
        "JavaScript": ["HTML", "CSS", "React", "Angular", "Vue.js", "Node.js"],
        "Java": ["Spring", "Hibernate", "Android Development"],
        "SQL": ["Database", "Data Analysis", "PostgreSQL", "MySQL"],
        "AWS": ["Cloud Computing", "Docker", "Kubernetes", "DevOps"],
        "Machine Learning": ["Python", "Data Science", "AI", "TensorFlow", "PyTorch"],
        "Communication": ["Presentation", "Writing", "Teamwork"],
        "Leadership": ["Management", "Project Management", "Team Management"],
        "Project Management": ["Agile", "Scrum", "Leadership", "Time Management"]
    }

    return related_skills.get(skill, [])