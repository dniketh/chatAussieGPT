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
        response = supabase.table('user_skills').insert({"user_id": user.id, "skill": skill}, upsert=True).execute()
        return len(response.data) > 0
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

        existing_response = (
            supabase.table("user_competencies")
            .select("competency_name, rating")
            .eq("user_id", user.id)
            .execute()
        )

        existing_data = {
            item["competency_name"]: item["rating"]
            for item in existing_response.data
        } if existing_response.data else {}

        all_same = all(existing_data.get(name) == rating for name, rating in ratings_dict.items())
        if all_same and len(existing_data) == len(ratings_dict):
            return "already_exists", 0

        saved_count = 0
        for name, rating in ratings_dict.items():
            if existing_data.get(name) != rating:

                update_result = supabase.table("user_competencies") \
                    .update({"rating": rating}) \
                    .eq("user_id", user.id) \
                    .eq("competency_name", name) \
                    .execute()

                if not update_result.data:
                    insert_result = supabase.table("user_competencies") \
                        .insert({
                            "user_id": user.id,
                            "competency_name": name,
                            "rating": rating
                        }) \
                        .execute()

                    if insert_result.data:
                        saved_count += 1
                else:
                    saved_count += 1

        if saved_count > 0:
            return "updated", saved_count
        else:
            return "already_exists", 0

    except Exception as e:
        st.error(f"❌ Something went wrong while saving competencies: {e}")
        return "error", 0

    
def save_user_skills_to_supabase(supabase, user, skills):
    """
    Save extracted skills to Supabase for the given user in the competency format.
    
    Args:
        supabase: Supabase client object
        user: Supabase authenticated user object
        skills: List of extracted skills
    
    Returns:
        (status: str, count: int)
            status can be "already_exists", "saved", or "error"
    """
    saved_count = 0
    try:
        existing = (
            supabase.table("user_skills")
            .select("skill")
            .eq("user_id", user.id)
            .in_("skill", skills)
            .execute()
        )

        existing_skills = {item["skill"] for item in existing.data}

        if len(existing_skills) == len(set(skills)):
            return "already_exists", 0

        data_to_upsert = [
            {"user_id": user.id, "skill": skill}
            for skill in skills
            if skill not in existing_skills
        ]

        if data_to_upsert:
            supabase.table("user_skills").upsert(data_to_upsert).execute()
            saved_count = len(data_to_upsert)

        return "saved", saved_count

    except Exception as e:
        st.error(f"Error saving skills to Supabase: {e}")
        return "error", 0

def fetch_saved_skills(supabase, user_id):
    try:
        response = supabase.table("user_skills").select("skill").eq("user_id", user_id).execute()
        if response.data:
            return [entry["skill"] for entry in response.data if "skill" in entry]
        return []
    except Exception as e:
        print("❌ Error fetching skills:", e)
        return []


def fetch_saved_competencies(supabase, user_id):
    try:
        response = supabase.table("user_competencies").select("*").eq("user_id", user_id).execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        print(f"Error fetching competencies: {e}")
        return []
def get_competency_ratings(supabase, user_id):
    """
    Retrieves competency ratings (Business & Soft skills) for a given user from Supabase.
    Ratings are expected on a scale from 0 to 10.
    
    Returns:
        dict: A dictionary {skill_name: rating}
    """
    try:
        response = supabase.table("user_competencies").select("competency_name", "rating").eq("user_id", user_id).execute()

        if response.error:
            print(f"Error fetching ratings: {response.error}")
            return {}

        ratings = {}
        for record in response.data:
            skill_name = record.get("competency_name")
            rating = record.get("rating")
            if skill_name is not None:
                ratings[skill_name] = float(rating)

        return ratings
    except Exception as e:
        print(f"Error retrieving competency ratings: {e}")
        return {}
