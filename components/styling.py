import streamlit as st

def load_css():
    """Return the custom CSS for the app"""
    css = """
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
        padding: 0rem;
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
        padding: 0rem;
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
    
    /* Button styling - Updated to black */
    .stButton button {
        background-color: #000000 !important;
        color: white !important;
        border-radius: 9999px !important;
        font-weight: 500 !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
    }
    
    .stButton button:hover {
        background-color: #333333 !important;
    }
    
    /* Progress bar styling - Updated to blue */
    .stProgress > div > div {
        background-color: #77c4ff !important;
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
        background-color: #000000;
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
    
    /* Calendar styling */
    .milestone-card {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
    }
    
    .milestone-date {
        font-size: 0.8rem;
        color: #6B7280;
    }
    
    .milestone-title {
        font-weight: 600;
        margin: 0.25rem 0;
    }
    
    .milestone-description {
        font-size: 0.9rem;
        color: #4B5563;
    }
    
    .milestone-badge {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1E40AF;
        font-size: 0.7rem;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
        margin-top: 0.25rem;
    }
    
    /* Timeline styling */
    .timeline-container {
        position: relative;
        width: 100%;
        height: 120px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
        overflow: visible;
    }
    
    .timeline-line {
        position: absolute;
        top: 50px;
        left: 0;
        height: 2px;
        background-color: #6B7280;
    }
    
    .timeline-marker {
        position: absolute;
        top: 46px;
        transform: translateX(-50%);
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    
    .timeline-label-top {
        position: absolute;
        top: -35px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.7rem;
        white-space: nowrap;
    }
    
    .timeline-label-bottom {
        position: absolute;
        top: 15px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.7rem;
        white-space: nowrap;
        max-width: 100px;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Competitive analysis styling */
    .company-card {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .company-card:hover {
        border-color: #FF5A5F;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .company-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: #111827;
    }
    
    .company-launch-year {
        font-size: 0.9rem;
        color: #6B7280;
    }
    
    .company-approach {
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    .company-funding {
        font-size: 0.9rem;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .strategy-list {
        margin: 0.5rem 0;
    }
    
    .notable-tactic {
        background-color: #FFF7ED;
        padding: 0.75rem;
        border-radius: 0.5rem;
        font-style: italic;
        margin: 0.5rem 0;
    }
    
    .insight-box {
        background-color: #F0FDF4;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .takeaway-card {
        background-color: #F9FAFB;
        border-left: 4px solid #FF5A5F;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    
    .takeaway-title {
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Export button styling */
    .export-button {
        display: inline-block;
        background-color: #000000;
        color: white !important;
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        text-align: center;
        width: 100%;
    }
    
    /* Remove default Streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .pricing-grid {
            grid-template-columns: 1fr;
        }
        
        .action-buttons {
            flex-direction: column;
        }
    }
    """
    
    # Return the CSS but don't apply it here
    return css

def apply_css():
    """Apply the CSS to the Streamlit app using st.markdown with unsafe_allow_html=True"""
    css = load_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)