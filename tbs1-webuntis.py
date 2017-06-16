import webuntis
import configparser
import datetime

# from https://python-webuntis.readthedocs.io/en/latest/

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

"""
# do some output
for d in s.subjects():
    print("Subject ", d.name, d.long_name)

for k in s.klassen():
    print("Klasse", k.name)
"""

tod = datetime.date.today()
date1 = datetime.date(year=2017, month=7, day=6)
date2 = date1 + datetime.timedelta(days=0)
print("from", date1, "to", date2)

# bak = s.teachers().filter(name="BAK")[0]
klasse = s.klassen().filter(name="ITF15a")[0]

tt = s.timetable(start=date1, end=date2, klasse=klasse)

for po in tt:
    print(po.start,
          "CO", po.code,
          # "TY",po.type,
          # po.end,
          "KL", [k.name for k in po.klassen],
          "LE", [t.name+" "+t.surname for t in po.teachers],
          "RA", [r.name for r in po.rooms],
          "SU", [s.name for s in po.subjects])

"""
print("== table ==")
table = tt.to_table()
for row in table:
    # print(row)
    for hour in row:
        print(hour, end="")
    print("")
"""
s.logout()
