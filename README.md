# cat-facts

This is a bot for regularly sending fun, free cat facts via email or sms. It
operates via an email account with SMTP access.

The bot does not cold-email anyone: only users who first email the bot will be
subscribed, and the bot will periodically remind them how to unsubscribe.

# How do I run this/I want to run my own free cat facts service

To get the bot running, create config.cfg, looking like follows. Username and
password should be to a gmail account accessible via SMTP (sadly, the url is
hardcoded in, but can easily be changed).

The email address specified as the alert recipient will be notified upon events
such as a user emailing the cat facts bot.

```
# config.txt
[Login]
username = catfacts@example.com
password = mee_wow

[Alert]
recipient = catfactsadmin@example.com
```

Then, create folders named 'sms' and 'email' in the cat facts directory.

Finally, setup cronjobs or similar to reply to emails and deliver facts like
the following:

```
#!/usr/bin/env bash
*/5 * * * * cd /path/to/CatFacts/ && python3 catfacts.py reply
0 * * * * cd /path/to/catfacts/CatFacts/ && python3 catfacts.py send hourly
0 0 * * * cd /path/to/catfacts/CatFacts/ && python3 catfacts.py send daily
```
