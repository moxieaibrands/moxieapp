import json
import os
import streamlit as st
import re

# Try to import OpenAI in different ways based on version
try:
    # For newer versions (v1.0.0+)
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
    USE_LEGACY_OPENAI = False
except ImportError:
    # For older versions
    import openai
    openai.api_key = st.secrets["openai"]["api_key"]
    USE_LEGACY_OPENAI = True

def parse_ai_response(ai_text):
    """
    Parse the AI generated text into structured data
    
    Args:
        ai_text (str): Raw text from AI response
        
    Returns:
        dict: Structured data with messaging_advice, strategies, and next_steps
    """
    result = {
        'messaging_advice': '',
        'recommended_strategies': [],
        'strategies': [],
        'next_steps': []
    }
    
    # Extract messaging advice
    messaging_match = re.search(r"Messaging Advice:(.*?)(?=Recommended Strategies:|$)", ai_text, re.DOTALL)
    if messaging_match:
        result['messaging_advice'] = messaging_match.group(1).strip()
    
    # Extract strategies
    strategies_match = re.search(r"Recommended Strategies:(.*?)(?=Next Steps:|$)", ai_text, re.DOTALL)
    if strategies_match:
        strategies_text = strategies_match.group(1).strip()
        # Split by numbered items (1., 2., 3., etc.)
        strategies = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', strategies_text + "999.", re.DOTALL)
        result['recommended_strategies'] = [s.strip() for s in strategies if s.strip()]
        
        # Also add structured format for consistency
        result['strategies'] = [{"title": s.split('.')[0].strip() if '.' in s else s, 
                               "description": s} for s in result['recommended_strategies']]
    
    # Extract next steps
    next_steps_match = re.search(r"Next Steps:(.*?)$", ai_text, re.DOTALL)
    if next_steps_match:
        next_steps_text = next_steps_match.group(1).strip()
        # Split by numbered items (1., 2., 3., etc.)
        next_steps = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', next_steps_text + "999.", re.DOTALL)
        
        # Also add structured format for consistency
        result['next_steps'] = [{"title": s.split('.')[0].strip() if '.' in s else s, 
                               "description": s} for s in [ns.strip() for ns in next_steps if ns.strip()]]
    
    return result

def generate_ai_launch_plan(form_data, external_strategies=None):
    """
    Generate a personalized launch plan using an AI language model.
    
    Args:
        form_data (dict): User inputs from the multi-step form.
        external_strategies (dict, optional): Additional strategy data (if needed).
        
    Returns:
        dict: A plan dictionary containing AI-generated content.
    """
    prompt = f"""
You are a high-impact launch assistant speaking directly to startup founders. Based on the following details, generate a personalized launch plan that includes:
- Concise messaging advice.
- Three recommended strategies tailored to the founder's context.
- Three actionable next steps for post-launch momentum.

Founder Details:
First Name: {form_data['first_name']}
Startup Name: {form_data['startup_name']}
Messaging Tested: {form_data['messaging_tested']}
Launch Type: {form_data['launch_type']}
Funding Status: {form_data['funding_status']}
Primary Goal: {form_data['primary_goal']}
Audience Readiness: {form_data['audience_readiness']}
Post-launch Priority: {form_data['post_launch_priority']}

Your answer should be structured exactly as follows:

Messaging Advice:
[Your messaging advice here]

Recommended Strategies:
1. [Strategy one]
2. [Strategy two]
3. [Strategy three]

Next Steps:
1. [Next step one]
2. [Next step two]
3. [Next step three]

Use a confident, direct, and founder-to-founder tone.
    """

    # Use the appropriate OpenAI API based on the available version
    if USE_LEGACY_OPENAI:
        # Old style API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a high-impact launch assistant speaking directly to startup founders. Use a confident, direct, founder-to-founder tone."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        output = response.choices[0].message.content.strip()
    else:
        # New style API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a high-impact launch assistant speaking directly to startup founders. Use a confident, direct, founder-to-founder tone."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        output = response.choices[0].message.content.strip()
    
    # Parse the AI output into structured data
    structured_data = parse_ai_response(output)
    
    # Return a plan with the AI-generated content in the expected structure
    plan = {
        'first_name': form_data['first_name'],
        'startup_name': form_data['startup_name'],
        'messaging_advice': structured_data['messaging_advice'],
        'launch_summary': {
            'launch_type': form_data['launch_type'],
            'funding_status': form_data['funding_status'],
            'primary_goal': form_data['primary_goal']
        },
        'recommended_strategies': structured_data['recommended_strategies'],
        'strategies': structured_data['strategies'],
        'next_steps': structured_data['next_steps'],
        'ai_generated_plan': output  # Keep raw output for reference
    }
    
    return plan

