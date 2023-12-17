from typing import List
import os
from dotenv import load_dotenv

import smtplib
from email.mime.text import MIMEText
import ssl


class EmailSender:
    def __init__(self, recipients: List[str] = None, subject: str = None):
        if isinstance(recipients, str):
            recipients = [recipients]
        if recipients is None:
            recipients = ['kamgra5@st.amu.edu.pl', 'domede@st.amu.edu.pl', 'artmak1@st.amu.edu.pl',
                          'zofrut1@st.amu.edu.pl']

        self.recipients = recipients
        self.subject = subject
        self.body = None

        load_dotenv()
        self.sender = os.environ.get('EMAIL_NOTIFICATION_LOGIN')
        self.password = os.environ.get('EMAIL_NOTIFICATION_PASSWD')

    def create_body(self, text):
        self.body = text

    def send(self):
        if self.body is None:
            raise ValueError("The message body is empty!")
        if self.subject is None:
            raise ValueError("The message subject is empty!")

        if '<html>' in self.body.lower():
            msg = MIMEText(self.body, 'html')
        else:
            msg = MIMEText(self.body)

        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(self.recipients)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp_server:
            smtp_server.login(self.sender, self.password)
            smtp_server.sendmail(self.sender, self.recipients, msg.as_string())
            print(f"Message sent to: {','.join(self.recipients)}")
