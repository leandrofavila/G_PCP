import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import io


class DisparaEmail:
    def __init__(self, msg, titulo, attach=None):
        self.msg = msg
        self.titulo = titulo
        self.attach = attach


    def dispara_email(self):
        msg = MIMEMultipart()
        message = self.trata_email()
        password = "srengld21v3l1"
        msg['From'] = "ldeavila@sr.ind.br"
        #presta atenção tu apanhaste bastante com recipients, em msg[to] deve ser uma string em sendmail deve ser uma lista de strings
        recipients = self.destinatarios()
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = self.titulo
        if self.titulo != "ITENS COMPRADOS COM EMBARQUE NÃO":
            msg.attach(MIMEText(message, 'plain'))
        else:
            msg.attach(MIMEText(message, 'html'))

        if self.attach:
            self.add_attachment(msg)
        server = smtplib.SMTP('10.40.3.12:465')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], recipients, msg.as_string())
        server.quit()


    def add_attachment(self, msg):
        arch = self.attach
        print(arch)
        with open(arch, "rb") as f:
            excel_attachment = MIMEApplication(f.read(), _subtype="xlsx")
            excel_attachment.add_header('Content-Disposition', 'attachment', filename=arch)
            return msg.attach(excel_attachment)


    def destinatarios(self):
        if 'EMBARQUE' in self.titulo:
            return ["ldeavila@sr.ind.br", 'rmoreira@sr.ind.br', 'wesley@sr.ind.br', 'braian@sr.ind.br', 'mtasquetto@sr.ind.br',
                    'fernando@sr.ind.br', 'jtomas@sr.ind.br', 'raphael@sr.ind.br', 'avirago@sr.ind.br',
                    'luis@sr.ind.br', 'william@sr.ind.br', 'leduardo@sr.ind.br']
        if '30 dias' in self.titulo:
            return ["ldeavila@sr.ind.br", 'producao@sr.ind.br', "qualidade@sr.ind.br", 'almoxarifado@sr.ind.br',
                    "expedicao@sr.ind.br"]
        if 'apontamentos' in self.titulo:
            return ["ldeavila@sr.ind.br", "vagner@sr.ind.br", "wesley@sr.ind.br"]


    def trata_email(self):
        if isinstance(self.msg, io.TextIOWrapper):
            return self.msg.read()
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