def generate_launch_plan(form_data, external_strategies=None):
    # Use AI-powered generation if OpenAI credentials are present
    try:
        if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
            return generate_ai_launch_plan(form_data, external_strategies)
    except Exception as e:
        st.error(f"Error using AI generation: {e}")
        # Fall back to static generation if AI generation fails
        
    # Fallback to your static generation logic
    messaging_advice = get_messaging_advice(form_data['messaging_tested'])
    strategies = get_launch_strategies(
        form_data['launch_type'], 
        form_data['funding_status'], 
        form_data['primary_goal'],
        external_strategies
    )
    next_steps = get_next_steps(
        form_data['funding_status'],
        form_data['audience_readiness'],
        form_data['post_launch_priority'],
        external_strategies
    )
    
    # Convert strategies to structured format if they're just strings
    structured_strategies = []
    for strategy in strategies:
        if isinstance(strategy, str):
            title = strategy.split('.')[0].strip() if '.' in strategy else strategy
            structured_strategies.append({
                "title": title,
                "description": strategy
            })
        else:
            structured_strategies.append(strategy)
    
    # Convert next steps to structured format if they're just strings
    structured_next_steps = []
    for step in next_steps:
        if isinstance(step, str):
            title = step.split('.')[0].strip() if '.' in step else step
            structured_next_steps.append({
                "title": title,
                "description": step
            })
        else:
            structured_next_steps.append(step)
    
    plan = {
        'first_name': form_data['first_name'],
        'startup_name': form_data['startup_name'],
        'messaging_advice': messaging_advice,
        'launch_summary': {
            'launch_type': form_data['launch_type'],
            'funding_status': form_data['funding_status'],
            'primary_goal': form_data['primary_goal']
        },
        'recommended_strategies': strategies,
        'strategies': structured_strategies,
        'next_steps': structured_next_steps
    }
    return plan

def get_messaging_advice(messaging_tested):
    """Get personalized messaging advice based on form selection"""
    if "✅ Yes" in messaging_tested:
        return "Your messaging is already rooted in real insights, which gives us a solid foundation for your launch."
    elif "🤔 Sort of" in messaging_tested:
        return "Before finalizing your launch plan, consider conducting 7 structured interviews with your ideal audience. Show them your landing page and collect specific feedback on what's compelling and what would make them buy."
    else:
        return "Your first step should be validating your messaging. Create a draft landing page and put it in front of your target audience to collect real reactions before investing in your launch."

