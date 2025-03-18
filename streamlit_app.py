import streamlit as st
import json
import os
import pandas as pd
import base64
from datetime import datetime
from utils.email_sender import send_email_to_user
from utils.plan_generator import generate_launch_plan
from utils.ui_components import (
    option_selector, step_navigation, step_card, 
    pricing_section, info_box
)

# Set page configuration
st.set_page_config(
    page_title="Moxie High-Impact Launch Assistant",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for improved styling matching the React UI example
st.markdown("""
<style>
    /* Main container styling */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF5A5F;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Step card styling */
    .step-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #FF5A5F;
    }
    
    .step-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    /* Info box styling */
    .info-box {
        background-color: #FFF7ED;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Option styling */
    .radio-option {
        padding: 0.75rem;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
    }
            




   
            
            
            
    

    









            
    
    .radio-option:hover {
        border-color: #FF5A5F;
        background-color: #FFF7ED;
    }
    
    .radio-option.selected {
        border-color: #FF5A5F;
        background-color: #FFF7ED;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #FF5A5F;
        color: white;
        border-radius: 9999px;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #FF7A7F;
    }
    
    /* Result card styling */
    .result-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
    
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .ready-badge {
        background-color: #DEF7EC;
        color: #03543E;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
    }
    
    .summary-box {
        background-color: #FFF7ED;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .strategy-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 0.75rem;
    }
    
    .strategy-number {
        background-color: #FEE2E2;
        color: #9B1C1C;
        height: 1.5rem;
        width: 1.5rem;
        border-radius: 9999px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.5rem;
        flex-shrink: 0;
        font-size: 0.875rem;
    }
    
    .next-step-number {
        background-color: #DBEAFE;
        color: #1E40AF;
        height: 1.5rem;
        width: 1.5rem;
        border-radius: 9999px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.5rem;
        flex-shrink: 0;
        font-size: 0.875rem;
    }
    
    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .pricing-card {
        padding: 0.75rem;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        text-align: center;
    }
    
    .pricing-card.highlighted {
        border-color: #FF5A5F;
        background-color: #FFF7ED;
    }
    
    .pricing-title {
        font-weight: 600;
    }
    
    .pricing-price {
        font-size: 1.25rem;
        font-weight: 700;
        color: #FF5A5F;
    }
    
    .pricing-description {
        font-size: 0.875rem;
        color: #6B7280;
    }
    
    .action-buttons {
        display: flex;
        gap: 0.75rem;
    }
    
    .email-button {
        flex: 1;
        background-color: #FF5A5F;
        color: white;
        border-radius: 9999px;
        padding: 0.5rem;
        font-weight: 500;
        text-align: center;
        cursor: pointer;
    }
    
    .reset-button {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 9999px;
        padding: 0.5rem 1rem;
        cursor: pointer;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: #FF5A5F;
    }
    
    /* Remove default Streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .pricing-grid {
            grid-template-columns: 1fr;
        }
        
        .action-buttons {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# Load strategies from JSON file if it exists
def load_strategies():
    try:
        if os.path.exists("data/strategies.json"):
            with open("data/strategies.json", "r") as f:
                return json.load(f)
        # If file doesn't exist, return None
        return None
    except Exception as e:
        st.error(f"Error loading strategies: {e}")
        return None

# Initialize session state for multi-step form
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'first_name': '',
        'startup_name': '',
        'messaging_tested': None,
        'launch_type': None,
        'funding_status': None,
        'primary_goal': None,
        'audience_readiness': None,
        'post_launch_priority': None,
        'email': ''
    }

if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = None
    
if 'email_sent' not in st.session_state:
    st.session_state.email_sent = False

# Main app UI
def main():
    # Try to load logo from assets directory
    # In your main() function, replace the current logo loading code with this:
    try:
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                    <img src="data:image/png;base64,{base64.b64encode(open(logo_path, 'rb').read()).decode()}" 
                        style="width: 150px; height: auto;" />
                </div>
                """, 
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"Error loading logo: {e}")
        pass
    
    # Header
    st.markdown('<div class="main-header">Moxie High-Impact Launch Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Created for founders who refuse to be ignored. Get your personalized launch plan in 3 minutes.</div>', unsafe_allow_html=True)
    
    # Progress bar (only show if not on results page)
    if st.session_state.generated_plan is None and 1 <= st.session_state.step <= 7:
        progress = (st.session_state.step - 1) / 6  # 6 steps total, not counting final step
        st.progress(progress)
        st.markdown(f"**Step {st.session_state.step}/7**")
    
    # Multi-step form
    if st.session_state.generated_plan is not None:
        display_results()
    elif st.session_state.step == 1:
        step_1()
    elif st.session_state.step == 2:
        step_2()
    elif st.session_state.step == 3:
        step_3()
    elif st.session_state.step == 4:
        step_4()
    elif st.session_state.step == 5:
        step_5()
    elif st.session_state.step == 6:
        step_6()
    elif st.session_state.step == 7:
        step_7()

def step_1():
    """Collect basic information"""
    def content():
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", value=st.session_state.form_data['first_name'], 
                                    placeholder="Your first name")
        
        with col2:
            email = st.text_input("Email", value=st.session_state.form_data['email'],
                                placeholder="your@email.com")
        
        startup_name = st.text_input("Startup Name", value=st.session_state.form_data['startup_name'],
                                   placeholder="Your startup's name")
        
        next_disabled = not first_name or not email or not startup_name
        
        def on_next():
            # Validate inputs
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email address.")
                return
                
            st.session_state.form_data['first_name'] = first_name
            st.session_state.form_data['startup_name'] = startup_name
            st.session_state.form_data['email'] = email
            st.session_state.step += 1
            st.experimental_rerun()
        
        step_navigation(back=False, next_disabled=next_disabled, on_next=on_next)
    
    step_card("Step 1: Let's get to know you", content)

