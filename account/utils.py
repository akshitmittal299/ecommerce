# utils.py
# from django.core.mail import send_mail
# from django.conf import settings

# def send_welcome_email(user):
#     subject = 'Welcome to MySite'
#     message = f'Hi {user.first_name}, thanks for registering at MySite.'
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
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
        # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg= SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        return e


# def send_forgot_password_email(user, reset_link):
#     try:
#         sendgrid_api_key = settings.SENDGRID_API_KEY

        
#         sg = SendGridAPIClient(api_key=sendgrid_api_key)
        
#         from_email = "akshit.testinguser@gmail.com"
#         to_email = user.email
#         subject = 'Password Reset Request'
#         html_content = f"""
#             <p>Hello {user.first_name},</p>
#             <p>We received a request to reset your password. Please click the button below to reset your password:</p>
#             <p style="text-align: center;">
#                 <a href="{reset_link}" style="
#                     background-color: #007bff;
#                     color: white;
#                     padding: 10px 20px;
#                     text-decoration: none;
#                     border-radius: 5px;
#                     font-size: 16px;
#                 ">Reset Password</a>
#             </p>
#             <p>If you didn't request this change, please ignore this email.</p>
#         """

#         mail = Mail(from_email, to_email, subject, html_content)
#         response = sg.send(mail)
#         if response.status_code != 202:
#             raise Exception(f"Failed to send email. Status Code: {response.status_code}, Response Body: {response.body}")
    
#     except Exception as e:
#         raise Exception(f"Error sending forgot password email via SendGrid: {str(e)}")


from sendgrid.helpers.mail import TrackingSettings, ClickTracking

def send_forgot_password_email(user, token):
    try:
        sendgrid_api_key = settings.SENDGRID_API_KEY

        sg = SendGridAPIClient(api_key=sendgrid_api_key)

        from_email = "akshit.testinguser@gmail.com"
        to_email = user.email
        subject = 'Password Reset Request'

        # # Disable click tracking for this email
        # tracking_settings = TrackingSettings()
        # click_tracking = ClickTracking(enable=False, enable_text=False)
        # tracking_settings.click_tracking = click_tracking

        html_content = f"""
            <p>Hello {user.first_name},</p>
            <p>We received a request to reset your password. Please click the button below to reset your password:</p>
            <p style="text-align: center;">
                <a href='{settings.FRONTEND_URL}reset-password/{token}/' style="
                    background-color: #007bff;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 16px;
                ">Reset Password</a>
            </p>
            <p>If you didn't request this change, please ignore this email.</p>
        """

        mail = Mail(from_email, to_email, subject, html_content)
        # mail.tracking_settings = tracking_settings  # Attach tracking settings

        response = sg.send(mail)
        if response.status_code != 202:
            raise Exception(f"Failed to send email. Status Code: {response.status_code}, Response Body: {response.body}")
    
    except Exception as e:
        raise Exception(f"Error sending forgot password email via SendGrid: {str(e)}")
