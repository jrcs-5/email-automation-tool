from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv

class Email:
    def __init__(self):
        try:
            load_dotenv()
            self.name = os.getenv("name_account")
            self.email = os.getenv("email_account")
            self.password = os.getenv("password_account")
            self.server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            self.server.ehlo()
            self.server.login(self.email, self.password)
        
        except smtplib.SMTPAuthenticationError:
            raise Exception("Error de autenticación. El usuario o la contraseña no son correctos.")
        except smtplib.SMTPConnectError:
            raise Exception("Error de conexión. No se pudo conectar al servidor.")
        except Exception as e:
            raise Exception(f"Ocurrió un error: {e}")


    def send_email(self, to, subject, body):
        message = f"Subject: {subject}\n\n{body}"
        self.server.sendmail(self.email, to, message)
        
    def __del__(self):
        self.server.quit()