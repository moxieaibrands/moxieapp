import streamlit as st
import datetime
import uuid
import json
import os
import calendar

# Dictionary to store milestone data (in a production app, this would be a database)
MILESTONE_DATA_PATH = "data/milestones.json"

def load_milestones():
    """Load saved milestones from JSON file"""
    if os.path.exists(MILESTONE_DATA_PATH):
        try:
            with open(MILESTONE_DATA_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading milestones: {e}")
    return {}

def save_milestones(milestones_data):
    """Save milestones to JSON file"""
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(MILESTONE_DATA_PATH), exist_ok=True)
        
        with open(MILESTONE_DATA_PATH, "w") as f:
            json.dump(milestones_data, f)
        return True
    except Exception as e:
        st.error(f"Error saving milestones: {e}")
        return False

def add_milestone(user_email, milestone_name, milestone_date, milestone_description, milestone_type="launch"):
    """Add a new milestone to the user's calendar"""
    # Load existing milestones
    milestones = load_milestones()
    
    # Create user entry if it doesn't exist
    if user_email not in milestones:
        milestones[user_email] = []
    
    # Check for duplicates before adding
    formatted_date = milestone_date.strftime("%Y-%m-%d") if isinstance(milestone_date, datetime.date) else milestone_date
    for existing in milestones[user_email]:
        if (existing["name"] == milestone_name and 
            existing["date"] == formatted_date and
            existing["description"] == milestone_description):
            # This is a duplicate, don't add it
            return True, existing["id"]
    
    # Create milestone object
    milestone_id = str(uuid.uuid4())
    milestone = {
        "id": milestone_id,
        "name": milestone_name,
        "date": formatted_date if isinstance(formatted_date, str) else milestone_date.strftime("%Y-%m-%d"),
        "description": milestone_description,
        "type": milestone_type,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to user's milestones
    milestones[user_email].append(milestone)
    
    # Save updated milestones
    success = save_milestones(milestones)
    
    return success, milestone_id

def reset_user_milestones(user_email):
    """Clear all milestones for a specific user"""
    milestones = load_milestones()
    
    if user_email in milestones:
        milestones[user_email] = []
        return save_milestones(milestones)
    
    return True

def get_user_milestones(user_email):
    """Get all milestones for a specific user"""
    milestones = load_milestones()
    return milestones.get(user_email, [])

def delete_milestone(user_email, milestone_id):
    """Delete a specific milestone"""
    milestones = load_milestones()
    
    if user_email in milestones:
        # Filter out the milestone to delete
        milestones[user_email] = [m for m in milestones[user_email] if m["id"] != milestone_id]
        return save_milestones(milestones)
    
    return False

def generate_google_calendar_link(user_email, milestone_id=None):
    """
    Generate a Google Calendar URL for adding events
    
    Args:
        user_email (str): User's email
        milestone_id (str, optional): Specific milestone ID
        
    Returns:
        str: Google Calendar URL
    """
    from datetime import datetime, timedelta
    import urllib.parse
    
    # Get user milestones
    milestones = get_user_milestones(user_email)
    
    if milestone_id:
        # Export a specific milestone
        milestone = next((m for m in milestones if m["id"] == milestone_id), None)
        if milestone:
            # Format for Google Calendar
            title = milestone["name"]
            # Format date properly for Google Calendar (YYYYMMDD)
            start_date = milestone["date"].replace("-", "")
            # For all-day events, Google Calendar expects the end date to be the next day
            date_obj = datetime.strptime(milestone["date"], "%Y-%m-%d")
            next_day = date_obj + timedelta(days=1)
            end_date = next_day.strftime("%Y%m%d")
            
            details = milestone["description"]
            
            # Create Google Calendar link with proper URL encoding
            google_link = (
                f"https://calendar.google.com/calendar/render?"
                f"action=TEMPLATE&text={urllib.parse.quote(title)}"
                f"&dates={start_date}/{end_date}"
                f"&details={urllib.parse.quote(details)}"
                f"&sf=true&output=xml"
            )
            
            return google_link
    
    # For all milestones - limit to the first few to avoid URL length issues
    if milestones:
        # Sort milestones by date
        sorted_milestones = sorted(milestones, key=lambda x: x["date"])
        
        # Google Calendar doesn't handle multiple events well in one URL
        # Instead, let's create a link for the first event that should work reliably
        milestone = sorted_milestones[0]
        
        title = milestone["name"]
        start_date = milestone["date"].replace("-", "")
        date_obj = datetime.strptime(milestone["date"], "%Y-%m-%d")
        next_day = date_obj + timedelta(days=1)
        end_date = next_day.strftime("%Y%m%d")
        
        details = (f"{milestone['description']} - This is the first of {len(sorted_milestones)} "
                  f"milestones in your launch plan. Type: {milestone['type']}")
        
        google_link = (
            f"https://calendar.google.com/calendar/render?"
            f"action=TEMPLATE&text={urllib.parse.quote(title)}"
            f"&dates={start_date}/{end_date}"
            f"&details={urllib.parse.quote(details)}"
            f"&sf=true&output=xml"
        )
        
        return google_link
    
    # Default Google Calendar link if no milestones
    return "https://calendar.google.com"

def create_suggested_milestones(launch_plan, user_email):
    """
    Create suggested milestones based on the launch plan
    
    Args:
        launch_plan (dict): The generated launch plan
        user_email (str): User's email
        
    Returns:
        list: List of suggested milestone dicts
    """
    # Get launch type and funding status with fallbacks
    launch_type = "New Startup/Product Launch"
    funding_status = "Bootstrapping (No external funding, self-funded)"
    
    # Safely access keys that might not exist
    if "launch_summary" in launch_plan:
        launch_type = launch_plan["launch_summary"].get("launch_type", launch_type)
        funding_status = launch_plan["launch_summary"].get("funding_status", funding_status)
    elif "launch_type" in launch_plan:
        # Direct access if not nested in launch_summary
        launch_type = launch_plan.get("launch_type", launch_type)
    
    if "funding_status" in launch_plan:
        # Direct access if not nested in launch_summary
        funding_status = launch_plan.get("funding_status", funding_status)
    
    # Base date is today
    today = datetime.date.today()
    
    # Create different timeline based on funding status
    if "Bootstrapping" in funding_status:
        # Shorter timeline for bootstrapped companies (8 weeks)
        pre_launch_weeks = 4
        launch_day = today + datetime.timedelta(weeks=pre_launch_weeks)
        post_launch_weeks = 4
    elif "under $1M" in funding_status:
        # Medium timeline (10 weeks)
        pre_launch_weeks = 5
        launch_day = today + datetime.timedelta(weeks=pre_launch_weeks)
        post_launch_weeks = 5
    else:
        # Longer timeline for well-funded companies (12 weeks)
        pre_launch_weeks = 6
        launch_day = today + datetime.timedelta(weeks=pre_launch_weeks)
        post_launch_weeks = 6
    
    # Create a list of suggested milestones
    suggested_milestones = [
        {
            "name": "Messaging Validation Complete",
            "date": today + datetime.timedelta(weeks=1),
            "description": "Complete customer interviews and messaging validation",
            "type": "pre-launch"
        },
        {
            "name": "Content Creation Deadline",
            "date": today + datetime.timedelta(weeks=pre_launch_weeks-2),
            "description": "Finalize all launch content, including website, social media posts, and press materials",
            "type": "pre-launch"
        },
        {
            "name": "Launch Day",
            "date": launch_day,
            "description": f"Official {launch_type.strip('🔄 🚀 💰 📢')} launch date",
            "type": "launch"
        },
        {
            "name": "Post-Launch Analysis",
            "date": launch_day + datetime.timedelta(weeks=1),
            "description": "Analyze initial launch metrics and adjust strategy",
            "type": "post-launch"
        },
        {
            "name": "Growth Strategy Implementation",
            "date": launch_day + datetime.timedelta(weeks=post_launch_weeks),
            "description": "Implement ongoing growth strategy based on launch results",
            "type": "post-launch"
        }
    ]
    
    # Add launch type specific milestones
    if "New Startup/Product Launch" in launch_type:
        suggested_milestones.append({
            "name": "Beta User Feedback Session",
            "date": today + datetime.timedelta(weeks=2),
            "description": "Collect feedback from beta users to refine product",
            "type": "pre-launch"
        })
    elif "Brand Repositioning" in launch_type:
        suggested_milestones.append({
            "name": "Stakeholder Communication",
            "date": today + datetime.timedelta(weeks=2),
            "description": "Communicate rebranding to key stakeholders and team",
            "type": "pre-launch"
        })
    elif "Funding Announcement" in launch_type:
        suggested_milestones.append({
            "name": "Investor Relations Setup",
            "date": today + datetime.timedelta(weeks=2),
            "description": "Prepare investor relations materials and communications",
            "type": "pre-launch"
        })
    elif "Partnership" in launch_type:
        suggested_milestones.append({
            "name": "Partner Coordination Meeting",
            "date": today + datetime.timedelta(weeks=2),
            "description": "Coordinate launch activities with partnership team",
            "type": "pre-launch"
        })
    
    # Format dates as strings for display
    for milestone in suggested_milestones:
        milestone["date"] = milestone["date"].strftime("%Y-%m-%d")
    
    return suggested_milestones

def remove_duplicate_milestones(user_email):
    """
    Remove duplicate milestones for a user by comparing name, date and description
    
    Args:
        user_email (str): User's email
        
    Returns:
        int: Number of duplicates removed
    """
    milestones = load_milestones()
    
    if user_email not in milestones:
        return 0
    
    user_milestones = milestones[user_email]
    unique_milestones = []
    seen = set()
    duplicates_removed = 0
    
    for milestone in user_milestones:
        # Create a unique key for each milestone
        key = (milestone["name"], milestone["date"], milestone["description"])
        
        if key not in seen:
            seen.add(key)
            unique_milestones.append(milestone)
        else:
            duplicates_removed += 1
    
    if duplicates_removed > 0:
        milestones[user_email] = unique_milestones
        save_milestones(milestones)
    
    return duplicates_removed

def display_improved_timeline(milestones, deletable=False, user_email=None):
    """
    Display an improved timeline visualization of milestones
    
    Args:
        milestones (list): List of milestone dictionaries
        deletable (bool): Whether to show delete checkboxes
        user_email (str, optional): User's email for calendar links
    """
    # Sort milestones by date
    import datetime
    
    sorted_milestones = sorted(milestones, key=lambda x: datetime.datetime.strptime(x["date"], "%Y-%m-%d"))
    
    # Group milestones by type
    grouped_milestones = {
        'pre-launch': [],
        'launch': [],
        'post-launch': []
    }
    
    for milestone in sorted_milestones:
        milestone_type = milestone.get("type", "pre-launch")
        if milestone_type in grouped_milestones:
            grouped_milestones[milestone_type].append(milestone)
    
    # Store selected milestones for deletion if in deletable mode
    if deletable and "milestones_to_delete" not in st.session_state:
        st.session_state.milestones_to_delete = []
    
    # Type color mapping
    type_colors = {
        'pre-launch': '#4299E1',  # Blue
        'launch': '#FF5A5F',      # Red
        'post-launch': '#38A169'  # Green
    }
    
    # Type titles
    type_titles = {
        'pre-launch': '🔍 Pre-Launch Phase',
        'launch': '🚀 Launch Phase',
        'post-launch': '📈 Post-Launch Phase'
    }
    
    st.markdown("## Your Launch Timeline")
    
    # Get date range
    if sorted_milestones:
        min_date = datetime.datetime.strptime(sorted_milestones[0]["date"], "%Y-%m-%d")
        max_date = datetime.datetime.strptime(sorted_milestones[-1]["date"], "%Y-%m-%d")
        
        # Add some padding to the timeline
        min_date = min_date - datetime.timedelta(days=7)  # Increased padding
        max_date = max_date + datetime.timedelta(days=7)  # Increased padding
        total_days = (max_date - min_date).days + 1  # Add 1 to avoid division by zero
        
        # Calculate weeks for better labeling
        total_weeks = (total_days // 7) + 1
        
        # Display timeline header with cleaner date format and more space
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 1rem; color: #666; font-weight: 500;">
            <span>{min_date.strftime('%b %d, %Y')}</span>
            <span>{max_date.strftime('%b %d, %Y')}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Create main timeline container
        st.markdown("""
        <div style="position: relative; height: 100px; margin-bottom: 30px; background-color: #f8f9fa; border-radius: 8px; padding: 10px;">
            <div style="position: absolute; top: 50px; left: 0; right: 0; height: 3px; background-color: #E2E8F0;"></div>
        """, unsafe_allow_html=True)
        
        # Group milestones by date to prevent overlap
        date_grouped_milestones = {}
        for milestone in sorted_milestones:
            date = milestone["date"]
            if date not in date_grouped_milestones:
                date_grouped_milestones[date] = []
            date_grouped_milestones[date].append(milestone)
        
        # Add milestone markers - with improved spacing for grouped items
        for date, ms_group in date_grouped_milestones.items():
            milestone_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            position_percent = ((milestone_date - min_date).days / total_days) * 100
            
            # Get the dominant type for this date group
            types = [m.get("type", "pre-launch") for m in ms_group]
            dominant_type = max(set(types), key=types.count)  # Most common type
            
            # Create a larger marker for grouped milestones
            marker_size = min(10 + (len(ms_group) * 2), 18)  # Larger for more milestones, but with a cap
            
            # Only show every other date label to reduce clutter
            show_label = (milestone_date.day % 3 == 0) or len(ms_group) > 1
            
            # Format milestone tooltip
            tooltip_content = "<br>".join([f"{m['name']} ({m['type']})" for m in ms_group])
            
            st.markdown(f"""
            <div style="position: absolute; top: {46 - marker_size/2}px; left: {position_percent}%; 
                        width: {marker_size}px; height: {marker_size}px; 
                        border-radius: 50%; background-color: {type_colors[dominant_type]}; 
                        transform: translateX(-{marker_size/2}px); 
                        box-shadow: 0 1px 3px rgba(0,0,0,0.2); 
                        cursor: pointer; 
                        display: flex; align-items: center; justify-content: center; 
                        color: white; font-weight: bold; font-size: {marker_size/2}px;"
                        title="{tooltip_content}">
                {len(ms_group) if len(ms_group) > 1 else ""}
            </div>
            """, unsafe_allow_html=True)
            
            # Show date labels with improved spacing
            if show_label:
                st.markdown(f"""
                <div style="position: absolute; top: 65px; left: {position_percent}%; 
                            transform: translateX(-50%) rotate(-45deg); 
                            font-size: 0.7rem; white-space: nowrap; 
                            transform-origin: top left; 
                            color: #555; font-weight: 500;">
                    {milestone_date.strftime('%b %d')}
                </div>
                """, unsafe_allow_html=True)
        
        # Close main timeline container
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Create expandable sections for each phase type
    for phase_type in ['pre-launch', 'launch', 'post-launch']:
        if not grouped_milestones[phase_type]:
            continue
            
        with st.expander(f"{type_titles[phase_type]} ({len(grouped_milestones[phase_type])} milestones)", expanded=True):
            # List milestones with cards - improved card design
            for milestone in grouped_milestones[phase_type]:
                milestone_date = datetime.datetime.strptime(milestone["date"], "%Y-%m-%d")
                milestone_id = milestone["id"]
                
                # Create columns with appropriate sizing based on mode
                if deletable:
                    cols = st.columns([0.1, 0.7, 0.2])
                else:
                    cols = st.columns([0.8, 0.2])
                
                # Add checkbox for deletion if in deletable mode
                if deletable:
                    with cols[0]:
                        is_selected = milestone_id in st.session_state.milestones_to_delete
                        if st.checkbox("", value=is_selected, key=f"delete_{milestone_id}"):
                            if milestone_id not in st.session_state.milestones_to_delete:
                                st.session_state.milestones_to_delete.append(milestone_id)
                        else:
                            if milestone_id in st.session_state.milestones_to_delete:
                                st.session_state.milestones_to_delete.remove(milestone_id)
                
                # Display milestone card
                with cols[1 if deletable else 0]:
                    st.markdown(f"""
                    <div style="margin: 12px 0; padding: 16px; border-left: 4px solid {type_colors[phase_type]}; 
                                background-color: #F7FAFC; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; align-items: center;">
                            <span style="font-weight: 600; font-size: 1.05rem; color: #2D3748;">{milestone["name"]}</span>
                            <span style="color: #4A5568; font-size: 0.9rem; background-color: #EDF2F7; 
                                        padding: 3px 8px; border-radius: 12px;">
                                {milestone_date.strftime('%a, %b %d')}
                            </span>
                        </div>
                        <p style="margin: 0; color: #4A5568; font-size: 0.95rem;">{milestone["description"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add calendar button for each milestone if user_email is provided
                if user_email and not deletable:
                    with cols[-1]:
                        # Generate calendar link for this specific milestone
                        calendar_link = generate_google_calendar_link(user_email, milestone_id)
                        st.markdown(f"""
                        <a href="{calendar_link}" target="_blank" style="display: inline-block; 
                           margin-top: 12px; text-decoration: none; color: white; 
                           background-color: #4285F4; padding: 8px 12px; 
                           border-radius: 4px; font-size: 0.8rem; text-align: center;
                           white-space: nowrap; width: 100%;">
                           <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" 
                              viewBox="0 0 16 16" style="vertical-align: text-bottom; margin-right: 5px;">
                              <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0ZM4.5 7.5a.5.5 0 0 1 0-1h5.793L8.146 4.354a.5.5 0 1 1 .708-.708l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L10.293 7.5H4.5Z"/>
                           </svg>
                           Add to Calendar
                        </a>
                        """, unsafe_allow_html=True)
    
    # Return list of milestone IDs to delete
    if deletable:
        return st.session_state.milestones_to_delete
    return []

def milestone_calendar_ui(user_email, launch_plan=None):
    """
    Display the milestone calendar UI
    
    Args:
        user_email (str): User's email
        launch_plan (dict, optional): The generated launch plan
    """
    try:
        st.markdown("### Launch Timeline & Milestones")

        # Check for duplicates and remove them automatically
        duplicates_removed = remove_duplicate_milestones(user_email)
        if duplicates_removed > 0:
            st.toast(f"Removed {duplicates_removed} duplicate milestones")
        
        # Get existing milestones
        user_milestones = get_user_milestones(user_email)
        
        # Display tabs for adding new milestones vs viewing existing ones
        tab1, tab2 = st.tabs(["Add Milestones", "View Calendar"])
        
        with tab1:
            # Option to use suggested milestones if launch plan is available
            if launch_plan:
                st.markdown("#### Suggested Milestones")
                
                try:
                    suggested_milestones = create_suggested_milestones(launch_plan, user_email)
                    
                    # Add option to reset calendar and use only suggested milestones
                    use_only_suggested = st.checkbox("Replace existing milestones with these suggestions", 
                                                    help="This will clear your current calendar and add only these suggested milestones")
                    
                    # Display suggested milestones as selectable options
                    selected_milestones = []
                    for i, milestone in enumerate(suggested_milestones):
                        col1, col2, col3 = st.columns([1, 3, 2])
                        with col1:
                            selected = st.checkbox("", key=f"suggested_ms_{i}")
                            if selected:
                                selected_milestones.append(milestone)
                        with col2:
                            st.markdown(f"**{milestone['name']}**")
                            st.markdown(f"_{milestone['description']}_")
                        with col3:
                            st.markdown(f"Date: {milestone['date']}")
                            st.markdown(f"Type: {milestone['type'].capitalize()}")
                        st.divider()
                    
                    # Add selected milestones
                    if selected_milestones and st.button("Add Selected Milestones", use_container_width=True):
                        # Clear existing milestones if requested
                        if use_only_suggested:
                            reset_user_milestones(user_email)
                            
                        # Add selected milestones
                        added_count = 0
                        for milestone in selected_milestones:
                            milestone_date = datetime.datetime.strptime(milestone['date'], "%Y-%m-%d").date()
                            success, _ = add_milestone(user_email, milestone['name'], milestone_date, 
                                                    milestone['description'], milestone['type'])
                            if success:
                                added_count += 1
                                
                        st.success(f"{added_count} milestones added to your calendar!")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error creating suggested milestones: {str(e)}")
                    st.info("You can still create custom milestones below.")
                
                st.markdown("---")
            
            # Custom milestone creation form
            st.markdown("#### Add Custom Milestone")
            
            milestone_name = st.text_input("Milestone Name", placeholder="E.g., Website Launch")
            milestone_date = st.date_input("Date", min_value=datetime.date.today())
            milestone_description = st.text_area("Description", placeholder="Describe this milestone")
            milestone_type = st.selectbox("Type", ["pre-launch", "launch", "post-launch"])
            
            if st.button("Add to Calendar", use_container_width=True):
                if milestone_name and milestone_description:
                    success, _ = add_milestone(user_email, milestone_name, milestone_date, milestone_description, milestone_type)
                    if success:
                        st.success("Milestone added to your calendar!")
                        st.experimental_rerun()
                else:
                    st.error("Please enter a name and description for your milestone.")
        
        with tab2:
            if not user_milestones:
                st.info("You haven't added any milestones yet. Add some milestones to see them in your calendar.")
            else:
                # Add a reset calendar button
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("Reset Calendar", type="secondary"):
                        if reset_user_milestones(user_email):
                            st.success("Calendar has been reset!")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to reset calendar")
                
                # Use checkbox instead of toggle for edit mode
                edit_mode = st.checkbox("Edit Mode (Select milestones to delete)", value=False)
                
                # Show total number of milestones at top
                st.info(f"You have {len(user_milestones)} milestones in your calendar")
                
                # Use the improved timeline display with delete checkboxes if in edit mode
                milestones_to_delete = display_improved_timeline(user_milestones, deletable=edit_mode, user_email=user_email)
                
                # Show delete button if in edit mode and milestones are selected
                if edit_mode and milestones_to_delete:
                    if st.button(f"Delete Selected Milestones ({len(milestones_to_delete)})", type="primary"):
                        deleted_count = 0
                        for milestone_id in milestones_to_delete:
                            if delete_milestone(user_email, milestone_id):
                                deleted_count += 1
                        
                        if deleted_count > 0:
                            st.success(f"Deleted {deleted_count} milestone(s).")
                            # Clear the selection state
                            if "milestones_to_delete" in st.session_state:
                                del st.session_state.milestones_to_delete
                            st.experimental_rerun()
                        else:
                            st.error("Failed to delete milestones.")
                
                # Add helpful info text instead of the Export section
                if not edit_mode:
                    st.info("Click the 'Add to Calendar' button next to any milestone to add it to your Google Calendar.")
    except Exception as e:
        st.error(f"An error occurred while displaying the calendar: {str(e)}")
        st.info("You can go back to your launch plan and try again later.")