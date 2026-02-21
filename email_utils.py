from flask_mail import Mail, Message
from flask import current_app, render_template
import os

mail = Mail()

def init_mail(app):
    """
    Initialize Flask-Mail with the app configuration.
    """
    # Mailtrap Configuration
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL") == "True"
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
    
    mail.init_app(app)

def send_contact_email(name, email, subject, message):
    """
    Sends confirmation email to the user only.
    Uses MAIL_DEFAULT_SENDER from app config automatically.
    """

    try:
        msg = Message(
            subject=f"We received your message: {subject}",
            recipients=[email]
        )

        msg.body = f"""
Hi {name},

Thank you for contacting us. We have received your message and will respond shortly.

Your Message:
{message}

Best Regards,
ScholarHub Team
"""

        mail.send(msg)
        return True

    except Exception as e:
        print(f"Mail Error: {e}")
        return False

