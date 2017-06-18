
# from https://python-webuntis.readthedocs.io/en/latest/

import webuntis
import configparser
import datetime
import os
import functools

import smtplib
from email.message import EmailMessage


class Mailer:
    def __init__(self, smtp_server, smtp_user, smtp_pass, klasse):
        self.smtp_server = smtp_server
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    def send_mail(self, from_, to, subject):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_
        msg['To'] = to

        s = smtplib.SMTP(self.smtp_server)
        s.login(self.smtp_user, self.smtp_pass)
        s.send_message(msg)
        s.quit()


class Timetable:
    def __init__(self, session):
        self.session = session

    def generate_tt(self, klasse, days):
        date1 = datetime.date.today()
        # date1 = datetime.date(year=2017, month=7, day=6)
        date2 = date1 + datetime.timedelta(days=days)

        klasse_object = self.session.klassen().filter(name=klasse)[0]
        tt = self.session.timetable(start=date1, end=date2,
                                    klasse=klasse_object)
        return tt


def main():
    # read credentials from config file
    config = configparser.ConfigParser()
    config.read("config.ini")
    cred = config["credentials"]

    # configuration via environment variables
    klasse = os.getenv("KLASSE", None)
    days = int(os.getenv("DAYS", 5))
    code = os.getenv("CODE", "cancelled")

    if klasse is None:
        print("Provide a class in EVN var KLASSE")
        exit(1)

    # create session object
    sess = webuntis.Session(
        username=cred["username"],
        password=cred["password"],
        server='cissa.webuntis.com',
        useragent="WebUntis Test",
        school='bk-bochum')
    sess.login()

    timet = Timetable(sess)
    tt = timet.generate_tt(klasse, days)
    # sorting result by start time
    tt = list(tt)
    tt.sort(key=lambda po: po.start)

    print(
        """Der folgende Unterricht fällt für die {0} in den folgenden {1} Tagen aus.""".format(
        klasse, days))

    for po in tt:
        if po.code == code:
            te = functools.reduce(
                lambda acc, le: acc+le.surname,
                po.teachers, "")
            ro = functools.reduce(
                lambda acc, r: acc+r.name,
                po.rooms, "")
            su = functools.reduce(
                lambda acc, s: acc+s.name,
                po.subjects, "")

            print(str(po.start) + " " + su,
                  te,
                  ro,
                  sep="\t")

    sess.logout()


if __name__ == "__main__":
    main()
