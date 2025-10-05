import smtplib
from email.message import EmailMessage
from typing import Optional
import logging


class EmailSender:
    """
    Cliente SMTP para envio de emails.
    Suporta configuração flexível de host, porta e credenciais.
    """
    
    def __init__(
        self, 
        host: str, 
        port: int, 
        username: str, 
        password: str, 
        default_from: Optional[str] = None,
        timeout: int = 30
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.default_from = default_from or username
        self.timeout = timeout
        
        logging.info(f"EmailSender configurado: {host}:{port}")

    def send(
        self, 
        to_address: str, 
        subject: str, 
        body: str, 
        *, 
        from_address: Optional[str] = None
    ) -> None:
        """
        Envia um email usando as configurações SMTP.
        
        Args:
            to_address: Email do destinatário
            subject: Assunto do email
            body: Corpo do email (texto)
            from_address: Email do remetente (opcional, usa default_from se não especificado)
        
        Raises:
            smtplib.SMTPException: Em caso de erro no envio
        """
        msg = EmailMessage()
        msg["From"] = from_address or self.default_from
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as smtp:
                smtp.starttls()
                if self.username:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg)
                
            logging.info(f"Email enviado com sucesso para {to_address}")
        except Exception as e:
            logging.error(f"Erro ao enviar email para {to_address}: {e}")
            raise
