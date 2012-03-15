#!/usr/bin/env python
# coding: utf-8

from jzsadmin import create_app
from jzsadmin.models import User

from flaskext.script import Server, Shell, Manager, Command, prompt_bool


manager = Manager(create_app('dev.cfg'))

manager.add_command("runserver", Server('0.0.0.0',port=8080))

@manager.option('-u', '--username', dest='name', type=str)
@manager.option('-p', '--password', dest='passwd', type=str)
@manager.option('-r', '--role', dest='role', default=100, type=int)
def adduser(name, passwd, role):
    user = User(name=name, password=passwd)
    user.save()
    print 'Created'

if __name__ == "__main__":
    manager.run()
