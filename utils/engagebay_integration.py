import requests
import json
import streamlit as st

def send_to_engagebay(first_name, email):
    """
    Send user's first name and email to EngageBay
    
    Args:
        first_name (str): User's first name
        email (str): User's email address
        
    Returns:
        bool: Success status
    """
    try:
        url = "https://app.engagebay.com/dev/api/panel/subscribers/subscriber"
        
        # Get API key from secrets
        api_key = st.secrets.get("engagebay", {}).get("api_key")
        
        if not api_key:
            return False
        
        # Headers with API key
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Contact data with tags
        data = {
            "properties": [
                {
                    "name": "name",
                    "value": first_name,
                    "type": "SYSTEM"
                },
                {
                    "name": "email", 
                    "value": email,
                    "type": "SYSTEM"
                }
            ],
            "tags": ["moxie-app"]
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # Return success status
        return response.status_code in [200, 201, 202]
        
    except Exception as e:
        return False