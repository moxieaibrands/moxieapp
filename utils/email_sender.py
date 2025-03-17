import smtplib
import json
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def send_email_to_user(recipient_email, plan):
    """
    Send the generated launch plan to the user's email
    
    Args:
        recipient_email (str): The user's email address
        plan (dict): The generated launch plan
        
    Returns:
        bool: Success status of the email sending
    """
    # Determine which method to use
    use_zapier = _should_use_zapier()
    
    if use_zapier:
        # First save to Google Sheets for Zapier to pick up
        return _save_to_sheets_for_zapier(recipient_email, plan)
    else:
        # Direct SMTP email
        return _send_direct_email(recipient_email, plan)

def _should_use_zapier():
    """Determine if we should use Zapier method based on configuration"""
    try:
        # Check if Google Sheets credentials are available
        if 'google' in st.secrets and 'service_account' in st.secrets['google']:
            return True
        return False
    except Exception:
        # If no configuration is found, default to direct email
        return False

def _save_to_sheets_for_zapier(recipient_email, plan):
    """
    Save plan data to Google Sheets for Zapier to handle email sending
    
    Args:
        recipient_email (str): The user's email address
        plan (dict): The generated launch plan
        
    Returns:
        bool: Success status
    """
    try:
        # Use service account credentials from Streamlit secrets
        service_account_info = json.loads(st.secrets["google"]["service_account"])
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
        client = gspread.authorize(creds)
        
        # Access the spreadsheet and worksheet
        sheet_id = st.secrets["google"]["sheets_id"]
        worksheet_name = st.secrets["google"]["worksheet_name"]
        
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)
        
        # Format data for insertion
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        strategies_json = json.dumps(plan['recommended_strategies'])
        next_steps_json = json.dumps(plan['next_steps'])
        
        # Prepare row data
        row = [
            timestamp,
            plan['first_name'],
            plan['startup_name'],
            recipient_email,
            plan['launch_summary']['launch_type'],
            plan['launch_summary']['funding_status'],
            plan['launch_summary']['primary_goal'],
            plan['messaging_advice'],
            strategies_json,
            next_steps_json,
            False  # email_sent status starts as False
        ]
        
        # Append row to sheet
        worksheet.append_row(row)
        return True
        
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        # Fall back to direct email if sheets fails
        return _send_direct_email(recipient_email, plan)

def _send_direct_email(recipient_email, plan):
    """
    Send email directly via SMTP
    
    Args:
        recipient_email (str): The user's email address
        plan (dict): The generated launch plan
        
    Returns:
        bool: Success status
    """
    try:
        # Get SMTP settings from Streamlit secrets
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]
        smtp_username = st.secrets["email"]["smtp_username"]
        smtp_password = st.secrets["email"]["smtp_password"]
        
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Your High-Impact Launch Plan 🚀"
        msg['From'] = f"Moxie Launch Assistant <{smtp_username}>"
        msg['To'] = recipient_email
        
        # Create HTML content
        strategies_html = ""
        for strategy in plan['recommended_strategies']:
            strategies_html += f"<li>{strategy}</li>"
        
        next_steps_html = ""
        for step in plan['next_steps']:
            next_steps_html += f"<li>{step}</li>"
        
        html = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333;">
            <p>Hey {plan['first_name']},</p>
            
            <p>First off—big congrats on building {plan['startup_name']}. I know firsthand how intense launching a startup can be, and I built Moxie AI to help founders like you get the visibility you need to succeed.</p>
            
            <p>Based on what you shared, here's your high-impact launch plan:</p>
            
            <p style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                🔹 <strong>Launch Type:</strong> {plan['launch_summary']['launch_type']}<br>
                🔹 <strong>Funding Stage:</strong> {plan['launch_summary']['funding_status']}<br>
                🔹 <strong>Your Primary Goal:</strong> {plan['launch_summary']['primary_goal']}
            </p>
            
            <p><strong>{plan['messaging_advice']}</strong></p>
            
            <div style="background-color: #f1f3f5; padding: 20px; border-radius: 5px; border-left: 5px solid #FF5A5F; margin: 20px 0;">
                <p style="font-weight: bold; font-size: 18px;">✨ Your Personalized Launch Strategies:</p>
                <ul>
                    {strategies_html}
                </ul>
            </div>
            
            <p style="font-weight: bold;">📌 Your Next Steps:</p>
            <ol>
                {next_steps_html}
            </ol>
            
            <p>💡 <strong>Ready to execute?</strong> You can take one of these three paths:</p>
            
            <p>
                1️⃣ <strong>DIY ($29/month):</strong> Get an automated weekly launch roadmap so you stay on track.<br>
                2️⃣ <strong>Coaching ($500/month):</strong> Get direct guidance & accountability to keep momentum.<br>
                3️⃣ <strong>Full-Service ($5K over 3 months):</strong> Let us run your launch for you.
            </p>
            
            <p>📅 If you ever want a deeper strategy session, let's chat. Otherwise, keep me posted—I'll be cheering for you.</p>
            
            <p>
                Best,<br>
                <strong>Steph</strong>
            </p>
        </body>
        </html>
        '''
        
        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))
        
        # Connect to server and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False