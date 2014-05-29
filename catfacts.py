import random
import time
import datetime
import email
import smtplib
import imaplib
import textwrap
from email.utils import parseaddr
from email.MIMEText import MIMEText


# 160 is the standard, but I've had texts cut off with it
# it might include the length of the email we're sending from
# 140 should be safe?
TEXT_MESSAGE_SIZE = 140

# too small and message parts arrive not in order
DELAY_BETWEEN_MESSAGE_PARTS = 5 # in seconds

# message sent when inviting someone to cat facts
# assumed to be small enough for one text message
INVITE_MESSAGE = "Thank you for signing up for Cat Facts! You will now "\
    "receive fun facts about CATS! >o<"


text_gateways = {
    # "carriername" : "whatever.com"
    # some commented out because I don't know anyone who uses them
    'verizon' : 'vtext.com',
    'att' : 'txt.att.net',
    'at&t' : 'txt.att.net',
    'sprint' : 'messaging.sprintpcs.com',
    #'alltel' : 'message.alltel.com',
    #'boost' : 'myboostmobile.com',
    #'nextel': 'messaging.nextel.com',
    #'t-mobile' : 'tmomail.net',
    #'tmobile' : 'tmomail.net',
    #'uscellular' : 'email.uscc.net',
    #'us cellular' : 'email.uscc.net',
    #'virgin mobile' : 'vmobl.com'
}


# like the above, but in reverse
# includes some additional domains that we may be sent messages from
reverse_gateways = {
    'vtext.com' : 'verizon',
    'vzwpix.com' : 'verizon',
    'txt.att.net' : 'att' ,
    'messaging.sprintpcs.com' : 'sprint',
    'message.alltel.com' : 'alltel',
    'myboostmobile.com' : 'boost',
    'messaging.nextel.com' : 'nextel',
    'tmomail.net' : 't-mobile',
    'email.uscc.net' : 'us cellular',
    'vmobl.com' : 'virgin mobile',
}


def get_phone_email(phone_number, provider):
    if provider in text_gateways.keys():
        return phone_number + '@' + text_gateways[provider]
    raise NotImplementedError, "I don't know how to handle " + provider +\
        " yet as a provider"


def get_possible_emails(phone_number):
    return [phone_number + '@' + domain
            for domain in set(text_gateways.values())]


def split_text(text):
    """Splits a text into messages of TEXT_MESSAGE_SIZE characters"""
    return textwrap.wrap(text, width=TEXT_MESSAGE_SIZE)

def get_phone_recipients():
    file = open("numbers.txt", "r")
    recipients = []

    for line in file.readlines():
        # skip lines beginning with # (fror easy commenting-out)
        if line[0] == '#':
            continue

        # otherwise, add the first two items of the line to the recipients list
        # (number, provider)
        # or (email_address, 'email')
        recipients.append(tuple(line.split()[0:2]))

    file.close()
    return recipients


def get_email_recipients():
    file = open("emails.txt", "r")
    recipients = []

    for line in file.readlines():
        # skip lines beginning with # (fror easy commenting-out)
        if line[0] == '#':
            continue

        recipients.append(line)

    file.close()
    return recipients



def get_nonwhitespace_lines_from_file(filename):
    f = open(filename, mode='r')
    lines = f.readlines()
    f.close()

    #return all lines that are not empty or whitespace
    return [line for line in lines if not (line == '' or line.isspace())]


def get_random_fact():
    # get a random fact
    lines = get_nonwhitespace_lines_from_file('facts.txt')
    return random.choice(lines)


def get_random_promo():
    lines = get_nonwhitespace_lines_from_file('promos.txt')
    return random.choice(lines)


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


def login_to_gmail(username, password):
    # ports 587 or 465 should work
    mail_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    mail_server.ehlo()
    mail_server.login(username, password)
    return mail_server


def logout(mail_server):
    mail_server.close()


def mail(username, to, text, subject, mail_server):
    msg = MIMEText(text)

    msg['From'] = username
    msg['To'] = to
    if subject:
        msg['Subject'] = subject

    print 'sending email to', to
    mail_server.sendmail(username, to, msg.as_string())


def send_invite(username, email_or_number, provider, mail_server):
    print 'sending invite to', email_or_number, provider
    if provider == 'email':
        email = email_or_number
        subject = "Cat Facts"
    else:
        number = email_or_number
        email = get_phone_email(number, provider)
        subject = None
    mail(username, email, INVITE_MESSAGE, subject, mail_server)


def send_fact():
    fact = get_random_fact()
    promo = get_random_promo()
    message = ' '.join((fact, promo))
    username, password = get_username_and_password()
    mail_server = login_to_gmail(username, password)

    # send all emails
    print 'message being sent over email: ', message
    for email in get_email_recipients():
        mail(username, email, message, "Cat Facts", mail_server)

    # send all texts
    messages = split_text(message)
    phone_recipients = get_phone_recipients()
    for message in messages:
        print 'message being sent over SMS: ', message
        for number, provider in phone_recipients:
            email = get_phone_email(number, provider)
            mail(username, email, message, None, mail_server)
        time.sleep(DELAY_BETWEEN_MESSAGE_PARTS)


