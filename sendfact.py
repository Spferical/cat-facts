#!/usr/bin/python2

import sendmail
import sendtext
import random
import gettext
import time
import datetime

def get_recipients():
    file = open("recipients.txt", 'r')
    recipients = []

    for line in file.readlines():

        # skip lines beginning with #
        # so they can be easily commented out
        if line[0] == "#": continue

        # otherwise, add the first two items of the line to the recipients list
        # (the number and provider)
        # comments can be added after the third items, and they won't matter
        recipients.append(tuple(line.split()[0:2]))

    file.close()
    return recipients

#recipients of the text, in [phone_number, provider] format
recipients = get_recipients()

def get_entire_file_text(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    return content


def get_random_message():
    return gettext.get_text()


def main():

    print 'sendfact.py running at', str(datetime.datetime.now())
    message = get_random_message()
    messages = sendtext.split_text(message)

    sendmail.login()

    for message in messages:

        print 'sending \"' + message + '\"'

        #send it
        for (number, provider) in recipients:
            #get the email to use
            email = sendtext.get_email(number, provider)

            print 'Sending email to ' + email + '...'

            #send the thing
            sendmail.mail(email, message)

        time.sleep(5)

    sendmail.logout()

if __name__ == '__main__':
    main()
