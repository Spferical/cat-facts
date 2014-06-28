import random
import time
import datetime
import email
import smtplib
import imaplib
import textwrap
import shutil
import tempfile
import traceback
import sys
import argparse
import os.path
import re
from email.utils import parseaddr
from email.MIMEText import MIMEText


# 160 is the standard, but I've had texts cut off with it
# it might include the length of the email we're sending from
# 140 should be safe?
# this may be because it includes the name of the sender
TEXT_MESSAGE_SIZE = 140

# too small and message parts arrive not in order
# too long and message parts arrive more separately...
DELAY_BETWEEN_MESSAGE_PARTS = 10 # in seconds

# messages sent when inviting someone to cat facts
# assumed to be small enough for one text message
_INVITE_MESSAGE = "Thank you for signing up for Cat Facts! You will now "\
    "receive {rlist} fun facts about CATS! >o<"

INVITE_MESSAGES = {
    'hourly' : _INVITE_MESSAGE.format(rlist='hourly'),
    'daily' : _INVITE_MESSAGE.format(rlist='daily'),
}

UNSUBSCRIBE_MESSAGE = "Unsubscribe? You gotta be kitten me! "\
    "You are now unsubscribed from Cat Facts."


INVITE_USAGE_MESSAGE = "<invalid arguments> to invite someone, either send " \
    "'invite sms <number> <provider>' or 'invite email <address>'"


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

def get_phone_recipients(rlist):
    recipients = []
    file_path = os.path.join('sms', rlist + '.txt')

    for line in get_nonwhitespace_lines_from_file(file_path):
        # skip lines beginning with # (fror easy commenting-out)
        if line[0] == '#':
            continue

        # otherwise, add the first two items of the line to the recipients list
        # (number, provider)
        # or (email_address, 'email')
        recipients.append(tuple(line.split()[0:2]))

    return recipients


def get_email_recipients(rlist):
    recipients = []
    file_path = os.path.join('email', rlist + '.txt')

    for line in get_nonwhitespace_lines_from_file(file_path):
        # skip lines beginning with # (fror easy commenting-out)
        if line[0] == '#':
            continue

        recipients.append(line)

    return recipients



def get_nonwhitespace_lines_from_file(filename):
    f = open(filename, mode='r')
    lines = f.readlines()
    f.close()

    #return all lines that are not empty or whitespace
    return [line.rstrip('\n') for line in lines
            if not (line == '' or line.isspace())]


def get_random_fact():
    # get a random fact
    lines = get_nonwhitespace_lines_from_file('facts.txt')
    return random.choice(lines)


def get_random_promo():
    lines = get_nonwhitespace_lines_from_file('promos.txt')
    return random.choice(lines)


def get_username_and_password():
    for line in get_nonwhitespace_lines_from_file('conf.txt'):
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


def send_invite(username, email_or_number, provider, mail_server,
                rlist='daily'):
    print 'sending invite to', email_or_number, provider
    if provider == 'email':
        email = email_or_number
        subject = "Cat Facts"
    else:
        number = email_or_number
        email = get_phone_email(number, provider)
        subject = None
    mail(username, email, INVITE_MESSAGES[rlist], subject, mail_server)


def send_fact(rlist):
    message = get_random_fact()
    if random.random() < 0.4:
        promo = get_random_promo()
        message = ' '.join((message, promo))
    username, password = get_username_and_password()
    mail_server = login_to_gmail(username, password)

    # send all emails
    print 'message being sent over email: ', message
    for email in get_email_recipients(rlist):
        mail(username, email, message, "Cat Facts", mail_server)

    # send all texts
    messages = split_text(message)
    phone_recipients = get_phone_recipients(rlist)
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


def add_phone_recipient_to_file(number, provider, rlist='daily'):
    file = open(os.path.join('sms', rlist + '.txt'), 'a')
    file.write("%s %s\n" % (number, provider))
    file.close()


def add_email_recipient_to_file(email, rlist='daily'):
    file = open(os.path.join('email', rlist + '.txt'), 'a')
    file.write(email + '\n')
    file.close()


def get_reply_message():
    fact = get_random_fact()
    promo = "Remember, text \"UnSuBsCrIbE\" at any time to unsubscribe "\
            "from Cat Facts!"
    return ' '.join(('<command not recognized>', fact, promo))


