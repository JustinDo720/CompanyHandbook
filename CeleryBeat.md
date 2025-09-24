# Retracing Django Celery + Beat 

## Table of Contents
- [Retracing Django Celery + Beat](#retracing-django-celery--beat)
  - [Table of Contents](#table-of-contents)
  - [Recap](#recap)
  - [Requirements](#requirements)
  - [Setting up Celery.py](#setting-up-celerypy)
    - [Celery Beat + App in INSTALLED\_APP](#celery-beat--app-in-installed_app)
    - [Environment + Settings](#environment--settings)
    - [Broker + Tasks](#broker--tasks)
    - [Setting up Init](#setting-up-init)
    - [Creating a job / task](#creating-a-job--task)
    - [Setting up CRON Schedule](#setting-up-cron-schedule)
    - [Running Up Our Application](#running-up-our-application)
  - [Extra](#extra)
    - [Django Custom Command](#django-custom-command)
    - [Crontab Schedule](#crontab-schedule)
    - [Scheduling](#scheduling)
    - [Timezone](#timezone)


## Recap 

**Celery** helps us schedule **periodic tasks** via **Beat**. We use **Crontab** to set up some time for us to run a specific job/operation/task. This is very much similar to the **ETL** pipeline where we used **Dagster** to register our jobs to talk to our Snowflake

This *README* Serves as a recap + referesher as to how do we integrate this tool into **Django**  

## Requirements 

We need a **Broker** something that we've seen with **Microservices** with Kafka but this Broker is more for sending a topic via **SQS**.

**Locally** we'll be using **RabbitMQ**

---

**Celery + Beat**
- `pip install celery; django-celery-beat`

**RabbitMQ** (Migrating to SQS later)
- `docker pull rabbitmq:3-management`
- `docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`

---

**Running Celery**
- `celery -A project_name worker -l info --pool=solo` -> (Running Celery as a worker)

---

## Setting up Celery.py

### Celery Beat + App in INSTALLED_APP

```py
INSTALLED_APPS = [
    # Default apps
    ....
    # My apps
    'app_name',
    'django_celery_beat'
]
```
---

### Environment + Settings

`project_root/settings.py/celery.py`
```py
"""
    We need to tell Celery where our Django settings are BEFORE we create a Celery Instance 
        - Importing OS 
        - Grabbing Settings from Conf 
"""
import os 
from django.conf import settings 
from celery import Celery

# Setting the environement 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings')

# Building Celery Instance 
celery_app = Celery('project_name')
celery_app.config_from_object(settings, namespace='CELERY')
```
--- 

### Broker + Tasks

*project_root/settings.py/celery.py*
```py
"""
    Using our celery instance that we've created
        - Set the broker url 
        - Auto Discovering Tasks (Searching for @shared_task)
"""
# RabbitMQ host running on local Docker Container
celery_app.conf.broker_url = "amqp://guest:guest@localhost:5672//"
celery_app.autodiscover_tasks()
```

---

### Setting up Init 

`project_root/__init__.py`
```py
"""
    Importing from celery to discover the tasks
"""
from .celery import celery_app

# Makes sure it's available when Django Starts
__all__ = ('celery_app',)
```

---

### Creating a job / task 

`app/tasks.py`
```py
"""
    Ideally we would create a custom command in Django:
        - py manage.py custom_command 

    Then we use the `call_command` from django.core.management to run our custom_command at a certain period 
"""
# Assume you have made a custom django command: check_handbook_dupes
from __future__ import absolute_import, unicode_literals    # Make sure this import is first
from celery import shared_task
from django.core.management import call_command 

@shared_task
def check_dupes_tasks():
    # Run: py manage.py check_handbook_dupes --> custom Django Command
    call_command('check_handbook_dupes')
```

---

### Setting up CRON Schedule 

`project/settings.py`
```py
""""
    Based on the time you want to set, we could set a frequency to that schedule task
"""
from celery.schedules import crontab

-- Rest of Settings.py --

CELERY_BEAT_SCHEDULE = {
    'clear-handbook-dupes': {
        'task': 'project_app.tasks.check_dupes_tasks',
        'schedule': crontab(hour=0, minute=0), # Run daily at midnight
        # 'args': ('',),    ## If applicable
    }
}
```

### Running Up Our Application 

```bash
# Migrate our Cron application (for periodic tasks)
py manage.py migrate

# Running Celery 
celery -A project_name worker -l info --pool=solo

# Running Beat (Seperate CMD)
celery -A project_name beat -l info 

# Running our Django (Seperate CMD)
py manage.py runserver
```

## Extra 

I mentioned **Django Custom Command** so let's take a look on how to set one up for our **Tasks**

### Django Custom Command 

**Create Path**

```
app/management/commands
    - task_1.py
    - task_2.py
    - task_n.py
```
1) Under your app, we'll create a path `management/commands` then add your **task files** there to use with `call_command()` 


`app/management/commands/task_1.py`
```py
# Inherting from Parent BaseCommand Class 
from django.core.management import BaseCommand

class Command(BaseCommand):
    help = "Help text"

    # Dealing with arguments (OPTIONAL)
    def add_arguments(self, parser):
        parser.add_argument('-f', '--flag', type=str,)

    # The logic behind the functionality of our command
    def handle(self, *args, **kwargs):
        optional_arg = kwargs['flag']   # Flag is the name that we put --flag
        # Logic Goes here
```
1) This lets us run: `py manage.py task_1` and (script-wise): `call_command('task_1', flag=flag_argument)`


### Crontab Schedule

```py
crontab() # Execute every minute.

crontab(minute=0, hour=0) # Execute daily at midnight.

crontab(minute=0, hour='*/3') # Execute every three hours: midnight, 3am, 6am, 9am, noon, 3pm, 6pm, 9pm.

crontab(minute=0, hour='0,3,6,9,12,15,18,21') # Same as previous.

crontab(minute='*/15') # Execute every 15 minutes.

crontab(day_of_week='sunday') # Execute every minute (!) at Sundays.

crontab(minute='*', hour='*', day_of_week='sun') # Same as previous.

crontab(minute='*/10', hour='3,17,22', day_of_week='thu,fri') # Execute every ten minutes, but only between 3-4 am, 5-6 pm, and 10-11 pm on Thursdays or Fridays.

crontab(minute=0, hour='*/2,*/3') # Execute every even hour, and every hour divisible by three. This means: at every hour except: 1am, 5am, 7am, 11am, 1pm, 5pm, 7pm, 11pm

crontab(minute=0, hour='*/5') # Execute hour divisible by 5. This means that it is triggered at 3pm, not 5pm (since 3pm equals the 24-hour clock value of “15”, which is divisible by 5).

crontab(minute=0, hour='*/3,8-17') # Execute every hour divisible by 3, and every hour during office hours (8am-5pm).

crontab(0, 0, day_of_month='2') # Execute on the second day of every month.

crontab(0, 0, day_of_month='2-30/2') # Execute on every even numbered day.

crontab(0, 0, day_of_month='1-7,15-21') # Execute on the first and third weeks of the month.

crontab(0, 0, day_of_month='11', month_of_year='5') # Execute on the eleventh of May every year.

crontab(0, 0, month_of_year='*/3') # Execute every day on the first month of every quarter.
```

### Scheduling

When changing something about the schedule make sure you remove:

`celerybeat-schedule` files

### Timezone 

Celery Timezone is a big thing it's by default: **UTC** but you could change it with:

```py
# --- DEPRECATED ---
# settings.py
CELERY_TIMEZONE = 'America/New_York'
CELERY_ENABLE_UTC = False

# --- Celery 5 / 6 ---
# project_name/celery.py
app.conf.timezone = 'America/New_York'
app.conf.enable_utc = False 

"""
You're looking for a log info in BEAT

[2025-09-22 16:45:23,477: INFO/MainProcess] beat: Starting...
[2025-09-22 16:45:23,517: WARNING/MainProcess] Reset: Timezone changed from 'UTC' to 'America/New_York'

"""
```
