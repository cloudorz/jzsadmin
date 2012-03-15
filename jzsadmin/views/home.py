# coding: utf-8

from flask import g, Module, request, flash, abort, redirect, url_for, session, render_template, \
                    jsonify

from jzsadmin.models import Entry, User, Cate, City

home = Module(__name__)

@home.route("/")
def index():
    return render_template("index.html")