def get_launch_strategies(launch_type, funding_status, primary_goal, external_strategies=None):
    """
    Get launch strategies based on user selections
    
    This function first tries to use externally loaded strategies from a JSON file,
    and falls back to hardcoded strategies if external strategies are not available
    or don't contain the requested combination.
    """
    # Try to get strategies from external file if available
    if external_strategies and 'launch_strategies' in external_strategies:
        try:
            return external_strategies['launch_strategies'][launch_type][funding_status][primary_goal]
        except KeyError:
            # If the combination doesn't exist in external file, fall back to hardcoded
            pass

    # Clean inputs by removing emojis if present
    clean_launch_type = launch_type
    clean_funding_status = funding_status
    clean_primary_goal = primary_goal
    
    # Also try with emoji
    emoji_strategies = {
        "🚀 New Startup/Product Launch": {
            "🚀 Bootstrapping (No external funding, self-funded)": {
                "🚀 Get Users or Customers": [
                    "Focus on founder-led storytelling through guest podcasts and social content",
                    "Create a limited beta program with exclusive perks to drive early adoption",
                    "Build direct relationships with early users for feedback and testimonials"
                ],
                "💰 Attract Investors": [
                    "Document your traction journey publicly to showcase momentum",
                    "Create case studies showing early customer impact",
                    "Target niche industry events where investors in your space gather"
                ],
                "🎙 Build Press & Awareness": [
                    "Craft a compelling founder story that ties to current trends",
                    "Pitch to industry-specific publications rather than mainstream media",
                    "Create shareable content that showcases your unique approach"
                ],
                "🌎 Create Industry Influence": [
                    "Start a focused content series solving key problems in your industry",
                    "Join relevant communities as a contributor, not just a promoter",
                    "Collaborate with complementary startups for wider reach"
                ]
            },
            "🌱 Raised under $1M": {
                "🚀 Get Users or Customers": [
                    "Run targeted ad experiments to identify high-converting messages",
                    "Create an exclusive waitlist with referral incentives",
                    "Partner with complementary products for shared launches"
                ],
                "💰 Attract Investors": [
                    "Build a data-driven pitch showing early traction metrics",
                    "Create investor-specific content demonstrating market understanding",
                    "Get warm introductions through strategic advisory relationships"
                ],
                "🎙 Build Press & Awareness": [
                    "Position your funding as validation for a larger trend story",
                    "Create data-driven content that journalists can easily reference",
                    "Build relationships with 3-5 key reporters in your space"
                ],
                "🌎 Create Industry Influence": [
                    "Participate in industry panels and speaking opportunities",
                    "Launch a small but high-quality thought leadership publication",
                    "Create a community initiative that positions you as a connector"
                ]
            }
        },
        "New Startup/Product Launch": {
            "Bootstrapping (No external funding)": {
                "Get Users or Customers": [
                    "Focus on founder-led storytelling through guest podcasts and social content",
                    "Create a limited beta program with exclusive perks to drive early adoption",
                    "Build direct relationships with early users for feedback and testimonials"
                ],
                "Attract Investors": [
                    "Document your traction journey publicly to showcase momentum",
                    "Create case studies showing early customer impact",
                    "Target niche industry events where investors in your space gather"
                ],
                "Build Press & Awareness": [
                    "Craft a compelling founder story that ties to current trends",
                    "Pitch to industry-specific publications rather than mainstream media",
                    "Create shareable content that showcases your unique approach"
                ],
                "Create Industry Influence": [
                    "Start a focused content series solving key problems in your industry",
                    "Join relevant communities as a contributor, not just a promoter",
                    "Collaborate with complementary startups for wider reach"
                ]
            }
        }
    }
    
    # Try to get strategies with emoji first
    try:
        return emoji_strategies[launch_type][funding_status][primary_goal]
    except KeyError:
        pass
        
    # Try common fallback strategies
    fallback_strategies = [
        "Create a compelling story that connects your mission to customer needs",
        "Focus on 1-2 high-impact marketing channels that align with your resources",
        "Build relationships with influencers and partners in your industry"
    ]
    
    # Return default fallback strategies
    return fallback_strategies

def get_next_steps(funding_status, audience_readiness, post_launch_priority, external_strategies=None):
    """
    Get next steps based on user selections
    
    This function first tries to use externally loaded strategies from a JSON file,
    and falls back to hardcoded next steps if external strategies are not available
    or don't contain the requested combination.
    """
    # Try to get next steps from external file if available
    if external_strategies and 'next_steps' in external_strategies:
        try:
            return external_strategies['next_steps'][funding_status][audience_readiness][post_launch_priority]
        except KeyError:
            # If the combination doesn't exist in external file, fall back to hardcoded
            pass

    # Emoji-based next steps
    emoji_next_steps = {
        "🚀 Bootstrapping (No external funding, self-funded)": {
            "✅ Yes, we have an engaged community": {
                "📈 Scaling & repeatable traction": [
                    "Analyze which launch channels delivered highest ROI",
                    "Document repeatable processes for your best-performing channels",
                    "Create a lean content calendar focused on high-conversion topics"
                ],
                "💰 Investor relations": [
                    "Build a simple investor update template highlighting key metrics",
                    "Identify 10-15 potential angels or micro-VCs aligned with your vision",
                    "Create a basic pitch deck focused on traction and capital efficiency"
                ],
                "🛠 Optimizing based on customer feedback": [
                    "Implement a simple feedback collection system",
                    "Identify the top 3 points of friction in your current experience",
                    "Create a weekly iteration schedule focused on quick wins"
                ],
                "🔥 Sustaining press & industry visibility": [
                    "Develop a simple PR calendar with monthly goals",
                    "Create a content repurposing system to maximize reach",
                    "Join 3-5 communities where your audience gathers"
                ]
            }
        }
    }
    
    # Try to get next steps with emoji first
    try:
        return emoji_next_steps[funding_status][audience_readiness][post_launch_priority]
    except KeyError:
        pass
    
    # Default next steps as fallback
    fallback_next_steps = [
        "Document what worked and what didn't in your launch",
        "Focus on optimizing your best-performing channel",
        "Create a 30-day action plan based on initial results"
    ]
    
    return fallback_next_steps