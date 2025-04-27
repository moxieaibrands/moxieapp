import json
import os
import streamlit as st

def load_strategies():
    """Load strategies from JSON file if it exists"""
    try:
        if os.path.exists("data/strategies.json"):
            with open("data/strategies.json", "r") as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Error loading strategies: {e}")
        return None