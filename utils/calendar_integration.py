import streamlit as st
import datetime
import uuid
import json
import os

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
    
    # Create milestone object
    milestone_id = str(uuid.uuid4())
    milestone = {
        "id": milestone_id,
        "name": milestone_name,
        "date": milestone_date.strftime("%Y-%m-%d"),
        "description": milestone_description,
        "type": milestone_type,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add to user's milestones
    milestones[user_email].append(milestone)
    
    # Save updated milestones
    success = save_milestones(milestones)
    
    return success, milestone_id

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
            
            # Create Google Calendar link with proper parameters
            google_link = (
                f"https://calendar.google.com/calendar/render?"
                f"action=TEMPLATE&text={title.replace(' ', '+')}"
                f"&dates={start_date}/{end_date}"
                f"&details={details.replace(' ', '+')}"
                f"&sf=true&output=xml"
            )
            
            return google_link
    
    # For all milestones - create a series of Google Calendar links
    if milestones:
        # Sort milestones by date
        sorted_milestones = sorted(milestones, key=lambda x: x["date"])
        
        # Start with base Google Calendar URL
        google_link = "https://calendar.google.com/calendar/render?action=TEMPLATE"
        
        # Add each milestone as a separate event
        for i, milestone in enumerate(sorted_milestones[:10]):  # Limit to 10 milestones to avoid URL length issues
            title = milestone["name"]
            # Format dates properly for Google Calendar
            start_date = milestone["date"].replace("-", "")
            # Calculate end date (next day for all-day events)
            date_obj = datetime.strptime(milestone["date"], "%Y-%m-%d")
            next_day = date_obj + timedelta(days=1)
            end_date = next_day.strftime("%Y%m%d")
            
            details = f"{milestone['description']} ({milestone['type']})"
            
            # Use unique parameter names for each event
            google_link += f"&src=none&text{i}={title.replace(' ', '+')}"
            google_link += f"&dates{i}={start_date}/{end_date}"
            google_link += f"&details{i}={details.replace(' ', '+')}"
        
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
    # Get launch type and funding status
    launch_type = launch_plan["launch_summary"]["launch_type"]
    funding_status = launch_plan["launch_summary"]["funding_status"]
    
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

def milestone_calendar_ui(user_email, launch_plan=None):
    """
    Display the milestone calendar UI
    
    Args:
        user_email (str): User's email
        launch_plan (dict, optional): The generated launch plan
    """
    st.markdown("### Launch Timeline & Milestones")
    
    # Get existing milestones
    user_milestones = get_user_milestones(user_email)
    
    # Display tabs for adding new milestones vs viewing existing ones
    tab1, tab2 = st.tabs(["Add Milestones", "View Calendar"])
    
    with tab1:
        # Option to use suggested milestones if launch plan is available
        if launch_plan:
            st.markdown("#### Suggested Milestones")
            
            suggested_milestones = create_suggested_milestones(launch_plan, user_email)
            
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
                for milestone in selected_milestones:
                    milestone_date = datetime.datetime.strptime(milestone['date'], "%Y-%m-%d").date()
                    add_milestone(user_email, milestone['name'], milestone_date, milestone['description'], milestone['type'])
                st.success("Selected milestones added to your calendar!")
                st.experimental_rerun()
            
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
            # Sort milestones by date
            sorted_milestones = sorted(user_milestones, key=lambda x: x["date"])
            
            # Filter options
            milestone_types = ["All Types"] + list(set(m["type"] for m in user_milestones))
            filter_type = st.selectbox("Filter by type:", milestone_types)
            
            # Apply filters
            filtered_milestones = sorted_milestones
            if filter_type != "All Types":
                filtered_milestones = [m for m in sorted_milestones if m["type"] == filter_type]
            
            # Calendar visualization
            st.markdown("#### Your Launch Timeline")
            
            # Get min and max dates for timeline
            min_date = min([datetime.datetime.strptime(m["date"], "%Y-%m-%d").date() for m in user_milestones])
            max_date = max([datetime.datetime.strptime(m["date"], "%Y-%m-%d").date() for m in user_milestones])
            
            # Create a simple timeline visualization
            total_days = (max_date - min_date).days
            if total_days > 0:
                timeline_width = 100  # percent
                
                # Draw timeline
                st.markdown(
                    f"""
                    <div class="timeline-container">
                        <div class="timeline-line" style="width: {timeline_width}%"></div>
                    """
                    , unsafe_allow_html=True
                )
                
                # Add milestone markers to timeline
                for milestone in filtered_milestones:
                    milestone_date = datetime.datetime.strptime(milestone["date"], "%Y-%m-%d").date()
                    days_from_start = (milestone_date - min_date).days
                    position_percent = (days_from_start / total_days) * 100
                    
                    # Select color based on type
                    color = "#FF5A5F"  # default
                    if milestone["type"] == "pre-launch":
                        color = "#4299E1"
                    elif milestone["type"] == "post-launch":
                        color = "#38A169"
                    
                    st.markdown(
                        f"""
                        <div style="left: {position_percent}%;" class="timeline-marker" style="background-color: {color};"></div>
                        <div style="left: {position_percent}%;" class="timeline-label-top">{milestone_date.strftime("%b %d")}</div>
                        <div style="left: {position_percent}%;" class="timeline-label-bottom">{milestone["name"]}</div>
                        """
                        , unsafe_allow_html=True
                    )
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Display milestones in a more detailed view
            st.markdown("#### Your Milestones")
            
            # Group milestones by month
            milestones_by_month = {}
            for milestone in filtered_milestones:
                date_obj = datetime.datetime.strptime(milestone["date"], "%Y-%m-%d")
                month_key = date_obj.strftime("%B %Y")
                if month_key not in milestones_by_month:
                    milestones_by_month[month_key] = []
                milestones_by_month[month_key].append(milestone)
            
            # Display milestones by month
            for month, month_milestones in milestones_by_month.items():
                with st.expander(month, expanded=True):
                    for milestone in month_milestones:
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            date_obj = datetime.datetime.strptime(milestone["date"], "%Y-%m-%d")
                            st.markdown(f"**{milestone['name']}** - {date_obj.strftime('%a, %b %d')}")
                            st.markdown(f"_{milestone['description']}_")
                        
                        with col2:
                            # Display type with appropriate color
                            type_color = "#FF5A5F"
                            if milestone["type"] == "pre-launch":
                                type_color = "#4299E1"
                            elif milestone["type"] == "post-launch":
                                type_color = "#38A169"
                            
                            st.markdown(f"<span style='background-color: {type_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;'>{milestone['type'].capitalize()}</span>", unsafe_allow_html=True)
                            
                            # Generate Google Calendar link
                            google_link = generate_google_calendar_link(user_email, milestone["id"])
                            st.markdown(f"<a href='{google_link}' target='_blank' style='font-size: 0.8rem;'>Add to Google Calendar</a>", unsafe_allow_html=True)
                        
                        with col3:
                            if st.button("Delete", key=f"del_{milestone['id']}", use_container_width=True):
                                if delete_milestone(user_email, milestone["id"]):
                                    st.success("Milestone deleted!")
                                    st.experimental_rerun()
                        
                        st.markdown("---")
            
            # Export options
            st.markdown("#### Export All Milestones")
            
            # Generate Google Calendar link for all milestones
            google_link = generate_google_calendar_link(user_email)
            st.markdown(f"<a href='{google_link}' target='_blank' class='export-button'>Export to Google Calendar</a>", unsafe_allow_html=True)
            
            st.info("This will open Google Calendar with your milestones ready to be added to your calendar.")