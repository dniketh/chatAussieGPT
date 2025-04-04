import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os
import streamlit as st

# Global variables for model and tokenizer
model = None
tokenizer = None


def initialize_model():
    """Initialize the finetuned model (call this once at app startup)"""
    global model, tokenizer

    # Load the model if not already loaded
    if model is None or tokenizer is None:
        load_model()


def load_model():
    """Load the finetuned model and tokenizer"""
    global model, tokenizer

    # Path to your finetuned adapter
    adapter_path = "./llama3-asc-finetuned-adapter"

    # Check if adapter exists
    if not os.path.exists(adapter_path):
        print("Adapter not found. Using mock responses.")
        return False

    try:
        # Load base model with quantization
        base_model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            load_in_4bit=True,
            device_map="auto"
        )

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct")
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Load your adapter weights
        model = PeftModel.from_pretrained(base_model, adapter_path)

        print("Model loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False


def generate_response(user_query, context=None, user_skills=None):
    """
    Generate a response using the finetuned LLM.

    Args:
        user_query: User's query string
        context: Unused parameter (kept for compatibility)
        user_skills: List of user's skills (can be None)

    Returns:
        str: Generated response text
    """
    global model, tokenizer

    # Initialize model if needed
    if model is None or tokenizer is None:
        model_loaded = load_model()
        if not model_loaded:
            return "I'm sorry, but I couldn't load the model. Please try again later."

    # Collect skills from parameter and session state
    all_skills = []

    # Skills passed as parameter
    if user_skills and len(user_skills) > 0:
        all_skills.extend(user_skills)

    # Skills from session state
    if "skills" in st.session_state and st.session_state.skills:
        for skill in st.session_state.skills:
            if skill not in all_skills:
                all_skills.append(skill)

    # Skills from resume
    if "resume_skills" in st.session_state and st.session_state.resume_skills:
        for skill in st.session_state.resume_skills:
            if skill not in all_skills:
                all_skills.append(skill)

    # Format skills as text
    skills_text = ", ".join(all_skills) if all_skills else ""

    # Get competency ratings
    competency_text = ""
    if "competencies" in st.session_state and st.session_state.competencies:
        competency_items = []
        for comp_name, rating in st.session_state.competencies.items():
            competency_items.append(f"{comp_name}: {rating}")
        competency_text = ", ".join(competency_items)

    # Format input for the model
    model_input = ""
    if skills_text:
        model_input = skills_text

    if competency_text:
        if model_input:
            model_input += f"\n{competency_text}"
        else:
            model_input = competency_text

    # Format prompt for the model
    prompt = f"""### Instruction:
Respond to the user query based on the skills and competency information provided.

### Input:
{model_input}
User query: {user_query}

### Response:
"""

    try:
        # Generate response from model
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )

        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the generated response
        response_parts = full_response.split("### Response:")
        if len(response_parts) > 1:
            return response_parts[-1].strip()
        else:
            return full_response

    except Exception as e:
        print(f"Error generating response: {e}")
        return f"I encountered an error when generating a response: {str(e)}"