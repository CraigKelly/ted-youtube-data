# -*- coding: utf-8 -*-

"""The crawler to download YouTube video viewcount history."""
# Author: Honglin Yu <yuhonglin1986@gmail.com>
# License: BSD 3 clause

import smtplib
import email.mime.text
import time


def send_email(s, c, from_addr, mail_password, to_addrs):
    """Send emai on completion."""
    # check if want to send email
    if from_addr + mail_password + to_addrs == '':
        return

    SUBJECT = s
    CONTENT = c

    # my test mail
    mail_username = from_addr
    mail_password = mail_password

    to_addrs = (to_addrs)

    # HOST & PORT
    HOST = 'smtp.gmail.com'
    PORT = 25

    # Create SMTP Object
    smtp = smtplib.SMTP()

    # show the debug log
    smtp.set_debuglevel(1)

    # connet
    try:
        smtp.connect(HOST, PORT)
    except Exception:
        print('CONNECT ERROR ****')
        raise
    # gmail uses ssl
    smtp.starttls()
    # login with username & password
    try:
        smtp.login(mail_username, mail_password)
    except Exception:
        print('LOGIN ERROR ****')
        raise
    # fill content with MIMEText's object
    msg = email.mime.text.MIMEText(CONTENT)
    msg['From'] = from_addr
    msg['To'] = ''.join(to_addrs)
    msg['Subject'] = SUBJECT
    # print msg.as_string()
    smtp.sendmail(from_addr, to_addrs, msg.as_string())
    smtp.quit()

    time.sleep(10)
