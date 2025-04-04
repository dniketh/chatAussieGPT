def generate_career_matches(skills):
    """
    Generate career matches based on skills.
    In a real implementation, this would use the ASC dataset.

    Args:
        skills: List of user's skills

    Returns:
        list: List of career match dictionaries
    """
    # This is just a placeholder

    matches = [
        {
            "title": "Software Developer (ANZSCO: 261312)",
            "description": "Designs, develops, and maintains software applications and systems.",
            "match_score": 85,
            "required_skills": ["Python", "JavaScript", "Problem Solving"],
            "skill_gaps": ["DevOps", "Cloud Computing"]
        },
        {
            "title": "Data Analyst (ANZSCO: 224711)",
            "description": "Analyzes data to provide business insights and support decision-making.",
            "match_score": 78,
            "required_skills": ["SQL", "Data Analysis", "Communication"],
            "skill_gaps": ["Statistical Modeling", "Tableau"]
        },
        {
            "title": "Project Manager (ANZSCO: 511112)",
            "description": "Plans, organizes, and oversees the completion of projects.",
            "match_score": 72,
            "required_skills": ["Project Management", "Leadership", "Communication"],
            "skill_gaps": ["Risk Management", "Agile Methodologies"]
        },
        {
            "title": "UX Designer (ANZSCO: 232414)",
            "description": "Designs user experiences for digital products and services.",
            "match_score": 65,
            "required_skills": ["UI Design", "User Research", "Problem Solving"],
            "skill_gaps": ["Prototyping", "User Testing", "Information Architecture"]
        }
    ]

    return matches


def calculate_skill_match(user_skills, job_skills):
    """
    Calculate the match score between user skills and job required skills.

    Args:
        user_skills: List of user's skills
        job_skills: List of skills required for a job

    Returns:
        float: Match score as a percentage
    """
    if not job_skills:
        return 0

    matching_skills = [skill for skill in user_skills if skill in job_skills]
    match_percentage = (len(matching_skills) / len(job_skills)) * 100

    return round(match_percentage)


# utils/career_matching.py (update with new function)

def generate_career_matches_with_competencies(skills, competencies):
    """
    Generate career matches based on skills and core competencies.

    Args:
        skills: List of user's skills
        competencies: Dictionary of user's core competency ratings

    Returns:
        list: List of career match dictionaries
    """
    # Get base matches based on skills
    matches = generate_career_matches(skills)

    # Define competency relevance for each job
    # In a real implementation, this would come from the ASC dataset
    job_competencies = {
        "Software Developer (ANZSCO: 261312)": {
            "Digital Literacy": 5,
            "Problem Solving": 5,
            "Learning": 4,
            "Communication": 3,
            "Teamwork": 3
        },
        "Data Analyst (ANZSCO: 224711)": {
            "Digital Literacy": 5,
            "Numeracy": 5,
            "Problem Solving": 4,
            "Communication": 3,
            "Initiative and Innovation": 3
        },
        "Project Manager (ANZSCO: 511112)": {
            "Communication": 5,
            "Planning and Organisation": 5,
            "Teamwork": 4,
            "Problem Solving": 3,
            "Initiative and Innovation": 3
        },
        "UX Designer (ANZSCO: 232414)": {
            "Digital Literacy": 4,
            "Communication": 4,
            "Problem Solving": 4,
            "Initiative and Innovation": 5,
            "Teamwork": 3
        }
    }

    # Adjust match scores based on competencies
    for match in matches:
        job_title = match["title"]

        if job_title in job_competencies:
            # Get relevant competencies for this job
            relevant_comps = job_competencies[job_title]

            # Calculate competency match score
            comp_score = 0
            comp_total = 0

            for comp_name, required_level in relevant_comps.items():
                comp_total += required_level

                # If user has rated this competency
                if comp_name in competencies:
                    user_level = competencies[comp_name]

                    # Award points based on how close user is to required level
                    if user_level >= required_level:
                        comp_score += required_level
                    else:
                        comp_score += user_level

            # Calculate percentage
            comp_match_pct = (comp_score / comp_total) * 100 if comp_total > 0 else 0

            # Blend skills match and competency match (equal weighting)
            original_match = match["match_score"]
            blended_score = (original_match + comp_match_pct) / 2

            # Update match score
            match["match_score"] = int(blended_score)

            # Add competency information
            match["competency_match"] = int(comp_match_pct)
            match["key_competencies"] = list(relevant_comps.keys())

    # Re-sort matches based on updated scores
    matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)

    return matches
def identify_skill_gaps(user_skills, job_skills):
    """
    Identify skills gaps between user skills and job requirements.

    Args:
        user_skills: List of user's skills
        job_skills: List of skills required for a job

    Returns:
        list: List of missing skills
    """
    return [skill for skill in job_skills if skill not in user_skills]


def get_career_path(starting_job, target_job):
    """
    Get a career path from starting job to target job.

    Args:
        starting_job: Starting job title or ANZSCO code
        target_job: Target job title or ANZSCO code

    Returns:
        list: List of jobs in the career path
    """
    # This would be implemented in a real system
    # For now, return a placeholder
    return ["Junior Developer", "Developer", "Senior Developer", "Lead Developer"]