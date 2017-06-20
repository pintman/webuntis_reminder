
# from https://python-webuntis.readthedocs.io/en/latest/

import webuntis
import configparser
import datetime
import os
import functools

import smtplib
from email.message import EmailMessage


class Mailer:
    def __init__(self, smtp_server, smtp_user, smtp_pass, from_, to, subject):
        self.smtp_server = smtp_server
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.from_ = from_
        self.to = to
        self.subject = subject

    def send_mail(self, body):
        msg = EmailMessage()
        msg.add_header("X-Mailer", "webuntisreminder")
        msg['Subject'] = self.subject
        msg['From'] = self.from_
        msg['To'] = self.to
        msg.set_content(body)

        s = smtplib.SMTP(self.smtp_server)
        s.login(self.smtp_user, self.smtp_pass)
        s.send_message(msg)
        s.quit()


class Timetable:
    def __init__(self, session, klasse, days, code):
        self.code = code
        self.klasse = klasse
        self.days = days
        
        date1 = datetime.date.today()
        # date1 = datetime.date(year=2017, month=7, day=6)
        date2 = date1 + datetime.timedelta(days=days)

        klasse_object = session.klassen().filter(name=klasse)[0]
        self.tt = session.timetable(start=date1, end=date2,
                                    klasse=klasse_object)
        self.tt = list(self.tt)
        self.tt.sort(key=lambda po: po.start)

    def send_via_mail(self, mailer):
        body = """Der folgende Unterricht fällt für die {0} in den folgenden {1} Tagen aus.\n\n""".format(
            self.klasse, self.days)

        for po in self.tt:  # po is a PeriodObject
            if po.code == self.code:
                teachr = functools.reduce(
                    lambda acc, le: acc+le.surname,
                    po.teachers, "")
                room = functools.reduce(
                    lambda acc, r: acc+r.name,
                    po.rooms, "")
                subj = functools.reduce(
                    lambda acc, s: acc+s.name,
                    po.subjects, "")

                body += " {st} {su}\t{t}\t{r}\n".format(
                    st=str(po.start), su=subj, t=teachr, r=room)

        mailer.send_mail(body)


def main():
    # read credentials from config file
    config = configparser.ConfigParser()
    config.read("config.ini")
    cred = config["credentials"]

    # configuration via environment variables
    klasse = os.getenv("KLASSE", None)
    days = int(os.getenv("DAYS", 5))
    code = os.getenv("CODE", "cancelled")
    recipient = os.getenv("RECIPIENT", None)

    if klasse is None or recipient is None:
        print("Provide a class and recipi in env var KLASSE and RECIPIENT")
        exit(1)

    # create session object
    sess = webuntis.Session(
        username=cred["username"],
        password=cred["password"],
        server=cred['server'],
        useragent="WebUntis Test",
        school=cred['school'])
    sess.login()

    # create mailer
    mailconf = config['mail']
    mailer = Mailer(mailconf['host'], mailconf['user'], mailconf['pass'],
                    mailconf['sender'], recipient, "WebUntis Reminder")

    timet = Timetable(sess, klasse, days, code)
    timet.send_via_mail(mailer)

    sess.logout()



if __name__ == "__main__":
    main()
