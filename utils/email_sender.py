import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email_to_user(recipient_email, plan):
    """
    Send the generated launch plan to the user's email using Gmail SMTP
    
    Args:
        recipient_email (str): The user's email address
        plan (dict): The generated launch plan
        
    Returns:
        bool: Success status of the email sending
    """
    try:
        # Gmail SMTP settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Your Gmail address
        smtp_username = "stephanie@moxieaibrands.com"  # Update if this is not your Gmail address
        
        # Your App Password (NOT your regular Gmail password)
        smtp_password = "tymimbzzquhxsksd"  # Your Gmail App Password without spaces
        
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Your High-Impact Launch Plan 🚀"
        msg['From'] = f"Roy at Moxie <{smtp_username}>"
        msg['To'] = recipient_email
        
        # Create the email content
        html_content = _create_email_html(plan)
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect to server and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        try:
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            st.success("Email sent successfully!")
            return True
        except smtplib.SMTPAuthenticationError as auth_error:
            st.error(f"""
            Gmail Authentication Error: {str(auth_error)}
            
            For Gmail accounts, you need to:
            1. Make sure you're using an App Password, not your regular password
            2. Verify that 2-Step Verification is enabled on your account
            3. Check that the email address is correct
            """)
            server.quit()
            return False
        
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

def _create_email_html(plan):
    """
    Create the HTML content for the email
    
    Args:
        plan (dict): The generated launch plan
        
    Returns:
        str: HTML content for the email
    """
    # Create HTML content for strategies
    strategies_html = ""
    for strategy in plan['recommended_strategies']:
        if isinstance(strategy, dict):
            # If it's a dictionary format, extract the description
            description = strategy.get('description', '')
            if description:
                strategies_html += f"<li>{description}</li>"
            else:
                strategies_html += f"<li>{str(strategy)}</li>"
        else:
            # If it's just a string, use it directly
            strategies_html += f"<li>{strategy}</li>"
    
    # Create HTML content for next steps with proper formatting
    next_steps_html = ""
    for i, step in enumerate(plan['next_steps']):
        if isinstance(step, dict):
            # If it's a dictionary format, extract the title and description
            title = step.get('title', '')
            description = step.get('description', '')
            if title and description:
                next_steps_html += f"<li><strong>{title}</strong>: {description}</li>"
            else:
                # If only description is available or neither
                next_steps_html += f"<li>{step.get('description', str(step))}</li>"
        else:
            # If it's just a string, use it directly
            next_steps_html += f"<li>{step}</li>"
    
    # Links for the plans
    diy_link = "https://www.moxieaibrands.com/diy-launch"
    coaching_link = "https://www.moxieaibrands.com/launch-coach"
    service_link = "https://www.moxieaibrands.com/high-impact-launch"
    
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
        
        <div style="margin: 25px 0;">
            <a href="{diy_link}" style="display: block; margin-bottom: 15px; padding: 12px 20px; background-color: #f8f9fa; text-decoration: none; color: #333; border-radius: 5px; border-left: 3px solid #FF5A5F;">
                <strong>1️⃣ DIY ($29/month):</strong> Get an automated weekly launch roadmap so you stay on track.
            </a>
            
            <a href="{coaching_link}" style="display: block; margin-bottom: 15px; padding: 12px 20px; background-color: #f8f9fa; text-decoration: none; color: #333; border-radius: 5px; border-left: 3px solid #FF5A5F;">
                <strong>2️⃣ Coaching ($500/month):</strong> Get direct guidance & accountability to keep momentum.
            </a>
            
            <a href="{service_link}" style="display: block; margin-bottom: 15px; padding: 12px 20px; background-color: #f8f9fa; text-decoration: none; color: #333; border-radius: 5px; border-left: 3px solid #FF5A5F;">
                <strong>3️⃣ Full-Service ($5K over 3 months):</strong> Let us run your launch for you.
            </a>
        </div>
        
        <p>📅 If you ever want a deeper strategy session, let's chat. Otherwise, keep me posted—I'll be cheering for you.</p>
        
        <p>
            Best,<br>
            <strong>Steph</strong>
        </p>
    </body>
    </html>
    '''
    
    return html