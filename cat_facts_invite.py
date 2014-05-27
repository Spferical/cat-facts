#!/usr/bin/python2

import sendmail
import sys
import sendtext

def send_invite(email):
    assert sendmail.logged_in
    print 'Sending email to ' + email + '...'

    sendmail.mail(email,
            "Thank you for signing up for Cat Facts! You will now receive fun facts about CATS! >o<")

def main():
    number = sys.argv[1]
    try:
        provider = sys.argv[2]
    except:
        provider = None

    if provider == None:
        for email in sendtext.get_possible_emails(number):
            send_invite(email)

    else:
        email = sendtext.get_email(number, provider)
        sendmail.login()
        send_invite(email)
        sendmail.logout()

if __name__ == '__main__':
    main()
