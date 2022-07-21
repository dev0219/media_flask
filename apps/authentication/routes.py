# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from cmath import log
from flask import render_template, redirect, request, url_for
from flask_login import (
    login_required,
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users, ClientData, ClientLogo, ClientImgData

from apps.authentication.util import verify_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('user_managament_blueprint.manage_users'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():

    if not current_user.is_admin:
        return redirect(url_for("authentication_blueprint.unauthorized_handler"))
    
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)

@blueprint.route("/admin/register", methods=["POST"])

@login_required
def register_new_user():
    # If the user is not an admin - inform the user of limited access
    if not current_user.is_admin:
        return redirect(url_for("authentication_blueprint.unauthorized_handler"))

    # get the inputs from the user
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    logofile = request.files["client-logo"]
    datafile = request.files["data"]
    files = request.files.getlist('imgdata[]')
    
    # populate the data to the database
    new_user = Users(username=username, email=email, password=password)

    client_data = ClientData(
        filename=datafile.filename,
        data=datafile.read(),
        user_id=new_user.id,
    )
    client_logo = ClientLogo(
        filename=logofile.filename,
        data=logofile.read(),
        user_id=new_user.id,
    )

    # create the relationships
    client_data.users = new_user
    client_logo.users = new_user

    # commit the data
    db.session.add(new_user)
    db.session.add(client_data)
    db.session.add(client_logo)
    for file in files:
        client_img_data = ClientImgData(
            filename=file.filename,
            data=file.read(),
            user_id=new_user.id,
        )
        client_img_data.users = new_user
        db.session.add(client_img_data)
        db.session.commit()
    db.session.commit()

    return redirect(url_for("user_managament_blueprint.manage_users"))


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
