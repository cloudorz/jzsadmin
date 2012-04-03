# coding: utf-8

import re, datetime

from flask import g, Module, request, flash, abort, redirect, url_for, session, render_template, \
                    jsonify, current_app
from flaskext.principal import identity_changed, Identity, AnonymousIdentity

from jzsadmin.models import Entry, User, Cate, City
from jzsadmin.forms import LoginForm, EntryForm, CateForm, CityForm
from jzsadmin.permissions import sa, normal

admin = Module(__name__)

now = datetime.datetime.utcnow

# home 
@admin.route("/")
@normal.require(401)
def index():
    return render_template("admin/home.html")

@admin.route('/menu/', methods=('GET', ))
@normal.require(401)
def menu():
    return render_template('admin/menulist.html')

@admin.route("/welcome/")
@normal.require(401)
def welcome():
    return render_template("admin/welcome.html")

# accounts
@admin.route('/login/', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form, next=request.args.get('next',''))

    if form.validate_on_submit():
        user = User.query.filter(User.name==form.name.data).first()
        if user and user.check_password(form.password.data):
            identity_changed.send(current_app._get_current_object(),
                    identity=Identity(user.pk))
            flash(u"登录成功")
            return redirect(request.args.get("next") or url_for("index"))

        flash(u"登录失败, 请重新登录")
    return render_template("admin/login.html", form=form)

@admin.route('/logout/')
def logout():
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    flash(u'已登出', 'success')
    return redirect(url_for('index'))


# entries 
@admin.route('/entry/')
@admin.route('/entry/<int:page>/')
@normal.require(401)
def list_entry(page=1):

    if page<1:page=1

    q = request.args.get('q','')
    if q:
        regex = re.compile(r'^.*?%s.*?$' % q)
        query = Entry.query.filter({'$or': [
            {'title': regex},
            {'brief': regex},
            {'desc': regex},
            {'tags': q}]})
    else:
        query = Entry.query

    p = query.descending(Entry.created).paginate(page, per_page=Entry.PERN)

    return render_template("admin/entry_list.html", p=p)

@admin.route('/entry/add/', methods=('GET', 'POST'))
@normal.require(401)
def add_entry():
    form = EntryForm(request.form, next=request.args.get('next',''))
    cities = City.query.ascending(City.no)
    cates = Cate.query.ascending(City.no)

    if form.validate_on_submit():

        entry = Entry()
        entry.updated = now()
        entry.created = now()
        entry.grades = []
        entry.city_label = request.form.get('city_label')
        form.populate_obj(entry)

        entry.save()
        flash(u"保存成功")

        next_url = form.next.data
        if not next_url:
            next_url = url_for('list_entry')

        return redirect(next_url)

    return render_template("admin/entry_add.html",form=form, cities=cities,
            cates=cates)

@admin.route('/entry/<eid>/edit/', methods=('GET', 'POST'))
@normal.require(401)
def edit_entry(eid):
    entry = Entry.query.get_or_404(eid)
    cities = City.query.ascending(City.no)
    cates = Cate.query.ascending(City.no)

    form = EntryForm(request.form, entry, next=request.args.get('next',''))

    if form.validate_on_submit():

        form.populate_obj(entry)

        entry.city_label = request.form.get('city_label', 'hangzhou')
        entry.status = 'wait' # wait for check again
        entry.save()
        flash(u"更新成功")

        next_url = form.next.data
        if not next_url:
            next_url = url_for('list_entry')

        return redirect(next_url)

    return render_template("admin/entry_add.html", form=form, cities=cities,
            city_label=entry.city_label,
            cates=cates)

@admin.route('/entry/<eid>/del')
@normal.require(401)
def del_entry(eid):
    
    entry = Entry.query.get_or_404(eid)
    entry.permissions.delete.test(403)
    entry.remove()

    return redirect(url_for('list_entry'))


# cates 
@admin.route('/cate/')
@admin.route('/cate/<int:page>/')
@normal.require(401)
def list_cate(page=1):

    if page<1:page=1

    q = request.args.get('q','')
    if q:
        regex = re.compile(r'^.*?%s.*?$' % q)
        query = Cate.query.filter({'name': regex})
    else:
        query = Cate.query

    p = query.descending(Cate.no).paginate(page, per_page=Cate.PERN)

    return render_template("admin/category_list.html", p=p)