def step_2():
    """Ask about messaging testing"""
    def content():
        info_box("Before we dive in, have you tested your messaging with real customers?")
        
        options = [
            "✅ Yes, I've gotten direct feedback on my messaging",
            "🤔 Sort of... I've talked to people, but nothing structured",
            "❌ No, I haven't tested it yet"
        ]
        
        selected = option_selector(options, "messaging", st.session_state.form_data['messaging_tested'])
        
        def on_next():
            st.session_state.form_data['messaging_tested'] = selected
            st.session_state.step += 1
            st.experimental_rerun()
            
        step_navigation(next_disabled=not selected, on_next=on_next)
    
    step_card("Step 2: Messaging Validation", content)

def step_3():
    """Ask about launch type"""
    def content():
        options = [
            "🚀 New Startup/Product Launch",
            "🔄 Brand Repositioning (Rebrand or Pivot)",
            "💰 Funding Announcement",
            "📢 Major Partnership or Publicity Push"
        ]
        
        selected = option_selector(
            options, 
            "launch", 
            st.session_state.form_data['launch_type'],
            with_info=True
        )
        
        def on_next():
            st.session_state.form_data['launch_type'] = selected
            st.session_state.step += 1
            st.experimental_rerun()
            
        step_navigation(next_disabled=not selected, on_next=on_next)
    
    step_card("Step 3: What kind of launch are you preparing for?", content)

def step_4():
    """Ask about funding status"""
    def content():
        info_box("Where are you financially right now?")
        
        options = [
            "🚀 Bootstrapping (No external funding, self-funded)",
            "🌱 Raised under $1M (Likely still raising, early-stage)",
            "📈 Raised $1M-$3M (Have 12-18 months of runway)",
            "🏆 Raised $3M+ (Series A+; established growth strategy)"
        ]
        
        selected = option_selector(options, "funding", st.session_state.form_data['funding_status'])
        
        def on_next():
            st.session_state.form_data['funding_status'] = selected
            st.session_state.step += 1
            st.experimental_rerun()
            
        step_navigation(next_disabled=not selected, on_next=on_next)
    
    step_card("Step 4: Funding Status", content)

def step_5():
    """Ask about primary launch goal"""
    def content():
        options = [
            "🚀 Get Users or Customers",
            "💰 Attract Investors",
            "🎙 Build Press & Awareness",
            "🌎 Create Industry Influence"
        ]
        
        selected = option_selector(
            options, 
            "goal", 
            st.session_state.form_data['primary_goal'],
            with_info=True
        )
        
        def on_next():
            st.session_state.form_data['primary_goal'] = selected
            st.session_state.step += 1
            st.experimental_rerun()
            
        step_navigation(next_disabled=not selected, on_next=on_next)
    
    step_card("Step 5: Primary Launch Goal", content)

def step_6():
    """Ask about audience readiness"""
    def content():
        options = [
            "✅ Yes, we have an engaged community",
            "⚡ We have a small following but need more traction",
            "❌ No, we're starting from scratch"
        ]
        
        selected = option_selector(
            options, 
            "audience", 
            st.session_state.form_data['audience_readiness'],
            with_info=True
        )
        
        def on_next():
            st.session_state.form_data['audience_readiness'] = selected
            st.session_state.step += 1
            st.experimental_rerun()
            
        step_navigation(next_disabled=not selected, on_next=on_next)
    
    step_card("Step 6: Audience Readiness", content)

