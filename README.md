Webuntis Reminder
=================

A reminder service for cancelled lessons in a WebUntis time table.


Installation
------------

    $ pip install -r requirements
    $ cp config.ini.sample config.ini
    
Change `config.ini` to reflect your configuration.
    
Usage
-----

You can run the reminder once or recurring in a cronjob. To run it once, just
invoke it with python.

    $ RECIPIENT=user@example.com python reminder.py
    
Or you can create a cronjob that allows for recurring invocations.

    $ conjob -e
    
