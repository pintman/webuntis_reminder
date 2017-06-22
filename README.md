Webuntis Reminder
=================

A reminder service for cancelled lessons in a WebUntis time table.


Installation
------------

    $ pip install -r requirements
    $ cp config.ini.sample config.ini
    
Change `config.ini` to reflect your configuration.
    
You can run the reminder once

    $ python reminder.py
    
Or you can create a cronjob that allows for recurring invocations.

