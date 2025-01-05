import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_welcome_email(user):
    message = Mail(
    from_email='akshit.testinguser@gmail.com',
    to_emails=user.email,
    subject='Welcome to our ecommerce website',
    html_content=f"""
        <p>Hello { user.first_name },</p>
        <p>Thank you for registering. Please click the link below to activate your account:</p>
        <p><a href="http://localhost:8000/api/v1/verify-email/?token={user.verification_code}">Activate your account</a></p>
        """)
    try:
        sg= SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        return e

def send_forgot_password_email(user, token):
    try:
        sendgrid_api_key = settings.SENDGRID_API_KEY

        sg = SendGridAPIClient(api_key=sendgrid_api_key)

        from_email = "akshit.testinguser@gmail.com"
        to_email = user.email
        template_id = settings.FORGOT_TEMPLATE_ID  

        reset_link = f"{settings.FRONTEND_URL}reset-password/{token}/"

        dynamic_data = {
            "first_name": user.first_name, 
            "reset_link": reset_link,      
        }
        mail = Mail(
            from_email=from_email,
            to_emails=to_email,
        )
        mail.template_id = template_id
        mail.dynamic_template_data = dynamic_data

        response = sg.send(mail)
        if response.status_code != 202:
            raise Exception(f"Failed to send email. Status Code: {response.status_code}, Response Body: {response.body}")
    
    except Exception as e:
        raise Exception(f"Error sending forgot password email via SendGrid: {str(e)}")
