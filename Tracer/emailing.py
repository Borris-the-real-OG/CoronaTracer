import smtplib
from os import getenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendEmails(recipients, subject, body):
    """
    Sends emails using Gmail server to recipients, who are all bcc'd.

    Parameters:
    body: Expects a MIMEText(html or plain)
    """
    
    sender_email = getenv("SENDER_EMAIL")
    sender_pass = getenv("SENDER_PASS")

    if sender_email is None or sender_pass is None:
        raise ValueError("Please provide a username and a password")
    
    message = MIMEMultipart('alternative')

    content = MIMEText(body, ('html' if body[:6] == "<html>" else 'plain'))

    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = sender_email # this is to get bcc to behave
    message.attach(content)

    with smtplib.SMTP("smtp.gmail.com:587") as server:
        server.starttls()
        server.login(sender_email, sender_pass)
        server.sendmail(sender_email, [sender_email] + recipients, message.as_string())
        server.quit()

if __name__ == '__main__':
    sendEmails(["YOUR EMAIL HERE"], "Testing Email", "What's the average air speed velocity of an unladen swallow?")
