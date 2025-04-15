import streamlit as st

def get_user_profile(supabase, user):
    try:
        response = supabase.table('profiles').select('*').eq('id', user.iselectd).maybe_single().execute()
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error fetching profile: {e}")
        return None

def get_user_skills(supabase, user):
    try:
        response = supabase.table('user_skills').select('skill').eq('user_id', user.id).execute()
        return [item['skill'] for item in response.data] if response.data else []
    except Exception as e:
        st.error(f"Error fetching skills: {e}")
        return []

def add_user_skill(supabase, user, skill):
    try:
        # Use upsert=True if you want to ignore duplicates based on UNIQUE constraint
        response = supabase.table('user_skills').insert({"user_id": user.id, "skill": skill}, upsert=True).execute()
        # Check response.data to see if insert happened or was ignored
        return len(response.data) > 0 # True if inserted/updated
    except Exception as e:
        st.error(f"Error adding skill: {e}")
        return False

def get_user_competencies(supabase, user):
    try:
        response = supabase.table('user_competencies').select('competency_name, rating').eq('user_id', user.id).execute()
        return {item['competency_name']: item['rating'] for item in response.data} if response.data else {}
    except Exception as e:
        st.error(f"Error fetching competencies: {e}")
        return {}

def save_user_competencies(supabase, user, ratings_dict):
    try:
        data_to_upsert = [
            {"user_id": user.id ,  "competency_name": name, "rating": rating}
            for name, rating in ratings_dict.items()
        ]
        if not data_to_upsert:
            return True # Nothing to save
        response = supabase.table('user_competencies').upsert(data_to_upsert).execute()
        return True
    except Exception as e:
        st.error(f"Error saving competencies: {e}")
        return False