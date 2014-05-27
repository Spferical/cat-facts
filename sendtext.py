#!/usr/bin/python2

import sendmail
import textwrap

gateways = {
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

def get_email(phone_number, provider=None):
    if provider in gateways.keys():
        return phone_number + '@' + gateways[provider]
    elif provider == None:
        print "I don't know how to handle " + provider + " yet as a provider!"
        raise NotImplementedError

def get_possible_emails(phone_number):
    emails = []

    for domain in set(gateways.values()):
        emails.append(phone_number + '@' + domain)

    return emails

def split_text(text):
    """Splits a text into messages of 140 characters"""
    return textwrap.wrap(text, width=140)
