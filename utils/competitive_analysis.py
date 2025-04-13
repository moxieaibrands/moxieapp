import json
import os
import random
import streamlit as st

def load_competitive_data():
    """Load competitive launch data from JSON file"""
    try:
        data_path = "data/competitive_launches.json"
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                return json.load(f)
        # If file doesn't exist, return None
        return None
    except Exception as e:
        st.error(f"Error loading competitive data: {e}")
        return None

def get_industries():
    """Get list of available industries from the data"""
    data = load_competitive_data()
    if data and 'industries' in data:
        return list(data['industries'].keys())
    return []

def get_similar_companies(launch_type=None, funding_status=None, industry=None, limit=3):
    """
    Get similar company examples based on launch type, funding status, and/or industry
    
    Args:
        launch_type (str, optional): Type of launch
        funding_status (str, optional): Funding status
        industry (str, optional): Industry category
        limit (int, optional): Maximum number of examples to return
        
    Returns:
        list: List of company examples
    """
    data = load_competitive_data()
    if not data:
        return []
    
    # Companies that match criteria
    matching_companies = set()
    
    # Add companies by launch type
    if launch_type and launch_type in data.get('launch_types', {}):
        matching_companies.update(data['launch_types'][launch_type])
    
    # Add companies by funding level
    if funding_status and funding_status in data.get('funding_levels', {}):
        # If we already have companies by launch type, prioritize intersection
        if matching_companies:
            funding_companies = set(data['funding_levels'][funding_status])
            matching_companies = matching_companies.intersection(funding_companies)
        else:
            matching_companies.update(data['funding_levels'][funding_status])
    
    # Filter by industry if specified
    industry_companies = []
    if industry and industry in data.get('industries', {}):
        industry_examples = data['industries'][industry]['examples']
        industry_companies = [example['company'] for example in industry_examples]
        
        # If we have companies from other filters, prioritize intersection
        if matching_companies:
            matching_companies = matching_companies.intersection(set(industry_companies))
        else:
            matching_companies = set(industry_companies)
    
    # Get detailed information for matching companies
    results = []
    all_examples = []
    
    # Collect all examples from all industries
    for ind, ind_data in data.get('industries', {}).items():
        if industry and ind != industry:
            continue
        all_examples.extend(ind_data['examples'])
    
    # Filter to matching companies
    for example in all_examples:
        if example['company'] in matching_companies:
            results.append(example)
    
    # If no matches found but industry specified, return random examples from that industry
    if not results and industry:
        industry_examples = data['industries'][industry]['examples']
        # Shuffle to get random selection
        random.shuffle(industry_examples)
        results = industry_examples[:limit]
    
    # If still no matches, return random examples across all industries
    if not results:
        # Collect some random examples from each industry
        for ind, ind_data in data.get('industries', {}).items():
            results.extend(random.sample(ind_data['examples'], min(1, len(ind_data['examples']))))
    
    # Limit the number of results
    random.shuffle(results)
    return results[:limit]

def display_competitive_analysis(launch_type=None, funding_status=None, selected_industry=None):
    """
    Display competitive analysis UI component
    
    Args:
        launch_type (str, optional): Type of launch
        funding_status (str, optional): Funding status
        selected_industry (str, optional): Selected industry
    """
    st.markdown("### Competitive Launch Analysis")
    
    # Get available industries
    industries = get_industries()
    
    # Let user select or change industry
    industry = st.selectbox(
        "Select your industry for more relevant examples:",
        ["All Industries"] + industries,
        index=0 if selected_industry is None else industries.index(selected_industry) + 1
    )
    
    selected_industry = None if industry == "All Industries" else industry
    
    # Get similar companies
    similar_companies = get_similar_companies(
        launch_type=launch_type,
        funding_status=funding_status,
        industry=selected_industry,
        limit=3
    )
    
    if not similar_companies:
        st.warning("No similar company examples found. Please try a different industry.")
        return
    
    st.markdown(
        f"Here are examples of successful launches from companies similar to yours:"
    )
    
    # Display company examples
    for i, company in enumerate(similar_companies):
        with st.expander(f"{company['company']} ({company['launch_year']})", expanded=i==0):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Launch Approach:** {company['approach']}")
                st.markdown(f"**Funding at Launch:** {company['funding_at_launch']}")
                
                # Key strategies
                st.markdown("**Key Strategies:**")
                for strategy in company['key_strategies']:
                    st.markdown(f"- {strategy}")
                
                st.markdown(f"**Results:** {company['results']}")
            
            with col2:
                st.markdown("**Notable Tactic:**")
                st.markdown(f"_{company['notable_tactics']}_")
                
                st.markdown("**Key Insight:**")
                st.markdown(f"_{company['retrospective_insight']}_")
    
    # Add section for key takeaways
    st.markdown("### Key Takeaways from Successful Launches")
    
    # Generate some smart takeaways based on the examples
    takeaways = generate_takeaways(similar_companies, launch_type, funding_status)
    
    for i, takeaway in enumerate(takeaways):
        st.markdown(f"**{i+1}. {takeaway['title']}**")
        st.markdown(f"{takeaway['description']}")

