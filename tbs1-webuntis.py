import webuntis
import configparser

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

for k in s.klassen():
    print(k.name)

    
s.logout()
