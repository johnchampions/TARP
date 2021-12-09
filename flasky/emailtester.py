
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_address = 'john.matthews72@gmail.com'
sender_pass = 'epdyljvuezscwphu'
receiver_address = 'john@champions.tech'
mail_content = '''Hello John,
This is a test of the smtp system.  See how you go.
'''



def emailinfo(stringtosend):
    if stringtosend is str:
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'flasky Error'
        message.attach(MIMEText(stringtosend, 'plain'))
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

