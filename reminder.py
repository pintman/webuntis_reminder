
# from https://python-webuntis.readthedocs.io/en/latest/

import webuntis
import configparser
import logging
import locale
import datetime
import os
import functools

import smtplib
from email.message import EmailMessage


class Mailer:
    def __init__(self, smtp_server, smtp_user, smtp_pass, from_, to):
        self.smtp_server = smtp_server
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.from_ = from_
        self.to = to

    def send_mail(self, subject, body):
        msg = EmailMessage()
        msg.add_header("X-Mailer", "webuntisreminder")
        msg['Subject'] = subject
        msg['From'] = self.from_
        msg['To'] = self.to
        msg.set_content(body)

        logging.debug("sending mail: %s", body)
        s = smtplib.SMTP(self.smtp_server)
        s.login(self.smtp_user, self.smtp_pass)
        s.send_message(msg)
        s.quit()


class FilteredTimetable:
    def __init__(self, session, klasse, days, code, use_cache=True):
        """Creating a filtered table for the given class.

        :param session: webuntis session used for creating the timetable
        :param klasse: create table for this klasse.
        :param days: starting from today and up to so many days into the future.
        :param code: One of None, "cancelled" or "irregular"
        """
        self.code = code
        self.klasse = klasse
        self.days = days

        date1 = datetime.date.today()
        # date1 = datetime.date(year=2017, month=7, day=6)
        date2 = date1 + datetime.timedelta(days=days)

        klasse_object = session.klassen().filter(name=klasse)[0]
        logging.debug("creating time table for %s", klasse)
        pos = session.timetable(start=date1, end=date2,
                                klasse=klasse_object,
                                from_cache=use_cache)
        pos = list(pos)
        # filtering period objects that conform to the given code
        self.period_objects = [po for po in pos if po.code == code]
        self.period_objects.sort(key=lambda po: po.start)

    def send_via_mail(self, mailer, subject, body_template):
        """Send the filtered table via mail.

        :param mailer: A mail used for Sending
        :param subject: A subject line.
        :param body_template: A template string that contains placeholders
            'days' and 'klasse' which will be substituted when sending.
        """

        body = body_template.format(klasse=self.klasse, days=self.days)

        logging.debug("traversing %s PeriodObjects in session result.",
                      len(self.period_objects))
        for po in self.period_objects:  # po is a PeriodObject
            subj = functools.reduce(
                lambda acc, s: acc+s.name + " " + s.long_name,
                po.subjects, "")

            # more about specifiers for date formats
            # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
            date = po.start.strftime("%c")
            body += " {start} {su}\n".format(
                start=date, su=subj)  # , t=teachr, r=room)

        mailer.send_mail(subject, body)

    def is_empty(self):
        return len(self.period_objects) == 0


def main():
    # setting locale to the default language
    # this is used for the date format in the mails.
    # https://docs.python.org/3/library/locale.html#locale.setlocale
    locale.setlocale(locale.LC_ALL, '')

    logging.debug("reading credentials from config file")
    config = configparser.ConfigParser()
    config.read("config.ini")
    cred = config["credentials"]

    logging.debug("checking environment variables")
    days = int(os.getenv("DAYS", 5))
    code = os.getenv("CODE", "cancelled")
    recipient = os.getenv("RECIPIENT", None)

    if recipient is None:
        print("Provide a recipient in env var RECIPIENT")
        exit(1)

    logging.debug("creating session object and connecting")
    sess = webuntis.Session(
        username=cred["username"],
        password=cred["password"],
        server=cred['server'],
        useragent="WebUntis Reminder",
        school=cred['school'])
    sess.login()

    logging.debug("creating mailer")
    mailconf = config['mail']
    mailer = Mailer(mailconf['host'], mailconf['user'], mailconf['pass'],
                    mailconf['sender'], recipient)

    mailbody_template = """
    Der folgende Unterricht fällt für die {klasse} 
    in den folgenden {days} Tagen aus.
    
"""
    for klasse in sess.klassen():
        logging.debug("Checking Klasse %s", klasse.name)

        timet = FilteredTimetable(sess, klasse.name, days, code)
        if not timet.is_empty():
            logging.debug("sending mail for %s", klasse.name)
            timet.send_via_mail(mailer, "Unterrichtsausfall für " + klasse.name,
                                mailbody_template)

    sess.logout()


if __name__ == "__main__":
    logging.basicConfig(
        filename="webuntis_reminder.log",
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(module)s %(funcName)s():%(message)s')

    main()
