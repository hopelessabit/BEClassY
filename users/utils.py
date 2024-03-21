from email.message import EmailMessage
import ssl
import smtplib

class Util:
    @staticmethod
    def send_email(data):
        email_sender = 'claasyhethongquanlylophoc@gmail.com'
        email_password = 'tailtafxtaclsqrd'
        email_receiver = 'classyhethongquanlylophoc@gmail.com'

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = data['email_subject']
        em.set_content(data['email_body'])

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, data['to_email'], em.as_string())

    @staticmethod
    def send_payment_email(data):
        email_sender = 'claasyhethongquanlylophoc@gmail.com'
        email_password = 'tailtafxtaclsqrd'
        
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = data['to_email']  # Sử dụng email người nhận từ dữ liệu đầu vào
        em['Subject'] = data['email_subject']
        em.set_content(data['email_body'])

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, data['to_email'], em.as_string())
