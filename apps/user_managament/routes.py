#import io
#import json
#import locale

#locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

import io
import pandas as pd
from flask import jsonify, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user

from apps.user_managament import blueprint
from apps import db
from apps.authentication.models import Users, ClientLogo, ClientData, ClientImgData


ROWS_PER_PAGE = 9
# create admin user


#ROWS_PER_PAGE = 9
@blueprint.route('/somethjinkg')
def route_default():
    admin = Users(username="admin",email= "admin@something.com", password="password", is_admin=True)
    db.session.add_all([admin])
    db.session.commit()
    return "somethjinkg"

#@blueprint.route("/manage_users", methods=["GET", "POST"])
#def login():
#    if current_user.is_authenticated and current_user.is_admin:
#        return redirect(url_for("
# user_managament_blueprint.manage_users"))


@blueprint.route("/manage", methods=["GET", "POST"])
def manage_users():
    # If the user is not an admin - inform the user of limited access
    if not current_user.is_admin:
        return redirect (url_for('home_blueprint.validation', user = current_user.username))

    page = request.args.get("page", 1, type=int)
    users = Users.query.paginate(page=page, per_page=ROWS_PER_PAGE)
    has_users = [user for user in users.items if not user.is_admin]

    return render_template("accounts/manage_users.html", users=users, has_users=has_users,username=current_user.username)


@blueprint.route("/profile", methods=["GET", "POST"])
def profile():
    # If the user is not an admin - inform the user of limited access
    if not current_user.is_admin:
        return "no permission"

    username = request.values["user"]
    user = Users.query.filter_by(username=username).first()

    return render_template("home/profile.html", user=user)

@blueprint.route("/client-logo/<user_id>")
def serve_client_logo(user_id):
    # access the user logo
    client_logo = ClientLogo.query.filter_by(user_id=user_id).first()
    file_ext = client_logo.filename.split(".")[1]
    return send_file(io.BytesIO(client_logo.data), mimetype=f"image/{file_ext}")

@blueprint.route("/client-img-data/<id>")
def serve_client_img_data(id):
    # access the user img data
    client_logo = ClientImgData.query.filter_by(id=id).first()
    file_ext = client_logo.filename.split(".")[1]
    return send_file(io.BytesIO(client_logo.data), mimetype=f"image/{file_ext}")


@blueprint.route("/client-data/<user_id>")
def serve_client_data(user_id):
    # access the dashboard excel file
    client_data = ClientData.query.filter_by(user_id=user_id).first()
    file_ext = client_data.filename.split(".")[1]
    if file_ext == "xlsx":
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_ext == "xls":
        mimetype = "application/vnd.ms-excel"
    elif file_ext == "csv":
        mimetype = "text/csv"
    else:
        mimetype = "application/vnd.ms-excel"
    
    data = pd.read_excel(
        io.BytesIO(client_data.data)
    )
    print(data)
    return send_file(io.BytesIO(client_data.data),attachment_filename=client_data.filename ,as_attachment = True)


# update data
@blueprint.route("/update-username", methods=["POST"])
def update_username():
    username = request.values["user"]
    user = Users.query.filter_by(username=username).first()

    new_username = request.form.get("username")
    is_username_existing = User.query.filter_by(username=new_username).first()

    if is_username_existing and (new_username != user.username):
        message = "Oops!!! username is already taken"
        return render_template(
            "manage_profile.html",
            user=user,
            message=message,
        )
    else:
        if new_username != user.username:
            user.username = new_username
            db.session.commit()

            message = "Username successfully updated!"

            return render_template(
                "manage_profile.html",
                user=user,
                message=message,
            )

    return render_template(
        "manage_profile.html",
        user=user,
    )


@blueprint.route("/update-admin-username", methods=["POST"])
def update_admin_username():
    # If the user is not an admin - inform the user of limited access
    if not current_user.is_admin:
        return redirect(url_for("unauthorized_access"))

    new_username = request.form.get("username")
    if new_username != current_user.username:
        current_user.username = new_username
        db.session.commit()

        message = "Username successfully updated!"

        return render_template(
            "manage_profile.html",
            user=current_user,
            message=message,
        )

    return render_template("manage_admin_profile.html", user=current_user)


