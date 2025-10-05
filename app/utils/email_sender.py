import smtplib
from email.message import EmailMessage
from typing import Optional


class EmailSender:
    def __init__(self, host: str, port: int, username: str, password: str, default_from: Optional[str] = None) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.default_from = default_from or username

    def send(self, to_address: str, subject: str, body: str, *, from_address: Optional[str] = None) -> None:
        msg = EmailMessage()
        msg["From"] = from_address or self.default_from
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=1200) as smtp:
            smtp.starttls()
            if self.username:
                smtp.login(self.username, self.password)
            smtp.send_message(msg)