@admin.route('/cate/add', methods=('GET', 'POST'))
@normal.require(401)
def add_cate():
    form = CateForm(request.form, next=request.args.get('next',''))

    if form.validate_on_submit():

        cate = Cate()
        form.populate_obj(cate)

        cate.save()
        flash(u"保存成功")

        next_url = form.next.data
        if not next_url:
            next_url = url_for('list_cate')

        return redirect(next_url)

    return render_template("admin/category_add.html",form=form)


@admin.route('/cate/<cid>/edit', methods=('GET', 'POST'))
@normal.require(401)
def edit_cate(cid):
    cate = Cate.query.get_or_404(cid)

    form = CateForm(request.form, cate, next=request.args.get('next',''))

    if form.validate_on_submit():

        form.populate_obj(cate)

        cate.save()
        flash(u"更新成功")

        next_url = form.next.data
        if not next_url:
            next_url = url_for('list_cate')

        return redirect(next_url)

    return render_template("admin/cate_add.html", form=form)


@admin.route('/cate/<cid>/del', methods=('GET',))
@normal.require(401)
def del_cate(cid):
    
    cate = Cate.query.get_or_404(cid)
    cate.permissions.delete.test(403)
    cate.remove()

    return redirect(url_for('list_cate'))


# cities 
@admin.route('/city/')
@admin.route('/city/<int:page>/')
@normal.require(401)
def list_city(page=1):

    if page<1:page=1

    q = request.args.get('q','')
    if q:
        regex = re.compile(r'^.*?%s.*?$' % q)
        query = City.query.filter({'name': regex})
    else:
        query = City.query

    p = query.descending(City.no).paginate(page, per_page=City.PERN)

    return render_template("admin/city_list.html", p=p)


@admin.route('/city/add', methods=('GET', 'POST'))
@normal.require(401)
def add_city():
    form = CityForm(request.form, next=request.args.get('next',''))

    if form.validate_on_submit():

        city = City()
        form.populate_obj(city)

        city.save()
        flash(u"保存成功")

        next_url = form.next.data
        if not next_url:
            next_url = url_for('list_city')

        return redirect(next_url)

    return render_template("admin/city_add.html",form=form)

@admin.route('/city/<cid>/edit', methods=('GET', 'POST'))
@normal.require(401)
def edit_city(cid):
    city = City.query.get_or_404(cid)

    form = CityForm(request.form, city, next=request.args.get('next',''))

    if form.validate_on_submit():

        form.populate_obj(city)

        city.save()
        flash(u"更新成功")

        next_url = form.next.data
        if not next_url:
            next_url = url_for('list_city')

        return redirect(next_url)

    return render_template("admin/city_add.html", form=form)

@admin.route('/city/<cid>/del')
@normal.require(401)
def del_city(cid):
    
    city = City.query.get_or_404(cid)
    city.permissions.delete.test(403)
    city.remove()

    return redirect(url_for('list_city'))

# others operation
@admin.route('/entry/status/')
@admin.route('/entry/status/<int:page>/')
@sa.require(403)
def wait_entry_list(page=1):

    if page<1:page=1

    q = request.args.get('q', '')
    city = request.args.get('c', '')
    tag = request.args.get('t', '')
    status = request.args.get('s', '')

    if q:
        regex = re.compile(r'^.*?%s.*?$' % q)
        condtions.append({'$or': [{'title': regex},
            {'brief': regex},
            {'desc': regex},
            {'tags': q}]})

    if city and city != 'all':
        condtions.append({'city_label': city})

    if tag and tag != 'all':
        condtions.append({'tags': tag})

    if status and status != 'all':
        condtions.append({'status': status})

    query = Entry.query.filter(*tuple(condtions))

    p = query.descending(Entry.created).paginate(page, per_page=Entry.PERN)
    cities = City.query.ascending(City.no)
    cates = Cate.query.ascending(City.no)
    statuses = [
            {'label': 'show', 'name': '显示'},
            {'label': 'wait', 'name': '等待'}, 
            {'label': 'block', 'name': '禁用'}]

    return render_template("admin/wait_entry_list.html",
            cities=cities,
            cates=cates,
            statuses=statuses,
            p=p,
            status=status)

@admin.route('/entry/<eid>/<tostatus>')
@sa.require(403)
def change_status(eid, tostatus):
    next = request.args.get('next', '')
    entry = Entry.query.get_or_404(eid)
    entry.status = tostatus
    entry.save()

    return redirect(next or url_for('wait_entry_list', status='wait'))
