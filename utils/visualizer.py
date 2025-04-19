import openai
import math
import streamlit as st

def categorize_skills_with_gpt(skills, api_key):
    """
    Categorizes a list of skills using GPT into categories:
    Technical, Soft, Business, and Other.
    """
    openai.api_key = api_key

    prompt = f"""
You are a helpful assistant who categorizes skills.
Given the following list of skills, categorize them into:
- Technical Skills
- Soft Skills
- Business Skills
- Other Skills

Return a valid Python dictionary with the category names as keys
and lists of skills as values.

Skills: {skills}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600
        )
        result = response.choices[0].message.content.strip()
        categories = eval(result) if result.startswith("{") else {}
        return categories
    except Exception as e:
        print("Error in categorization:", e)
        return {
            "Technical Skills": [],
            "Soft Skills": [],
            "Business Skills": [],
            "Other Skills": skills
        }


def create_svg_skills_visualization(categorized_skills):
    """
    Creates an SVG string to visualize categorized skills in a non-overlapping, aesthetic layout.
    """

    colors = {
        "Technical Skills": "#1f77b4",
        "Soft Skills": "#ff7f0e",
        "Business Skills": "#2ca02c",
        "Other Skills": "#d62728"
    }

    center_positions = {
        "Technical Skills": (250, 200),
        "Soft Skills": (750, 200),
        "Business Skills": (250, 500),
        "Other Skills": (750, 500)
    }

    canvas_width = 1200
    canvas_height = 800

    svg = f"""
    <div id="svg-container" style="overflow: auto; width: 100%; height: 100%;">
        <svg width="{canvas_width}" height="{canvas_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#f9f9f9" rx="10" ry="10" />
    """

    for category, skills in categorized_skills.items():
        center_x, center_y = center_positions.get(category, (canvas_width // 2, canvas_height // 2))
        color = colors.get(category, "#999")

        # Category bubble
        svg += f"""
        <circle cx="{center_x}" cy="{center_y}" r="70" fill="{color}" opacity="0.1" />
        <text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle"
              font-size="16" font-family="Arial" fill="{color}">{category}</text>
        """

        # Skill layout
        radius = 140 + len(skills) * 2  # Increase spacing dynamically
        angle_step = 360 / max(len(skills), 1)

        for i, skill in enumerate(skills):
            angle = math.radians(i * angle_step)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            svg += f"""
            <line x1="{center_x}" y1="{center_y}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="1" opacity="0.3"/>
            <circle cx="{x}" cy="{y}" r="34" fill="{color}" opacity="0.7"/>
            <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="middle"
                  font-size="11" font-family="Arial" fill="black" stroke="Black" stroke-width="0.5" font-weight="normal">{skill}</text>
            """

    svg += "</svg></div>"
    return svg