def remove_matching_lines_from_file(text, filename):

    # open the file and a temporary file
    f = open(filename, 'r')
    tmpfile = tempfile.NamedTemporaryFile(mode='w+t', delete=False)

    # write lines not containing the text to the temporary file
    for line in f:
        if not text in line:
            tmpfile.write(line)

    f.close()
    tmpfile.close()

    # replace the original file with the temporary (modified) file
    shutil.move(tmpfile.name, filename)


def get_command_from_text(text):
    # parse everything in lowercase
    text = text.lower()

    # returns a command and the arguments for that command, if any found
    # if none found, returns (None, [])
    command = None
    arguments = []

    for possible_command in ['unsubscribe', 'daily', 'hourly', 'invite',
                             'nuke_everything']:
        if possible_command in text:
            command = possible_command
            if command == 'invite':
                # search for an sms invite
                match = re.search("invite sms [0-9]{10} \w+", text)
                if match:
                    words = match.group().split()
                    number = words[2]
                    provider = words[3]
                    arguments = ['sms', number, provider]
                    break

                # search for an email address invite
                match = re.search("invite email \S+", text)
                if match:
                    words = match.group().split()
                    email = words[2]
                    arguments = ['email', email]
                    break
            break
    return command, arguments


def get_command_from_message(message):
    # go through each text part of the message and see if it includes the
    # word for a command
    # returns a command and the arguments for that command
    for part in message.walk():
        if part.get_content_type() in ('text/plain'): # TODO: parse 'text/html'
            message_text = part.get_payload()
            command, arguments = get_command_from_text(message_text)
            if command:
                return command, arguments
    # no command found
    return None, []


def nuke_everything():
    for rlist in ('daily', 'hourly'):
        for recipient_type in ('sms', 'email'):
            f = open(os.path.join(recipient_type, rlist + '.txt'), 'w')
            f.write("")


def remove_recipient_from_files(recipient, recipient_type):
    print 'removing...'

    for rlist in ('hourly', 'daily'):
        file_path = os.path.join(recipient_type, rlist + '.txt')
        if recipient_type == 'sms':
            number, provider = recipient
            remove_matching_lines_from_file(number, file_path)
        else:
            remove_matching_lines_from_file(recipient, file_path)


def reply():
    username, password = get_username_and_password()

    email_recipients = []
    phone_recipients = []
    for rlist in ('daily', 'hourly'):
        email_recipients.extend(get_email_recipients(rlist))
        phone_recipients.extend(get_phone_recipients(rlist))

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

        # find out if the message includes a command
        command, arguments = get_command_from_message(message)

        # extract /just/ the plain address from the address
        # e.g. foo@gmail.com instead of Foo Bar <foo@gmail.com>
        sender = parseaddr(sender)[1]

        # debug printing
        print "Got email! Sender=" + sender

        # see if we this is a new person / not in the recipient list
        number, provider = get_number_and_provider(sender)

        print number, provider

        if number:
            recipient_type = 'sms'
        else:
            recipient_type = 'email'

        if command == 'nuke_everything':
            nuke_everything()
        else:

            existing_recipient = (number, provider) in phone_recipients \
                or sender in email_recipients

            if existing_recipient:
                if command == 'unsubscribe':
                    print 'this recipient is unsubscribing :('

                    # remove recipient from all files
                    if recipient_type == 'sms':
                        remove_recipient_from_files(
                            (number, provider), recipient_type)
                    else:
                        remove_recipient_from_files(email, recipient_type)

                    # remove recipient from lists so we treat them properly
                    # if we receive another email near the same time
                    if recipient_type == 'email':
                        email_recipients.remove(sender)
                    else:
                        phone_recipients.remove((number, provider))

                    print 'replying with unsubscription message'
                    mail(username, sender, UNSUBSCRIBE_MESSAGE, None,
                         mail_server)

                elif command in ('hourly', 'daily'):
                    print 'this person wants %s cat facts' % command

                    # remove user from all groups he might have been part of
                    # previously
                    if recipient_type == 'sms':
                        remove_recipient_from_files(
                            (number, provider), recipient_type)
                    else:
                        remove_recipient_from_files(email, recipient_type)

                    # add the user to his new list
                    rlist = command
                    file_path = os.path.join(recipient_type, rlist + '.txt')
                    if recipient_type == 'sms':
                        add_phone_recipient_to_file(number, provider,
                                                    rlist=command)
                    else:
                        add_email_recipient_to_file(sender, rlist=command)

                    print 'replying with message'
                    text = "You will now receive %s cat facts." % command
                    mail(username, sender, text, None, mail_server)

                elif command == 'invite':
                    print 'this person wants to invite someone'

                    if len(arguments) == 0:
                        print "Insufficient arguments"
                        print "Sending invite usage message"
                        mail(username, sender, INVITE_USAGE_MESSAGE, None,
                            mail_server)
                    else:
                        method = arguments[0]
                        if method == 'sms':
                            print 'this person wants to invite via sms'
                            number, provider = arguments[1:2]
                            print 'inviting the number'
                            invite_number(number, provider)
                        elif method == 'email':
                            print 'this person wants to invite via email'
                            email_address = arguments[1]
                            print 'inviting the email'
                            invite_email(email_address)

                else:
                    # no command was detected
                    # get a reply and send it in text messages
                    print "replying to this message with command not found"
                    for reply_part in split_text(get_reply_message()):
                        #debug output
                        print reply_part

                        mail(username, sender, reply_part, None, mail_server)
                        time.sleep(DELAY_BETWEEN_MESSAGE_PARTS)

            else:
                # we don't know this person

                if command == 'unsubscribe':
                    # we'll just ignore an unknown recipient who wants to
                    # unsubscribe
                    pass

                else:
                    # this is a new person, so subscribe them!

                    # check if their message included a time preference
                    # or default to daily facts
                    if command in ('hourly', 'daily'):
                        rlist = command
                    else:
                        rlist = 'daily'

                    if recipient_type == 'sms':
                        # this person text-messaged
                        # add them to the recipient rlist
                        add_phone_recipient_to_file(number, provider,
                                                    rlist=rlist)
                        phone_recipients.append((number, provider))
                        # also give them a welcome message!
                        send_invite(username, number, provider,  mail_server)
                    else:
                        # this person emailed, probably
                        # add them to the recipient rlist
                        add_email_recipient_to_file(sender, rlist=rlist)
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


