# coding: utf-8

from flask import Flask, g, session, request, redirect, url_for, jsonify, render_template, flash
from flaskext.principal import Principal, identity_loaded

from jzsadmin import views
from jzsadmin.models import User
from jzsadmin.ext import db
from jzsadmin.utils.escape import json_encode, json_decode

# configure
DEFAULT_APP_NAME = 'jzsadmin'

DEFAULT_MODULES = (
    ("/", views.home),
    ("/admin", views.admin),
)

# actions
def create_app(config=None, app_name=None, modules=None):

    if app_name is None:
        app_name = DEFAULT_APP_NAME

    if modules is None:
        modules = DEFAULT_MODULES   
    
    app = Flask(app_name)

    app.config.from_pyfile(config)

    # register module
    configure_modules(app, modules) 
    configure_extensions(app)
    configure_identity(app)
    configure_ba_handlers(app)
    configure_errorhandlers(app)
    configure_template_filters(app)

    return app


def configure_extensions(app):
    # configure extensions          
    db.init_app(app)


def configure_modules(app, modules):
    
    for url_prefix, module in modules:
        app.register_module(module, url_prefix=url_prefix)


def configure_identity(app):

    principal = Principal(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        g.user = User.query.from_identity(identity)


def configure_ba_handlers(app):
    pass


def configure_errorhandlers(app):
    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_xhr:
            return jsonify(code=401, error="Login required")
        flash("Please login to see this page", "error")
        return redirect(url_for("login", next=request.path))
  
    @app.errorhandler(403)
    def forbidden(error):
        if request.is_xhr:
            return jsonify(error='Sorry, page not allowed')
        return render_template("errors/403.html", error=error)

    @app.errorhandler(404)
    def page_not_found(error):
        if request.is_xhr:
            return jsonify(error='Sorry, page not found')
        return render_template("errors/404.html", error=error)

    @app.errorhandler(500)
    def server_error(error):
        if request.is_xhr:
            return jsonify(error='Sorry, an error has occurred')
        return render_template("errors/500.html", error=error)

def configure_template_filters(app):

    @app.template_filter()
    def intrange(value, page):
        if page > 6 and value > 10:
            res = range(page-5, page+5 if page+5 <= value else value+1)
        else:
            max_v = 10 if value >= 10 else value
            res = range(1, 1+max_v)
        return res