def get_number_and_provider(email):
    """Gets a phone number and service provider from an email address."""
    # all seem to be of the form number@something
    # so we can find the number on the left of the '@'
    # and the provider from processing the something on the right of it
    at_index = email.find("@")
    if at_index == -1:
        return None, None
    number = email[:at_index]
    domain = email[at_index + 1:]
    try:
        provider = reverse_gateways[domain]
    except KeyError:
        return None, None
    return number, provider


def add_phone_recipient_to_file(number, provider):
    file = open('numbers.txt', 'a')
    file.write("%s %s\n" % (number, provider))
    file.close()


def add_email_recipient_to_file(email):
    file = open('emails.txt', 'a')
    file.write(email + '\n')
    file.close()


def get_reply_message():
    fact = get_random_fact()
    promo = get_random_promo()
    return ' '.join(('<command not recognized>', fact, promo))


def reply():
    fact = get_random_fact()
    promo = get_random_promo()
    username, password = get_username_and_password()

    email_recipients = get_email_recipients()
    phone_recipients = get_phone_recipients()

    imap_mail = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_mail.login(username, password)
    imap_mail.list()
    imap_mail.select("INBOX")

    # get all mail in the inbox, not including that from mailer daemons/post
    # masters (which send messagess for mail that was not received)
    # TODO: find better way to ignore mailer daemon/post master mail
    result, data = imap_mail.uid('search', None, '(NOT FROM '
            '"mailer-daemon@googlemail.com" NOT FROM "post_master@vtext.com" '
            'NOT FROM "MAILER_DAEMON@email.uscc.net")')

    # login to smtp in preparation for sending mail
    mail_server = login_to_gmail(username, password)

    for id in data[0].split():

        #get the email for each uid
        typ, data = imap_mail.uid("fetch", id, '(RFC822)')
        raw_email = data[0][1]

        #get a nice interface for the mail via the email library
        message = email.message_from_string(raw_email)
        # with it, get who sent the email
        sender = message['From']

        # extract /just/ the plain address from the address
        # e.g. foo@gmail.com instead of Foo Bar <foo@gmail.com>
        sender = parseaddr(sender)[1]

        # debug printing
        print "Got email! Sender=" + sender

        # see if we this is a new person / not in the recipient list
        number, provider = get_number_and_provider(sender)

        print number, provider

        if ((number, provider) in phone_recipients):
            # we know this number
            # get a reply and send it in text messages
            print "replying to this person (we know them)"
            for reply_part in split_text(get_reply_message()):
                #debug output
                print reply_part

                mail(username, sender, reply_part, None, mail_server)
                time.sleep(DELAY_BETWEEN_MESSAGE_PARTS)
        elif sender in email_recipients:
            # we know this email
            # get a reply and email it
            mail(username, sender, get_reply_message(), "Cat Facts",
                 mail_server)

        else:
            # we don't know this person
            if number:
                # this person text-messaged
                # add them to the recipient list
                add_phone_recipient_to_file(number, provider)
                phone_recipients.append((number, provider))
                # also give them a welcome message!
                send_invite(username, number, provider,  mail_server)
            else:
                # this person emailed, probably
                # add them to the recipient list
                add_email_recipient_to_file(sender)
                email_recipients.append(sender)
                # also give them a welcome message!
                send_invite(username, sender, 'email', mail_server)


        # move the email to archive so we don't reply to it again
        # (in gmail, by default, when a mail is deleted via imap, it is archived)
        imap_mail.uid('store', str(id), '+FLAGS', r'(\Deleted)')
        imap_mail.expunge()

    #logout of smtp
    logout(mail_server)

    #logout of imap
    imap_mail.close()
    imap_mail.logout()


def invite_number(number, provider):
    username, password = get_username_and_password()
    mail_server = login_to_gmail(username, password)
    add_phone_recipient_to_file(number, provider)
    send_invite(username, number, provider, mail_server)


def invite_email(email):
    username, password = get_username_and_password()
    mail_server = login_to_gmail(username, password)
    add_email_recipient_to_file(email)
    send_invite(username, email, 'email', mail_server)


def main():
    from sys import argv
    action = argv[1]
    if action == 'send':
        print 'catfacts sending at %s' % datetime.datetime.now()
        send_fact()
    elif action == 'reply':
        print 'catfacts replying at %s' % datetime.datetime.now()
        reply()
    elif action == 'invite_text':
        print 'catfacts inviting text at %s' % datetime.datetime.now()
        number = argv[2]
        provider = argv[3]
        invite_number(number, provider)
    elif action == 'invite_email':
        print 'catfacts inviting email at %s' % datetime.datetime.now()
        email = argv[2]
        invite_email(email)


if __name__ == '__main__':
    main()