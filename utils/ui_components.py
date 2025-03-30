import streamlit as st

def option_selector(options, key_prefix, selected_option=None, with_info=False):
    """
    Create a custom radio-button like selector using native radio buttons
    
    Args:
        options (list): List of option labels
        key_prefix (str): Prefix for the key to make it unique
        selected_option (str, optional): Currently selected option
        with_info (bool): Whether this option will show an info box
    
    Returns:
        str: The selected option
    """
    # Find index of selected option
    index = 0
    if selected_option in options:
        index = options.index(selected_option)
    
    # Use native radio buttons with visible labels
    selected = st.radio(
        "",  # Empty label
        options,
        index=index,
        key=f"{key_prefix}_radio",
        label_visibility="collapsed"  # Hide the main label
    )
    
    # Show info box if option is selected and with_info is True
    if with_info and selected:
        display_info_for_option(selected)
    
    return selected

def display_info_for_option(option):
    """Display contextual information based on the selected option"""
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    
    # Launch Type info
    if "New Startup/Product Launch" in option:
        st.markdown(
            'Your first launch moment needs to be more than an announcement. '
            'It\'s a story. Why did you build this? What\'s the problem it solves? '
            'Who will this change everything for?'
        )
    elif "Brand Repositioning" in option:
        st.markdown(
            'Rebrands fail when people don\'t get why they\'re happening. '
            'Your job is to control the narrative. Is this a bold evolution? A course correction? '
            'A category-defining move?'
        )
    elif "Funding Announcement" in option:
        st.markdown(
            'Raising capital isn\'t just a financial win—it\'s a moment that builds '
            'credibility. But investors don\'t just bet on your idea—they bet on momentum.'
        )
    elif "Partnership" in option:
        st.markdown(
            'If you\'re making a big move, the world needs to see it. Partnerships, '
            'media coverage, and collaborations only work when the story is compelling and shareable.'
        )
    
    # Primary Goal info
    elif "Get Users or Customers" in option:
        st.markdown(
            'A great product doesn\'t sell itself. Your job is to make people '
            'see themselves in your story and feel like this is the solution '
            'they\'ve been waiting for.'
        )
    elif "Attract Investors" in option:
        st.markdown(
            'Investors don\'t fund ideas—they fund traction & narrative '
            'control. Your launch isn\'t just about raising money, it\'s about '
            'shaping perception.'
        )
    elif "Build Press & Awareness" in option:
        st.markdown(
            'Press doesn\'t just come to you—you have to make them want to '
            'cover you. The most successful PR strategies are built on story-driven '
            'angles that journalists need to write about.'
        )
    elif "Create Industry Influence" in option:
        st.markdown(
            'People don\'t just want products—they want movements. To become '
            'an industry leader, your launch needs to position you as a must-follow '
            'voice.'
        )
    
    # Audience info
    elif "Yes, we have an engaged community" in option:
        st.markdown(
            'Great. Your job isn\'t just to maintain them—it\'s to activate '
            'them. Your existing audience is your biggest launch asset.'
        )
    elif "small following" in option:
        st.markdown(
            'Perfect. This means your audience is real—but you need wider '
            'visibility. You don\'t need a big audience—you need a targeted, engaged one.'
        )
    elif "starting from scratch" in option:
        st.markdown(
            'No problem. The best way to build an audience is to leverage '
            'existing ones. Instead of grinding to build your own, let\'s shortcut the process.'
        )
    
    # Post-launch info
    elif "Scaling & repeatable traction" in option:
        st.markdown(
            'The best post-launch strategies are repeatable. '
            'You need to figure out what worked, scale it, and automate it.'
        )
    elif "Investor relations" in option:
        st.markdown(
            'Your investors need to see a clear, momentum-driven path. '
            'Your updates should highlight efficiency, customer love, and strategic moves.'
        )
    elif "Optimizing based on customer feedback" in option:
        st.markdown(
            'Your launch was the start. Now it\'s time to listen. The '
            'fastest-growing startups iterate aggressively.'
        )
    elif "Sustaining press" in option:
        st.markdown(
            'You made noise—now keep it going. If you had media coverage or '
            'early traction, your job is to stay relevant.'
        )
    else:
        st.markdown("Select an option to learn more.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def step_navigation(back=True, next_label="Next →", next_disabled=True, on_next=None):
    """
    Create consistent navigation buttons with Back under Next
    
    Args:
        back (bool): Whether to show back button
        next_label (str): Label for the next button
        next_disabled (bool): Whether next button should be disabled
        on_next (function, optional): Function to call on next
    """
    # Create Next button - full width
    if st.button(next_label, disabled=next_disabled, key="next_button", use_container_width=True):
        if on_next:
            on_next()
        else:
            st.session_state.step += 1
            st.experimental_rerun()
    
    # Create Back button below (if needed) - full width
    if back:
        if st.button("← Back", key="back_button", use_container_width=True):
            st.session_state.step -= 1
            st.experimental_rerun()

def step_card(title, content_func):
    """
    Create a styled step card with consistent formatting
    
    Args:
        title (str): Title of the step
        content_func (function): Function that contains the step content
    """
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="step-title">{title}</div>', unsafe_allow_html=True)
    
    # Call the content function
    content_func()
    
    st.markdown('</div>', unsafe_allow_html=True)

def pricing_section():
    """Display the pricing options grid"""
    st.markdown('<div class="pricing-grid">', unsafe_allow_html=True)
    
    # DIY Option
    st.markdown(
        '<div class="pricing-card">'
        '<p class="pricing-title">DIY</p>'
        '<p class="pricing-price">$29/month</p>'
        '<p class="pricing-description">Weekly roadmap</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Coaching Option (highlighted)
    st.markdown(
        '<div class="pricing-card highlighted">'
        '<p class="pricing-title">Coaching</p>'
        '<p class="pricing-price">$500/month</p>'
        '<p class="pricing-description">Direct guidance</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Full-Service Option
    st.markdown(
        '<div class="pricing-card">'
        '<p class="pricing-title">Full-Service</p>'
        '<p class="pricing-price">$5K</p>'
        '<p class="pricing-description">We run it for you</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

def info_box(text):
    """Display a consistent info box"""
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown('</div>', unsafe_allow_html=True)

def display_user_responses_summary(form_data):
    """
    Display a summary of all user responses
    
    Args:
        form_data (dict): User's form data containing all responses
    """
    st.markdown('<h3 style="font-weight: 600; margin-bottom: 0.5rem; margin-top: 1.5rem;">Your Responses</h3>', unsafe_allow_html=True)
    
    # Create an expandable section with all responses
    with st.expander("View all your responses", expanded=False):
        st.markdown("### Messaging Validation")
        st.markdown(f"**Your response:** {form_data['messaging_tested']}")
        
        st.markdown("### Launch Type")
        st.markdown(f"**Your response:** {form_data['launch_type']}")
        
        st.markdown("### Funding Status")
        st.markdown(f"**Your response:** {form_data['funding_status']}")
        
        st.markdown("### Primary Goal")
        st.markdown(f"**Your response:** {form_data['primary_goal']}")
        
        st.markdown("### Audience Readiness")
        st.markdown(f"**Your response:** {form_data['audience_readiness']}")
        
        st.markdown("### Post-Launch Priority")
        st.markdown(f"**Your response:** {form_data['post_launch_priority']}")