def invite_number(number, provider, rlist='daily'):
    username, password = get_username_and_password()
    mail_server = login_to_gmail(username, password)
    add_phone_recipient_to_file(number, provider, rlist)
    send_invite(username, number, provider, mail_server)


def invite_email(email, rlist='daily'):
    username, password = get_username_and_password()
    mail_server = login_to_gmail(username, password)
    add_email_recipient_to_file(email, rlist)
    send_invite(username, email, 'email', mail_server)


def main():
    parser = argparse.ArgumentParser(
        description = "Send cat facts via email and sms")

    subparsers = parser.add_subparsers(dest="action")

    send_parser = subparsers.add_parser("send", help="send messages")
    send_parser.add_argument(
        "list", help="list of users to send to",
        type=str)

    reply_parser = subparsers.add_parser(
        "reply", help="read messages and send replies")

    invite_parser = subparsers.add_parser(
        "invite", help="invite users to cat facts")
    invite_parser.add_argument(
        '-l', '--list', help="list to add the user to", default='daily',
        choices=['hourly', 'daily'])
    invite_subparsers = invite_parser.add_subparsers(dest="method")
    invite_sms_parser = invite_subparsers.add_parser(
        "sms", help="invite a cell phone number")
    invite_sms_parser.add_argument(
        "number", help="phone number to invite")
    invite_sms_parser.add_argument(
        "provider", help="phone service provider of number")
    invite_email_parser = invite_subparsers.add_parser(
        "email", help="invite an email address")
    invite_email_parser.add_argument(
        "address", help="email address to send facts to")

    args = parser.parse_args()

    if args.action == 'send':
        print 'catfacts sending to %s at %s' %\
            (args.list, datetime.datetime.now())
        send_fact(args.list)

    elif args.action == 'reply':
        print 'catfacts replying at %s' % datetime.datetime.now()
        reply()

    elif args.action == 'invite':
        print 'catfacts inviting via %s at %s' %\
            (args.method, datetime.datetime.now())

        if args.method == 'sms':
            number = args.number
            provider = args.provider
            invite_number(number, provider, rlist=args.list)

        elif args.method == 'email':
            email_address = args.address
            invite_email(email_address, rlist=args.list)


if __name__ == '__main__':
    main()