def generate_takeaways(companies, launch_type, funding_status):
    """
    Generate smart takeaways based on company examples
    
    Args:
        companies (list): List of company examples
        launch_type (str): Type of launch
        funding_status (str): Funding status
        
    Returns:
        list: List of takeaway dictionaries
    """
    takeaways = []
    
    # Look for patterns in the examples
    has_exclusivity = any("invite-only" in company['approach'].lower() or 
                         "waitlist" in company['approach'].lower() for company in companies)
    
    has_content = any("content" in company['approach'].lower() for company in companies)
    
    has_community = any("community" in company['approach'].lower() or 
                       "community" in str(company['key_strategies']).lower() for company in companies)
    
    is_bootstrapped = "Bootstrapping" in str(funding_status) if funding_status else False
    
    # Generate relevant takeaways
    if has_exclusivity:
        takeaways.append({
            "title": "Controlled Access Creates Demand",
            "description": "Several successful companies used waitlists or invite systems to create early demand and control quality. Consider an exclusive beta or staged rollout to build anticipation."
        })
    
    if has_content:
        takeaways.append({
            "title": "Content Marketing Builds Authority",
            "description": "Content-first or content-supported launches help establish authority and educate potential customers. Consider how you can use content to showcase your expertise and use case."
        })
    
    if has_community:
        takeaways.append({
            "title": "Community-Driven Growth Is Powerful",
            "description": "Building a community around your product creates evangelists and provides valuable feedback. Consider how to cultivate early adopters into a supportive community."
        })
    
    if is_bootstrapped:
        takeaways.append({
            "title": "Resource Constraints Can Drive Focus",
            "description": "Bootstrapped companies often succeed through extreme focus on a core value proposition. Consider how to create maximum impact with minimal resources."
        })
    
    # Add general takeaways based on launch type
    if launch_type and "New Startup/Product Launch" in launch_type:
        takeaways.append({
            "title": "Simplicity Wins at Launch",
            "description": "Successful product launches often start with a focused offering rather than numerous features. Consider launching with your 'hero' feature or product that clearly demonstrates your value."
        })
    
    if launch_type and "Brand Repositioning" in launch_type:
        takeaways.append({
            "title": "Narrative Is Critical for Repositioning",
            "description": "Successful rebrand launches clearly articulate the 'why' behind the change. Ensure your narrative connects past to future while highlighting new value."
        })
    
    if launch_type and "Funding Announcement" in launch_type:
        takeaways.append({
            "title": "Connect Funding to Customer Benefit",
            "description": "The most effective funding announcements tie the investment to specific customer benefits. Frame your funding in terms of how it enables you to better serve customers."
        })
    
    if launch_type and "Partnership" in launch_type:
        takeaways.append({
            "title": "Mutual Value Must Be Clear",
            "description": "Successful partnership launches clearly articulate the value to all parties, including customers. Ensure your partnership story explains benefits for everyone involved."
        })
    
    # Ensure we have at least 3 takeaways
    generic_takeaways = [
        {
            "title": "Timing Can Be As Important As Execution",
            "description": "Many successful launches benefited from timing with market trends or shifts. Consider how your launch aligns with current market conditions and adjust messaging accordingly."
        },
        {
            "title": "Product Experience Drives Word-of-Mouth",
            "description": "The initial user experience often determines whether users become advocates. Invest in creating memorable moments in your onboarding and core workflows."
        },
        {
            "title": "Clear Positioning Cuts Through Noise",
            "description": "Companies that articulate a clear, differentiated position tend to gain traction faster. Ensure your launch clearly communicates what makes your offering unique."
        }
    ]
    
    # Add generic takeaways if needed
    while len(takeaways) < 3:
        if not generic_takeaways:
            break
        takeaway = generic_takeaways.pop(0)
        if takeaway not in takeaways:
            takeaways.append(takeaway)
    
    return takeaways