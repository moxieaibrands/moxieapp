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
        # EngageBay API endpoint for adding a contact
        # Note: Using contact API instead of subscriber API
        url = "https://api.engagebay.com/dev/api/panel/contacts"
        
        # Get API key from secrets or use the one provided
        api_key = st.secrets.get("engagebay", {}).get("api_key", "cak8t5icrm193ahgtjee7sbcud")
        
        # Try different authentication method
        headers = {
            "X-AUTH-TOKEN": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Prepare data payload - simplified to match API specs
        data = {
            "properties": [
                {
                    "name": "first_name",
                    "value": first_name
                },
                {
                    "name": "email",
                    "value": email
                },
                {
                    "name": "source",
                    "value": "moxie-app"
                }
            ]
        }
        
        # Debug info
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        # Make the API request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # Check if successful
        if response.status_code in [200, 201, 202]:
            print(f"Contact added successfully: {response.text}")
            return True
        else:
            print(f"Error adding contact: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception in EngageBay integration: {str(e)}")
        return False
        