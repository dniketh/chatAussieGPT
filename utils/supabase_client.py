from supabase import create_client
import os
import streamlit as st
@st.cache_resource
def init_supabase_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    try:
        client = create_client(url, key)
        st.success("Connected to Supabase!")
        return client
    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        return None

supabase = init_supabase_connection()