from flask import render_template, request, redirect, Blueprint, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_bcrypt import Bcrypt

from models import *

auth_bp = Blueprint("auth", __name__)

bcrypt = Bcrypt()

# login_manager = LoginManager(auth_bp)
# login_manager.login_view = 'auth.login'

# @login_manager.user_loader
# def load_user(user_id):
#     # return User.query.get(int(user_id))
#     return db.session.get(User, int(user_id))

@auth_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect("/week_program")
    
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def process_login():
    if current_user.is_authenticated:
        return {
           "Already logged in." 
        }, 400
    
    usernumber = request.form['usernumber']
    password = request.form['password']

    user = User.query.filter_by(number=usernumber).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        
        # role = Role.query.filter_by(id=user.role_id).first().name

        # if role == "Student":
        if user.role_id == 3:
            return redirect("/week_program?students_number=" + user.number)
        else:
            return redirect("/week_program")

    # message = "Invalid username or password"
    flash('Invalid username or password!', 'error')

    return redirect("/login")

@auth_bp.route("/logout")
@login_required
def process_logout():
    logout_user()
    return redirect('/login')
