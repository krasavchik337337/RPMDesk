import smtplib
import ssl
from pathlib import Path
from email.message import EmailMessage


class EmailSender:
    def __init__(self, host, port, username, password, security):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.security = security

    def send_email(self, recipient, subject, body, attachment_path):
        attachment_path = Path(attachment_path)

        if not attachment_path.is_file():
            raise FileNotFoundError("Файл не найден")

        message = EmailMessage()
        message["From"] = self.username
        message["To"] = recipient
        message["Subject"] = subject

        with attachment_path.open("rb") as file:
            message.add_attachment(
                file.read(),
                maintype="text",
                subtype="csv",
                filename=attachment_path.name
            )

        context = ssl.create_default_context()

        if self.security == "ssl":
            server = smtplib.SMTP_SSL(
                self.host,
                self.host,
                context=context,
                timeout=20
            )
        else:
            server = smtplib.SMTP(
                self.host,
                self.port,
                timeout=20
            )
        with server:
            if self.security == "starttls":
                server.starttls(context=context)

            if self.username:
                server.login(self.username, self.password)

            server.send_message(message)
