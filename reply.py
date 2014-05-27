import imaplib
import sendmail
import datetime
import email
import gettext
import sendtext
import time
import sendfact
import cat_facts_invite


def get_reply():
    """Creates a random message to reply with."""
    s = "<Command not recognized> "
    s += gettext.get_text()
    return s


def get_number_and_provider(email):
    """Gets a phone number and service provider from an email address."""
    # all seem to be of the form number@something
    #so we can find the number on the left of the '@'
    #and the provider from processing the something on the right of it
    at_index = email.find("@")
    if at_index == -1: return None, None
    number = email[:at_index]
    domain = email[at_index + 1:]
    reverse_gateways = {v : k for k, v in sendtext.gateways.items()}
    print reverse_gateways
    try:
        provider = reverse_gateways[domain]
    except KeyError:
        return None, None
    return number, provider


def add_recipient_to_file(number, provider):
    file = open('recipients.txt', 'a')
    file.write(number + " " + provider + "\n")
    file.close()


def main():
    print 'reply.py running at', str(datetime.datetime.now())

    # login with imap and select the inbox
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(sendmail.gmail_user, sendmail.gmail_pwd)
    mail.list()
    mail.select("INBOX")

    # get all mail from today still in the inbox
    # does NOT include mail from any of the mailer daemons or post masters
    # (who send error messages for mail that was not received)
    #date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
    #result, data = mail.uid('search', None, '(SENTSINCE {date} NOT FROM "mailer-daemon@googlemail.com" NOT FROM "post_master@vtext.com" NOT FROM "MAILER_DAEMON@email.uscc.net")'.format(date=date))
    result, data = mail.uid('search', None, '(NOT FROM '
            '"mailer-daemon@googlemail.com" NOT FROM "post_master@vtext.com" '
            'NOT FROM "MAILER_DAEMON@email.uscc.net")')

    #login in preparation for sending the email via smtp
    sendmail.login()

    #reply to all mail from today
    for id in data[0].split():

        #get the email for each uid
        typ, data = mail.uid("fetch", id, '(RFC822)')
        raw_email = data[0][1]

        #get a nice interface for the mail via the email library
        message = email.message_from_string(raw_email)
        # with it, get who sent the email
        sender = message['From']

        # debug printing
        print "Got email!"
        print 'Sender=' + sender

        # see if we this is a new person / not in the recipient list
        number, provider = get_number_and_provider(sender)
        print number, provider
        if not ((number, provider) in sendfact.recipients):
            if number:
                #this person text-messaged
                # add them to the recipient list
                add_recipient_to_file(number, provider)
                sendfact.recipients.append((number, provider))
                # also give them a welcome message!
                print 'sending invite to ' + sender
                cat_facts_invite.send_invite(sender)

        else:
            # we know this person
            # get a reply and send it in text messages
            print "replying to this person (we know them)"
            for reply_part in sendtext.split_text(get_reply()):
                #debug output
                print reply_part

                sendmail.mail(sender, reply_part)
                time.sleep(2)

        #move the email to archive so we don't reply to it again
        #(in gmail, by default, when a mail is deleted via imap, it is archived)
        mail.uid('store', str(id), '+FLAGS', r'(\Deleted)')
        mail.expunge()

    #logout of smtp
    sendmail.logout()

    #logout of imap
    mail.close()
    mail.logout()

if __name__ == '__main__':
    main()
