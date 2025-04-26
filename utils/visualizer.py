import openai
import math
import streamlit as st
from utils.supabase_data_utils import fetch_saved_skills, fetch_saved_competencies

def create_svg_skills_visualization(categorized_skills):
    """
    Creates an SVG string to visualize categorized skills in a non-overlapping, aesthetic layout.
    """

    colors = {
        "Technical Skills": "#1f77b4",
        "Soft Skills": "#ff7f0e",
        "Business Skills": "#2ca02c"
    }

    center_positions = {
        "Technical Skills": (700, 700),
        "Soft Skills": (1000, 200),
        "Business Skills": (400, 200)
    }

    canvas_width = 1400
    canvas_height = 900

    svg = f"""
    <div id="svg-container" style="overflow: auto; width: 100%; height: 100%;">
        <svg width="{canvas_width}" height="{canvas_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f9f9f9" rx="10" ry="10" />
    """

    for category, skills in categorized_skills.items():
        center_x, center_y = center_positions.get(category, (canvas_width // 2, canvas_height // 2))
        color = colors.get(category, "#999")


        radius = 140 + len(skills) * 2
        angle_step = 360 / max(len(skills), 1)

        for i, skill in enumerate(skills):
            angle = math.radians(i * angle_step)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            svg += f"""
            <line x1="{center_x}" y1="{center_y}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="1" opacity="0.35"/>
            <circle cx="{x}" cy="{y}" r="30" fill="{color}" opacity="0.35"/>
            <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle"
                  font-size="11" font-family="Arial" fill="black" stroke="black" stroke-width="0.3" font-weight="normal">{skill}</text>
            """

        # Draw center node on top with more opacity and depth
        svg += f"""
        <circle cx="{center_x}" cy="{center_y}" r="70" fill="{color}" opacity="0.9" />
        <text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle"
              font-size="16" font-family="Arial" fill="white" font-weight="bold">{category}</text>
        """

    svg += "</svg></div>"
    return svg

def categorize_skills(supabase, user_id):
    resume_skills = fetch_saved_skills(supabase,user_id,)
    core_competencies = fetch_saved_competencies(supabase,user_id)

    categorized = {
        "Technical Skills": [],
        "Soft Skills": [],
        "Business Skills": []
    }

    soft_keywords = ["teamwork", "communication", "problem solving", "initiative and innovation", "learning"]
    business_keywords = ["digital literacy", "planning and organisation", "numeracy", "reading", "writing"]

    for comp in core_competencies:
        skill = comp.get("competency_name", "").lower()
        if skill in soft_keywords:
            categorized["Soft Skills"].append(skill)
        if skill in business_keywords:
            categorized["Business Skills"].append(skill)

    for skill in resume_skills:
        categorized["Technical Skills"].append(skill.lower())

    return categorized