def step_7():
    """Ask about post-launch priority and generate plan"""
    def content():
        info_box(
            'Most founders think the launch is the moment. '
            'It\'s not. It\'s just the beginning. The question is: How do you sustain attention, turn '
            'interest into conversions, and prove traction?'
        )
        
        options = [
            "📈 Scaling & repeatable traction (growth systems)",
            "💰 Investor relations & positioning for next raise",
            "🛠 Optimizing based on customer feedback",
            "🔥 Sustaining press & industry visibility"
        ]
        
        selected = option_selector(
            options, 
            "priority", 
            st.session_state.form_data['post_launch_priority'],
            with_info=True
        )
        
        def on_generate_plan():
            st.session_state.form_data['post_launch_priority'] = selected
            
            # Generate plan
            with st.spinner("Creating your personalized launch plan..."):
                external_strategies = load_strategies()
                st.session_state.generated_plan = generate_launch_plan(
                    st.session_state.form_data, 
                    external_strategies
                )
            st.experimental_rerun()
            
        step_navigation(
            next_label="Generate My Launch Plan", 
            next_disabled=not selected, 
            on_next=on_generate_plan
        )
    
    step_card("Step 7: Post-Launch Priority", content)

def display_results():
    """Display generated plan and offer email sending"""
    plan = st.session_state.generated_plan
    
    if not plan:
        st.error("Something went wrong. Please try again.")
        if st.button("Start Over"):
            reset_form()
        return
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-header">', unsafe_allow_html=True)
    st.markdown('<h2>Your High-Impact Launch Plan</h2>', unsafe_allow_html=True)
    st.markdown('<div class="ready-badge">Ready</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display summary box
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p style="color: #6B7280; font-size: 0.875rem;">Startup</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-weight: 500;">{plan["startup_name"]}</p>', unsafe_allow_html=True)
        
        st.markdown('<p style="color: #6B7280; font-size: 0.875rem;">Funding Status</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-weight: 500;">{plan["launch_summary"]["funding_status"]}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p style="color: #6B7280; font-size: 0.875rem;">Launch Type</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-weight: 500;">{plan["launch_summary"]["launch_type"]}</p>', unsafe_allow_html=True)
        
        st.markdown('<p style="color: #6B7280; font-size: 0.875rem;">Primary Goal</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-weight: 500;">{plan["launch_summary"]["primary_goal"]}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Messaging advice
    st.markdown(f"**{plan['messaging_advice']}**")
    
    # Display recommended strategies
    st.markdown('<h3 style="font-weight: 600; margin-bottom: 0.5rem;">Recommended Strategies:</h3>', unsafe_allow_html=True)
    for i, strategy in enumerate(plan['recommended_strategies']):
        st.markdown(
            f'<div class="strategy-item">'
            f'<div class="strategy-number">{i+1}</div>'
            f'<span>{strategy}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Display next steps
    st.markdown('<h3 style="font-weight: 600; margin-bottom: 0.5rem; margin-top: 1.5rem;">Next Steps:</h3>', unsafe_allow_html=True)
    for i, step in enumerate(plan['next_steps']):
        st.markdown(
            f'<div class="strategy-item">'
            f'<div class="next-step-number">{i+1}</div>'
            f'<span>{step}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Display pricing options
    st.markdown('<div style="border-top: 1px solid #E5E7EB; margin-top: 1.5rem; padding-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<h3 style="font-weight: 600; margin-bottom: 0.75rem;">Ready to execute?</h3>', unsafe_allow_html=True)
    
    pricing_section()
    
    # Email and reset buttons
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.button("📧 " + ("Email Sent!" if st.session_state.email_sent else "Send to My Email")):
            with st.spinner("Sending email..."):
                success = send_email_to_user(st.session_state.form_data['email'], plan)
                if success:
                    st.success(f"Your personalized launch plan has been sent to {st.session_state.form_data['email']}!")
                    st.session_state.email_sent = True
                    st.experimental_rerun()
                else:
                    st.error("There was an error sending your email. Please try again.")
    
    with col2:
        if st.button("Reset"):
            reset_form()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close result-card div

def reset_form():
    """Reset the form to start over"""
    st.session_state.form_data = {
        'first_name': '',
        'startup_name': '',
        'messaging_tested': None,
        'launch_type': None,
        'funding_status': None,
        'primary_goal': None,
        'audience_readiness': None,
        'post_launch_priority': None,
        'email': ''
    }
    st.session_state.generated_plan = None
    st.session_state.email_sent = False
    st.session_state.step = 1
    st.experimental_rerun()

# App run entry point
if __name__ == "__main__":
    main()

    