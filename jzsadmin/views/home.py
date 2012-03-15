# coding: utf-8

from flask import g, Module, request, flash, abort, redirect, url_for, session, render_template, \
                    jsonify
from flaskext.login import login_user, login_required, current_user, \
        logout_user

from jzsadmin.models import Entry, User, Cate, City
from jzsadmin.forms import LoginForm

home = Module(__name__)

@home.route("/")
def index():
    return render_template("index.html")
