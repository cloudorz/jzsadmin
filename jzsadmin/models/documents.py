# coding: utf-8

import re, datetime, hashlib

from flask import g, abort
from werkzeug import cached_property
from flaskext.mongoalchemy import BaseQuery
from flaskext.principal import RoleNeed, UserNeed, Permission

from jzsadmin.ext import db
from jzsadmin.permissions import sa, normal


now = datetime.datetime.utcnow


def hash(data):
    return  hashlib.md5(data).hexdigest()


class UserQuery(BaseQuery):

    def from_identity(self, identity):
        user = self.get(identity.name)
        if user:
            identity.provides.update(user.provides)

        identity.user = user

        return user


class HashField(db.StringField):
    def set_value(self, instance, value, from_db=False):
        if from_db:
            super(HashField, self).set_value(instance, value)
        else:
            super(HashField, self).set_value(instance, str(hash(value)))


class User(db.Document):
    query_class = UserQuery

    BLOCK, NORMAL, ADMIN = 0, 100, 200

    name = db.StringField(max_length=20)
    password = HashField()
    role = db.EnumField(db.IntField(), BLOCK, NORMAL, ADMIN, default=NORMAL)

    def maybe_save(self, safe=None):
        try:
            self.save()
        except:
            abort(400)

    def check_password(self, value):
        return hash(value) == self.password

    class Permissions(object):
        def __init__(self, obj):
            self.obj = obj

        @cached_property
        def edit(self):
            return Permission(UserNeed(self.obj.pk)) & sa

        @cached_property
        def delete(self):
            return Permission(UserNeed(self.obj.pk)) & sa

    @cached_property
    def permissions(self):
        return Self.Permissions(self)

    @cached_property
    def provides(self):
        needs = [RoleNeed('auth'), UserNeed(self.pk)]

        if self.is_sa:
            needs.append(RoleNeed('admin'))

        return needs

    @property
    def is_sa(self):
        return self.role >= self.ADMIN

    @cached_property
    def pk(self):
        return str(self.mongo_id)

    @property
    def created_time(self):
        if self.has_id():
            return self.mongo_id.generation_time


class Entry(db.Document):

    PERN = 20

    title = db.StringField()
    brief = db.StringField()
    desc = db.StringField()
    city_label = db.StringField(max_length=30)
    address = db.StringField() 
    worktime = db.StringField()
    counter = db.DocumentField(Counter)
    _serviceitems = db.SetField(db_field="serviceitems", item_type=db.StringField())
    _serviceareas = db.SetField(db_field="serviceareas", item_type=db.StringField())
    _contracts = db.ListField(db_field="contracts", item_type=db.StringField())
    linkman = db.StringField()
    _tags = db.SetField(db_field='tags', item_type=db.StringField())
    grades = db.ListField(item_type=db.IntField())
    _location = db.TupleField(db.FloatField(), db.FloatField())
    status = db.EnumField(db.StringField(), 'block', 'show', 'wait',
            default='wait')
    updated = db.DateTimeField()
    created = db.DateTimeField()
    # counters
    c_click = db.SetField(item_type=db.StringField())
    c_sms = db.SetField(item_type=db.StringField())
    c_call = db.SetField(item_type=db.StringField())
    c_empty = db.SetField(item_type=db.StringField())
    c_good = db.SetField(item_type=db.StringField())
    c_bad = db.SetField(item_type=db.StringField())
    c_collection = db.SetField(item_type=db.StringField())


    def init_counters(self):
        self.c_click = set()
        self.c_sms = set()
        self.c_call = set()
        self.c_empty = set()
        self.c_good = set()
        self.c_bad = set()
        self.c_collection = set()
        self.grades = []

    @cached_property
    def pk(self):
        return str(self.mongo_id)

    def maybe_save(self, safe=None):
        try:
            self.save()
        except:
            abort(400)

    def _get_tags(self):
        return ' '.join(self._tags)

    def _set_tags(self, tags):
        if isinstance(tags, set):
            self._tags = tags
        elif isinstance(tags, basestring):
            self._tags = set(e.lower() for e in re.split('\s+', tags) if e)
        else:
            self._tags = set()

    tags = property(_get_tags, _set_tags)

    def _get_serviceitems(self):
        return ' '.join(self._serviceitems)

    def _set_serviceitems(self, tags):
        if isinstance(tags, set):
            self._serviceitems = tags
        elif isinstance(tags, basestring):
            self._serviceitems = set(e.lower() for e in re.split('\s+', tags) if e)
        else:
            self._serviceitems = set()

    serviceitems = property(_get_serviceitems, _set_serviceitems)

    def _get_serviceareas(self):
        return ' '.join(self._serviceareas)

    def _set_serviceareas(self, tags):
        if isinstance(tags, set):
            self._serviceareas = tags
        elif isinstance(tags, basestring):
            self._serviceareas = set(e.lower() for e in re.split('\s+', tags) if e)
        else:
            self._serviceareas = set()

    serviceareas = property(_get_serviceareas, _set_serviceareas)

    def _get_contracts(self):
        return ' '.join(self._contracts)

    def _set_contracts(self, tags):
        if isinstance(tags, list):
            self._contracts = tags
        elif isinstance(tags, basestring):
            self._contracts = [e.lower() for e in re.split('\s+', tags) if e]
        else:
            self._contracts = []

    contracts = property(_get_contracts, _set_contracts)

    def _get_location(self):
        a, b = self._location
        return "%f,%f" % (b,a)

    def _set_location(self, data):
        a, b = data.split(',')
        self._location = (float(b), float(a))

    location = property(_get_location, _set_location)

    class Permissions(object):
        def __init__(self, obj):
            self.obj = obj

        @cached_property
        def edit(self):
            return normal & sa

        @cached_property
        def delete(self):
            return sa

    @cached_property
    def permissions(self):
        return self.Permissions(self)

    @property
    def created_time(self):
        if self.has_id():
            return self.mongo_id.generation_time


class City(db.Document):

    PERN = 20

    name = db.StringField()
    _no = db.IntField(db_field='no')
    block = db.BoolField(default=True)
    label = db.StringField()

    def maybe_save(self, safe=None):
        try:
            self.save()
        except:
            abort(400)

    @cached_property
    def pk(self):
        return str(self.mongo_id)

    class Permissions(object):
        def __init__(self, obj):
            self.obj = obj

        @cached_property
        def edit(self):
            return normal & sa

        @cached_property
        def delete(self):
            return sa

    def get_no(self):
        return self._no

    def set_no(self, data):
        self._no = int(data)

    no = property(get_no, set_no)

    @cached_property
    def permissions(self):
        return self.Permissions(self)

    @property
    def created_time(self):
        if self.has_id():
            return self.mongo_id.generation_time


class Cate(db.Document):

    PERN = 20
    
    name = db.StringField()
    _no = db.IntField(db_field='no')
    logo = db.StringField()
    label = db.StringField()

    def maybe_save(self, safe=None):
        try:
            self.save()
        except:
            abort(400)

    @cached_property
    def pk(self):
        return str(self.mongo_id)

    class Permissions(object):
        def __init__(self, obj):
            self.obj = obj

        @cached_property
        def edit(self):
            return normal & sa

        @cached_property
        def delete(self):
            return sa

    @cached_property
    def permissions(self):
        return self.Permissions(self)

    def get_no(self):
        return self._no

    def set_no(self, data):
        self._no = int(data)

    no = property(get_no, set_no)

    @property
    def created_time(self):
        if self.has_id():
            return self.mongo_id.generation_time
