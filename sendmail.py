#!/usr/bin/python2

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os


def get_username_and_password():
    config = open('conf.txt')

    for line in config.readlines():
        if not line.startswith('#'):  # comments

            first_space_index = line.find(' ')
            # username: the line up to the first space
            username = line[:first_space_index]
            # password: the line after the first space
            password = line[first_space_index + 1:]

            return username, password
    assert False, "no username and password found in conf.txt!"

gmail_user, gmail_pwd = get_username_and_password()
logged_in = False
mailServer = None

def login():
    global mailServer, logged_in
    assert not logged_in
    print 'connecting to smtp server'
    #587 or 465 should work
    mailServer = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    print 'running ehlo()'
    mailServer.ehlo()
    print 'logging in'
    mailServer.login(gmail_user, gmail_pwd)
    logged_in = True

def logout():
    global mailServer, logged_in
    assert logged_in
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
    logged_in = False

def mail(to, text, subject=None):
    global mailServer, logged_in
    assert logged_in
    print 'composing message'
    msg = MIMEText(text)

    msg['From'] = gmail_user
    msg['To'] = to
    if subject:
        msg['Subject'] = subject

    print 'sending email'
    mailServer.sendmail(gmail_user, to, msg.as_string())
    print 'done sending mail'

#example
#login()
#mail("test@mailinator.com",
#    "Hello from python!",
#    "This is a email sent with python")
#logout()
