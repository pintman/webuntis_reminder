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
    school='bk-bochum').login()

# do some output
for k in s.klassen():
    print(k.name)

date1 = datetime.date(year=2017,month=5,day=8)
date2 = date1 + datetime.timedelta(2)
print("from", date1, "to", date2)

bak = s.teachers().filter(name="BAK")[0]

tt = s.timetable(start=date1,end=date2,teacher=bak)
for po in tt:
    if (len(po.klassen)==1 and
        len(po.rooms)==1 and
        len(po.subjects)==1 and
        len(po.teachers)==1):
        print(po.start,
              #po.end,
              po.klassen[0].name,
              po.teachers[0].name,
              po.rooms[0].name,
              po.subjects[0].name)

print("== table ==")
table = tt.to_table()
for row in table:
    #print(row)
    for hour in row:
        print(hour, end="")
    print("")
        
s.logout()
