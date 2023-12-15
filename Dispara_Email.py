import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import io


class DisparaEmail:
    def __init__(self, msg):
        self.msg = msg

    def dispara_email(self, subject):
        msg = MIMEMultipart()
        message = self.trata_email()
        password = "srengld21v3l1"
        msg['From'] = "ldeavila@sr.ind.br"
        recipients = ["ldeavila@sr.ind.br", 'rmoreira@sr.ind.br']
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        if subject != "ITENS COMPRADOS COM EMBARQUE NÃO":
            msg.attach(MIMEText(message, 'plain'))
        else:
            msg.attach(MIMEText(message, 'html'))

        server = smtplib.SMTP('10.40.3.12:465')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], recipients, msg.as_string())
        server.quit()


    def trata_email(self):
        if isinstance(self.msg, io.TextIOWrapper):
            return self.msg
        else:
            nlis = self.sauda() + self.msg
        return nlis


    @staticmethod
    def sauda():
        currentTime = datetime.datetime.now()
        if currentTime.hour < 12:
            return 'Bom dia. '
        elif 12 <= currentTime.hour <= 18:
            return 'Boa tarde. '
        else:
            return 'Boa noite. '
