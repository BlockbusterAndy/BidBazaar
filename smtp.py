import smtplib
from django.core.mail import send_mail

#for testing the connection to the SMTP server

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    #enter your email and password here
    server.login('email', 'password')
    #enter the sender and reciever email address here along with the message
    server.sendmail('sendermailaddress','recievermailaddress','Hello from BidBazaar!')
    print("SMTP server connection successful, message sent successfully!")
except Exception as e:
    print("Failed to connect to SMTP server: \n Error -", e)
