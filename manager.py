#!/usr/bin/env python
# coding: utf-8

from jzsadmin import create_app
from jzsadmin.models import User, Entry

from flaskext.script import Server, Shell, Manager, Command, prompt_bool


manager = Manager(create_app('dev.cfg'))

manager.add_command("runserver", Server('0.0.0.0',port=8080))

@manager.option('-u', '--username', dest='name', type=str)
@manager.option('-p', '--password', dest='passwd', type=str)
@manager.option('-r', '--role', dest='role', default=100, type=int)
def adduser(name, passwd, role):
    user = User(name=name, password=passwd, role=role)
    user.save()
    print 'Created'

@manager.option('-c', '--city', dest='city', type=str)
@manager.option('-o', '--operation', dest='op', type=str)
def status(city, op):
    if op not in ('wait', 'block', 'show'): 
        print "The status not allow"
    for e in Entry.query.filter(Entry.city_label==city):
        e.city_label = op
        e.save()
    print "The task Done."

if __name__ == "__main__":
    manager.run()
