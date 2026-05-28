import os
import smtplib
from email.mime.multipart import MIMEMultipart


class EmailFacade:
    def __init__(self):
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = os.getenv("SMTP_PORT")

    def send_email(self, recipients: list, subject: str, body: str) -> None:
        message = MIMEMultipart()
        message["From"] = self.username
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.attach(body)

        mailserver = self._connect_to_smtp_server()
        mailserver.send_message(message)
        mailserver.quit()

    def _connect_to_smtp_server(self) -> smtplib.SMTP:
        mailserver = smtplib.SMTP(self.smtp_server, self.smtp_port)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login(self.username, self.password)
        return mailserver


def email_client():
    email_facade = EmailFacade()
    recipients = ["recipient1@gmail.com", "recipient2@gmail.com"]
    subject = "Hello from Facade!"
    body = "This is a test email sent using the EmailFacade."
    email_facade.send_email(recipients, subject, body)


if __name__ == "__main__":
    email_client()
