
# from https://python-webuntis.readthedocs.io/en/latest/

import webuntis
import configparser
import datetime

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

    # create session object
    s = webuntis.Session(
        username=cred["username"],
        password=cred["password"],
        server='cissa.webuntis.com',
        useragent="WebUntis Test",
        school='bk-bochum')
    s.login()

    timet = Timetable(s)
    tt = timet.generate_tt("ITA15a", 5)

    for po in tt:
        print(po.start,
              "CO", po.code,
              # "TY",po.type,
              # po.end,
              "KL", [k.name for k in po.klassen],
              "LE", [t.name+" "+t.surname for t in po.teachers],
              "RA", [r.name for r in po.rooms],
              "SU", [s.name for s in po.subjects])
    s.logout()


if __name__ == "__main__":
    main()
