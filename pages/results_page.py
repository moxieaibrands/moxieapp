import streamlit as st
from utils.email_sender import send_email_to_user as send_email
from utils.competitive_analysis import display_competitive_analysis
from utils.ui_components import pricing_section, display_user_responses_summary
from utils.state_management import reset_form

def display_results():
    """Display the launch plan results page"""
    try:
        plan = st.session_state.generated_plan
        
        if not plan:
            st.error("Something went wrong. Please try again.")
            if st.button("Start Over"):
                reset_form()
            return
        
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-header">', unsafe_allow_html=True)
        st.markdown(f'<h2>Your Launch Plan, {plan.get("first_name", "")}</h2>', unsafe_allow_html=True)
        st.markdown('<span class="ready-badge">Ready to Launch</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Summary box
        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
        
        # Safely access nested dictionaries with get() and provide fallbacks
        launch_type = "Launch"
        funding_status = "Startup"
        
        if "launch_summary" in plan:
            launch_type = plan["launch_summary"].get("launch_type", launch_type)
            funding_status = plan["launch_summary"].get("funding_status", funding_status)
        elif "launch_type" in plan:
            # Direct access if not nested in launch_summary
            launch_type = plan.get("launch_type", launch_type)
        
        if "funding_status" in plan:
            # Direct access if not nested in launch_summary
            funding_status = plan.get("funding_status", funding_status)
        
        st.markdown(f'<p style="font-weight: 500;">{funding_status}</p>', unsafe_allow_html=True)
        st.markdown(f'<p>Launch Type: <strong>{launch_type}</strong></p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Strategies section
        st.markdown("<h3>Your Launch Strategies</h3>", unsafe_allow_html=True)
        
        # Safely get strategies or use fallback
        strategies = []
        if "strategies" in plan:
            strategies = plan.get("strategies", [])
        elif "recommended_strategies" in plan:
            strategies = plan.get("recommended_strategies", [])
        
        if strategies:
            for i, strategy in enumerate(strategies[:5]):  # Limit to 5 strategies
                st.markdown('<div class="strategy-item">', unsafe_allow_html=True)
                st.markdown(f'<div class="strategy-number">{i+1}</div>', unsafe_allow_html=True)
                
                # Handle both string and dictionary formats for strategies
                if isinstance(strategy, dict):
                    st.markdown(f"<p><strong>{strategy.get('title', 'Strategy')}</strong></p>", unsafe_allow_html=True)
                    st.markdown(f"<p>{strategy.get('description', '')}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p>{strategy}</p>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No specific strategies were generated. Try adjusting your inputs and generating a new plan.")
        
        # Next steps section
        st.markdown("<h3>Immediate Next Steps</h3>", unsafe_allow_html=True)
        
        # Safely get next steps or use fallback
        next_steps = []
        if "next_steps" in plan:
            next_steps = plan.get("next_steps", [])
        
        if next_steps:
            for i, step in enumerate(next_steps[:3]):  # Limit to 3 next steps
                st.markdown('<div class="strategy-item">', unsafe_allow_html=True)
                st.markdown(f'<div class="next-step-number">{i+1}</div>', unsafe_allow_html=True)
                
                # Handle both string and dictionary formats for next steps
                if isinstance(step, dict):
                    st.markdown(f"<p><strong>{step.get('title', 'Next Step')}</strong></p>", unsafe_allow_html=True)
                    st.markdown(f"<p>{step.get('description', '')}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p>{step}</p>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No specific next steps were generated. Try adjusting your inputs and generating a new plan.")
        
        # Competitive analysis section (if selected industry)
        industry = None
        if "form_data" in st.session_state and "industry" in st.session_state.form_data:
            industry = st.session_state.form_data.get("industry")
        
        if industry:
            display_competitive_analysis(industry)
        
        # Show user responses
        if "form_data" in st.session_state:
            display_user_responses_summary(st.session_state.form_data)
        
        # Email and calendar options
        st.markdown("<h3>Save Your Plan</h3>", unsafe_allow_html=True)
        
        email = ""
        if "form_data" in st.session_state and "email" in st.session_state.form_data:
            email = st.session_state.form_data.get("email", "")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if not st.session_state.get("email_sent", False):
                if st.button("Email My Plan", use_container_width=True):
                    if email:
                        # Send email - using the proper function
                        success = send_email(email, plan)
                        if success:
                            st.session_state.email_sent = True
                            st.success("Plan sent to your email!")
                            st.rerun()
                        else:
                            st.error("Failed to send email. Please try again.")
                    else:
                        st.error("No email address provided.")
            else:
                st.success("Plan sent to your email!")
        
        with col2:
            if st.button("Schedule in Calendar", use_container_width=True):
                st.session_state.show_calendar = True
                st.rerun()
        
        # Pricing section
        st.markdown("<h3>Get Additional Support</h3>", unsafe_allow_html=True)
        pricing_section()
        
        # Action buttons
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Start Over", use_container_width=True):
                reset_form()
        
        with col2:
            # Export button as link (placeholder)
            st.markdown('<a href="#" class="export-button">Export as PDF</a>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred while displaying results: {str(e)}")
        if st.button("Start Over"):
            reset_form()



            