@blueprint.route("/delete-account", methods=["POST"])
def delete_account():
    username = request.values["user"]
    user = Users.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()

    if current_user.is_admin:
        return redirect(url_for("manage_users"))
    else:
        return redirect(url_for("login"))


@blueprint.route("/update-files", methods=["POST"])
def update_files():
    username = request.values["user"]
    user = Users.query.filter_by(username=username).first()

    client_logo = ClientLogo.query.filter_by(user_id=user.id).first()
    client_data = ClientData.query.filter_by(user_id=user.id).first()


    # grab the uploaded files from the user
    new_logo = request.files.get("client-logo")
    new_data = request.files.get("data")
    files = request.files.getlist('imgdata[]')
    if len(files) > 1 :
        ClientImgData.query.filter_by(user_id=user.id).delete()
        for file in files:
            client_img_data = ClientImgData(
                filename=file.filename,
                data=file.read(),
                user_id=user.id,
            )
            db.session.add(client_img_data)
            db.session.commit()

    if new_logo and client_logo != None :
        client_logo.filename = new_logo.filename
        client_logo.data = new_logo.read()
        db.session.commit()
    else:
        client_logo = ClientLogo(
        filename=new_logo.filename,
        data=new_logo.read(),
        user_id=user.id)
        db.session.add(client_logo)
        db.session.commit()

    if new_data and client_data != None:
        client_data.filename = new_data.filename
        client_data.data = new_data.read()
        db.session.commit()
    else:
        client_data = ClientData(
        filename=new_data.filename,
        data=new_data.read(),
        user_id=user.id)
        db.session.add(client_data)
        db.session.commit()
    
    return render_template(
        "home/profile.html",
        user=user,
        upload_message="Files updated successfully",
    )


@blueprint.route("/update-password", methods=["POST"])
def update_user_password():
    username = request.values["user"]
    user = Users.query.filter_by(username=username).first()

    # if the user passed an invalid password
    passed_current_password = request.form.get("old-password")
    if not user.check_password(passed_current_password):
        return render_template(
            "manage_profile.html",
            user=user,
            pass_message="Incorrect password!",
        )

    # if the new password and confirmation password do not match
    new_password = request.form.get("new-password")
    confirm_new_password = request.form.get("confirm-new-password")
    print("new_password: ", new_password)
    print("confirm_new_password: ", confirm_new_password)
    if new_password != confirm_new_password:
        return render_template(
            "manage_profile.html",
            user=user,
            pass_message="Both passwords must match! Ensure the new password matches the confirmation password",
        )

    # if everything is done right
    if (user.check_password(passed_current_password)) and (
        new_password == confirm_new_password
    ):
        user.password = user.set_password(new_password)
        db.session.commit()
        password_message = "Password successfully updated!"
        return render_template(
            "manage_profile.html",
            user=user,
            pass_message=password_message,
        )

    # if we are unable to detect whats wrong
    return render_template(
        "manage_profile.html",
        user=user,
        pass_message="Something went wrong! ",
    )


@blueprint.route("/update-admin-password", methods=["POST"])
def update_admin_password():
    # If the user is not an admin - inform the user of limited access
    if not current_user.is_admin:
        return redirect(url_for("unauthorized_access"))

    # if the user passed an invalid password
    passed_current_password = request.form.get("old-password")
    if not current_user.check_password(passed_current_password):
        return render_template(
            "manage_admin_profile.html",
            user=current_user,
            pass_message="Incorrect password!",
        )

    # if the new password and confirmation password do not match
    new_password = request.form.get("new-password")
    confirm_new_password = request.form.get("confirm-new-password")
    print("new_password: ", new_password)
    print("confirm_new_password: ", confirm_new_password)
    if new_password != confirm_new_password:
        return render_template(
            "manage_admin_profile.html",
            user=current_user,
            pass_message="Both passwords must match! Ensure the new password matches the confirmation password",
        )

    # if everything is done right
    if (current_user.check_password(passed_current_password)) and (
        new_password == confirm_new_password
    ):
        current_user.password = current_user.set_password(new_password)
        db.session.commit()
        password_message = "Password successfully updated!"
        return render_template(
            "manage_admin_profile.html",
            user=current_user,
            pass_message=password_message,
        )

    # if we are unable to detect whats wrong
    return render_template(
        "manage_admin_profile.html",
        user=current_user,
        pass_message="Something went wrong! ",
    )

