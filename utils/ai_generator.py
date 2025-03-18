import os
import openai
import streamlit as st
import json

# Initialize OpenAI API - you'll need to set this in your Streamlit secrets
def get_openai_api_key():
    try:
        if 'openai' in st.secrets and 'api_key' in st.secrets['openai']:
            return st.secrets['openai']['api_key']
        else:
            # For local testing - should be removed in production
            return os.environ.get("OPENAI_API_KEY")
    except Exception as e:
        st.error(f"Error getting OpenAI API key: {e}")
        return None

def initialize_openai():
    api_key = get_openai_api_key()
    if api_key:
        openai.api_key = api_key
        return True
    return False

def generate_ai_strategies(form_data, fallback_strategies=None):
    """
    Generate personalized launch strategies using OpenAI GPT
    
    Args:
        form_data (dict): User form data with selections
        fallback_strategies (list, optional): Fallback strategies if API fails
        
    Returns:
        list: AI-generated launch strategies
    """
    if not initialize_openai():
        if fallback_strategies:
            return fallback_strategies
        return ["API key not configured. Please contact support."]
    
    try:
        # Create a prompt that follows the Moxie brand voice
        prompt = f"""
        As a High-Impact Launch Assistant for Moxie, I need to create 3 personalized launch strategies for a startup founder.
        
        About Moxie: We help bold, visionary founders who refuse to be ignored. Our tone is confident but warm, 
        ambitious but down-to-earth, and we focus on high-impact strategies that actually move the needle.
        
        About the founder:
        - Startup Name: {form_data['startup_name']}
        - Launch Type: {form_data['launch_type']}
        - Funding Status: {form_data['funding_status']}
        - Primary Goal: {form_data['primary_goal']}
        - Audience Readiness: {form_data['audience_readiness']}
        - Post-Launch Priority: {form_data['post_launch_priority']}
        - Messaging Validation Status: {form_data['messaging_tested']}
        
        Create 3 highly specific, actionable launch strategies tailored to this founder's situation.
        Each strategy should be 1-2 sentences long and focus on high-impact visibility and traction.
        Use a confident, warm tone that speaks directly to the founder.
        Do not label or number your strategies, just provide them as a list.
        
        Example strategy format: "Build a pre-launch email sequence that shares your founder story over 5 days, ending with exclusive early access for subscribers."
        """
        
        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use the appropriate model (gpt-4, gpt-3.5-turbo, etc.)
            messages=[
                {"role": "system", "content": "You are the Moxie High-Impact Launch Assistant, an expert in startup marketing and visibility strategies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and format the response
        strategies_text = response.choices[0].message['content'].strip()
        
        # Split by newlines and clean up
        strategies = [line.strip() for line in strategies_text.split('\n') if line.strip()]
        
        # Remove any numbering or bullets
        strategies = [s.strip().lstrip('0123456789.-• ') for s in strategies]
        
        # Ensure we have at least 3 strategies
        if len(strategies) < 3:
            if fallback_strategies:
                missing = 3 - len(strategies)
                strategies.extend(fallback_strategies[:missing])
            else:
                # Add generic strategies if needed
                while len(strategies) < 3:
                    strategies.append(f"Focus on high-impact visibility tactics tailored to your {form_data['launch_type'].lower()} situation.")
        
        # Limit to 3 strategies
        return strategies[:3]
        
    except Exception as e:
        st.error(f"Error generating AI strategies: {e}")
        # Use fallback strategies if available
        if fallback_strategies:
            return fallback_strategies
        return [
            "Create a compelling story that connects your mission to customer needs.",
            "Focus on 1-2 high-impact marketing channels that align with your resources.",
            "Build relationships with influencers and partners in your industry."
        ]

def generate_ai_next_steps(form_data, fallback_steps=None):
    """
    Generate personalized next steps using OpenAI GPT
    
    Args:
        form_data (dict): User form data with selections
        fallback_steps (list, optional): Fallback steps if API fails
        
    Returns:
        list: AI-generated next steps
    """
    if not initialize_openai():
        if fallback_steps:
            return fallback_steps
        return ["API key not configured. Please contact support."]
    
    try:
        # Create a prompt
        prompt = f"""
        As a High-Impact Launch Assistant for Moxie, I need to create 3 personalized next steps for a startup founder's launch plan.
        
        About Moxie: We help bold, visionary founders who refuse to be ignored. Our tone is confident but warm, 
        ambitious but down-to-earth, and we focus on high-impact strategies that actually move the needle.
        
        About the founder:
        - Startup Name: {form_data['startup_name']}
        - Launch Type: {form_data['launch_type']}
        - Funding Status: {form_data['funding_status']}
        - Primary Goal: {form_data['primary_goal']}
        - Audience Readiness: {form_data['audience_readiness']}
        - Post-Launch Priority: {form_data['post_launch_priority']}
        - Messaging Validation Status: {form_data['messaging_tested']}
        
        Create 3 specific, actionable next steps that this founder should take immediately after their launch.
        Focus on their post-launch priority of "{form_data['post_launch_priority']}".
        Each step should be 1-2 sentences and start with an action verb.
        Format each step with a number (1., 2., 3.) followed by the action.
        
        Example step format: "1. Document which launch channels delivered the highest ROI in your first week by tracking traffic sources and conversion rates."
        """
        
        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are the Moxie High-Impact Launch Assistant, an expert in startup marketing and visibility strategies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and format the response
        steps_text = response.choices[0].message['content'].strip()
        
        # Split by newlines and clean up
        steps = [line.strip() for line in steps_text.split('\n') if line.strip()]
        
        # Ensure we have at least 3 steps
        if len(steps) < 3:
            if fallback_steps:
                missing = 3 - len(steps)
                steps.extend(fallback_steps[:missing])
            else:
                # Add generic steps if needed
                while len(steps) < 3:
                    steps.append(f"{len(steps)+1}. Focus on analyzing early results and optimizing your approach based on what's working.")
        
        # Limit to 3 steps
        return steps[:3]
        
    except Exception as e:
        st.error(f"Error generating AI next steps: {e}")
        # Use fallback steps if available
        if fallback_steps:
            return fallback_steps
        return [
            "1. Document what worked and what didn't in your launch.",
            "2. Focus on optimizing your best-performing channel.",
            "3. Create a 30-day action plan based on initial results."
        ]

def generate_ai_messaging_advice(messaging_tested):
    """
    Generate personalized messaging advice using OpenAI GPT
    
    Args:
        messaging_tested (str): User's response about messaging testing
        
    Returns:
        str: AI-generated messaging advice
    """
    if not initialize_openai():
        # Return default responses based on the selection
        if "Yes, I've gotten direct feedback" in messaging_tested:
            return "Your messaging is already rooted in real insights, which gives us a solid foundation for your launch."
        elif "Sort of... I've talked to people" in messaging_tested:
            return "Before finalizing your launch plan, consider conducting structured interviews with your ideal audience to collect specific feedback on what's compelling and what would make them buy."
        else:
            return "Your first step should be validating your messaging. Create a draft landing page and put it in front of your target audience to collect real reactions before investing in your launch."
    
    try:
        # Create a prompt
        prompt = f"""
        As a High-Impact Launch Assistant for Moxie, I need to provide personalized messaging advice based on a founder's response.
        
        About Moxie: We help bold, visionary founders who refuse to be ignored. Our tone is confident but warm, 
        ambitious but down-to-earth, and we focus on high-impact strategies that actually move the needle.
        
        The founder's response to "Have you tested your messaging with real customers?" was:
        "{messaging_tested}"
        
        Provide a short paragraph (2-3 sentences) of advice about messaging validation.
        Be specific, actionable, and maintain Moxie's confident but warm tone.
        
        If they've tested messaging, acknowledge this as a strong foundation.
        If they've done some testing but not structured, suggest a specific approach to formalize it.
        If they haven't tested, emphasize this as a critical first step with a concrete action item.
        """
        
        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are the Moxie High-Impact Launch Assistant, an expert in startup marketing and visibility strategies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        # Return the response
        return response.choices[0].message['content'].strip()
        
    except Exception as e:
        st.error(f"Error generating AI messaging advice: {e}")
        # Return default responses based on the selection
        if "Yes, I've gotten direct feedback" in messaging_tested:
            return "Your messaging is already rooted in real insights, which gives us a solid foundation for your launch."
        elif "Sort of... I've talked to people" in messaging_tested:
            return "Before finalizing your launch plan, consider conducting structured interviews with your ideal audience to collect specific feedback on what's compelling and what would make them buy."
        else:
            return "Your first step should be validating your messaging. Create a draft landing page and put it in front of your target audience to collect real reactions before investing in your launch."