import streamlit as st
from utils.ui_components import option_selector, step_navigation, step_card, info_box
from utils.competitive_analysis import get_industries
from utils.plan_generator import generate_launch_plan
from utils.state_management import reset_form
from utils.data_loader import load_strategies

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
            st.rerun()
        
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
            st.rerun()
            
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
            st.rerun()
            
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
            st.rerun()
            
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
            st.rerun()
            
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
            st.rerun()
            
        step_navigation(next_disabled=not selected, on_next=on_next)
    
    step_card("Step 6: Audience Readiness", content)

def step_7():
    """Ask about post-launch priority"""
    def content():
        info_box(
            'The launch itself is just day one of your journey. Your success will depend on '
            'what you do after the initial excitement fades. Select your primary focus for '
            'the post-launch phase to maximize your momentum and impact.'
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
        
        def on_next():
            st.session_state.form_data['post_launch_priority'] = selected
            st.session_state.step += 1
            st.rerun()
            
        step_navigation(next_disabled=not selected, on_next=on_next)
    
    step_card("Step 7: Post-Launch Priority", content)

def step_8():
    """Ask about industry for competitive analysis"""
    def content():
        info_box(
            'Understanding how similar companies launched can provide valuable insights. '
            'Select your industry to see examples of successful launches from companies like yours.'
        )
        
        # Get available industries
        industries = get_industries()
        
        # Create options with emojis
        industry_emojis = {
            "SaaS": "💻",
            "D2C / E-commerce": "🛒",
            "Fintech": "💰",
            "Healthcare": "🏥",
            "Enterprise Software": "🏢",
            "AI/ML": "🤖",
            "Service": "🛎️",
            "Other": "🔍"  # Added "Other" option with magnifying glass emoji
        }
        
        options = []
        for industry in industries:
            emoji = industry_emojis.get(industry, "🔍")
            options.append(f"{emoji} {industry}")
        
        # Add "Other" option at the end
        options.append(f"{industry_emojis['Other']} Other")
        
        selected = option_selector(options, "industry", st.session_state.form_data['industry'])
        
        # Add text input for "Other" industry if selected
        other_industry = None
        if selected and "Other" in selected:
            other_industry = st.text_input("Please specify your industry:", key="other_industry_input")
        
        def on_next():
            # Extract industry name without emoji
            if selected:
                if "Other" in selected and other_industry:
                    # Use the user's custom industry input
                    st.session_state.form_data['industry'] = other_industry
                else:
                    # Use the selected predefined industry (remove emoji)
                    industry = selected.split(" ", 1)[1] if " " in selected else selected
                    st.session_state.form_data['industry'] = industry
            else:
                st.session_state.form_data['industry'] = None
                
            st.session_state.step += 1
            st.rerun()  # Changed from st.experimental_rerun() to st.rerun()
        
        # Next button should be disabled if "Other" is selected but no text is entered
        next_is_disabled = not selected or ("Other" in selected and not other_industry)
            
        step_navigation(next_disabled=next_is_disabled, on_next=on_next)
    
    step_card("Step 8: Your Industry", content)


def step_9():
    """Generate plan and schedule milestones"""
    def content():
        info_box(
            'A successful launch requires careful planning and scheduling. '
            'Would you like us to create a suggested launch timeline with key milestones for your calendar?'
        )
        
        options = [
            "✅ Yes, help me plan my launch timeline",
            "⏭️ Skip calendar scheduling for now"
        ]
        
        selected = option_selector(options, "calendar", None)
        
        def on_generate_plan():
            # Generate plan
            with st.spinner("Creating your personalized launch plan..."):
                # Import EngageBay integration
                from utils.engagebay_integration import send_to_engagebay
                
                # Load strategies from the utility function
                external_strategies = load_strategies()
                st.session_state.generated_plan = generate_launch_plan(
                    st.session_state.form_data, 
                    external_strategies
                )
                
                # Send contact info to EngageBay
                first_name = st.session_state.form_data.get('first_name', '')
                email = st.session_state.form_data.get('email', '')
                
                if email:
                    # Send to EngageBay in the background
                    send_to_engagebay(first_name, email)
                
                # Set calendar preference
                if selected == "✅ Yes, help me plan my launch timeline":
                    st.session_state.show_calendar = True
                else:
                    st.session_state.show_calendar = False
                    
            st.rerun()
            
        step_navigation(
            next_label="Generate My Launch Plan", 
            next_disabled=not selected, 
            on_next=on_generate_plan
        )
    
    step_card("Step 9: Launch Timeline", content)