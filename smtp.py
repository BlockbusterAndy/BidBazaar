import smtplib
from django.core.mail import send_mail


try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('bidbazaar2024@gmail.com', 'veur iymr rtdj twki')
    server.sendmail('bidbazaar2024@gmail.com','aniketdj19@gmail.com','Hello from BidBazaar!')
    print("SMTP server connection successful")
except Exception as e:
    print("Failed to connect to SMTP server:", e)
