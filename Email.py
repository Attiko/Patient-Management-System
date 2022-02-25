import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Email:
    def __init__(self, receiver):
        self.email = "Patienthelpteam@gmail.com"
        self.password = "Patient24."
        self.receiver = receiver
        self.subject = ""
        self.text = ""

    def welcome_message(self, patient):
        self.subject = "WELCOME TO PATIENT MANAGEMENT INC"
        self.text = "Dear " + patient + "\nWe are delighted to have you at Patient Management Inc. we look forward to " \
                                        "providing you with our world class health service. we can't wait to have you " \
                                        "in " \
                                        "office! "

    def prescription_sent(self, patient):
        self.subject = "Prescription Sent"
        self.text = "Dear " + patient + ",\nYour Medications have been sent to your address. you should receive it in " \
                                        "three working days "

    def appointment_reminder(self, patient, date, time):
        self.subject = "Appointment Confirmation"
        self.text = "Dear " + patient + ",\nYour appointment with the GP has been set for " + date + " at " \
                    + time + ". We look forward to seeing you soon! "

    def setup_message(self):
        message = MIMEMultipart()
        message['From'] = self.email
        message['To'] = self.receiver
        message['Subject'] = self.subject
        message.attach(MIMEText(self.text, 'plain'))
        return message

    def sendmail(self):

        smtpserver = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtpserver.login(self.email, self.password)  # login with mail_id and password
        text = self.setup_message().as_string()
        try:
            smtpserver.sendmail(self.email, self.receiver, text)

        except:
            sys.exit("Mail failed to send")

        finally:
            smtpserver.quit()


