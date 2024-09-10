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
    html_content="""<strong>We're thrilled to have you on board and can't wait for you to explore all that we have to offer. Here’s a quick overview to get you started:</strong>""")
    try:
        # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg= SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)