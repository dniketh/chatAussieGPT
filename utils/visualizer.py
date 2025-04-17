import math
import network as nx
import random
from utils.resume_parser import load_local_llm
from gpt4all import GPT4All
import re

def categorize_skills_with_gpt4all(skills):
    """
    Categorizes a list of skills into Technical, Soft, Business, or Other using GPT4All.

    Args:
        skills (list): List of skill strings.
        model_path (str): Path to your GPT4All model file (e.g. orca-2-7b.Q4_0.gguf).

    Returns:
        dict: A dictionary with categorized skills.
    """
    model = load_local_llm()

    prompt = f"""
You are an AI assistant. Categorize the following list of skills into one of these four categories:
1. Technical Skills
2. Soft Skills
3. Business Skills
4. Other Skills

Return the result as a valid Python dictionary with category names as keys and lists of skill names as values.

Skills:
{skills}
"""

    try:
        response = model.generate(prompt, max_tokens=512, temp=0.2)
        # Simple sanitization and eval fallback
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            result = eval(match.group())
            if isinstance(result, dict):
                return result
    except Exception as e:
        print(f"GPT4All categorization error: {e}")

    # Fallback
    return {
        "Technical Skills": [],
        "Soft Skills": [],
        "Business Skills": [],
        "Other Skills": skills
    }

def create_simple_skills_visualization(skills):
    """
    Create a vertical skills visualization optimized for sidebar display.
    """
    categories = categorize_skills_with_gpt4all(skills)

    # Colors for categories
    colors = {
        "Technical Skills": "#4285F4",
        "Soft Skills": "#FBBC05",
        "Business Skills": "#34A853",
        "Other Skills": "#EA4335"
    }

    # Layout (adjusted for sidebar)
    x_position = 150        # Center in smaller SVG
    y_start = 10            # Start closer to top
    y_spacing = 80          # Slightly tighter spacing
    category_spacing = 80   # Less space between categories

    total_height = y_start
    for cat in colors.keys():
        skill_count = len(categories.get(cat, []))
        total_height += category_spacing + skill_count * y_spacing

    html = f"""
    <div style="width:100%;">
        <svg width="100%" height="{total_height}" viewBox="0 0 300 {total_height}">
            <rect width="300" height="{total_height}" fill="#f8f9fa" rx="10" ry="10" />
    """

    current_y = y_start

    for category, color in colors.items():
        skills_in_category = categories.get(category, [])

        # Category heading
        html += f"""
        <text x="{x_position}" y="{current_y}" text-anchor="middle" dominant-baseline="middle"
              font-family="Arial" font-size="16" font-weight="bold" fill="{color}">{category}</text>
        """
        current_y += category_spacing

        # Skill bubbles
        for skill in skills_in_category:
            html += f"""
            <circle cx="{x_position}" cy="{current_y}" r="30" fill="{color}" opacity="0.9" />
            <text x="{x_position}" y="{current_y}" text-anchor="middle" dominant-baseline="middle"
                  font-family="Arial" font-size="10" fill="black">{skill}</text>
            """
            current_y += y_spacing

    html += "</svg></div>"

    return html


def create_career_path_visualization(current_skills, target_job):
    html = """
    <div style="width:100%; text-align:center;">
        <h4>Career Path Visualization Placeholder</h4>
        <p>This would show a pathway from your current skills to the target job.</p>
    </div>
    """
    return html


def create_skills_network_graph(skills, skill_relationships):
    html = """
    <div style="width:100%; text-align:center;">
        <h4>Skills Network Graph Placeholder</h4>
        <p>This would show a network graph of your skills and their relationships.</p>
    </div>
    """
    return html
