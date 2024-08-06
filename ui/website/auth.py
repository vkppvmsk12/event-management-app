from flask import Blueprint, render_template, request, flash, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint("auth", __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["event-management-app"]
users = db["users"]

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users.find_one({"username":username})
        if user:
            if check_password_hash(user.get("password"), password):
                flash("Logged in succesfully!", category="success")
                #login_user(user, remember=True)
            else:
                flash("Incorrect password. Try again.", category="error")
        else:
            flash("Username doesn't exist.", category="error")

    return render_template("login.html")

@auth.route("/logout")
#@login_required
def logout():
    #logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        username = request.form.get("username").strip()

        user = users.find_one({"username":username})
        if user:
            flash("This username already exists. Please enter a different username.", category="error")
        elif not firstName:
            flash("Please provide a first name.", category="error")
        elif not lastName:
           flash("Please provide a last name.", category="error") 
        elif not email:
            flash("Please provide an email.", category="error")
        elif len(username) < 3:
            flash("Username too short. Must be at least 3 characters.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 8:
            flash("Password too short. Must be at least 8 characters", category="error")
        else:
            user_info = {
                "firstName" : firstName, 
                "lastName" : lastName,
                "email" : email,
                "username" : username,
                "password" : generate_password_hash(password1, method="scrypt")
            }
            users.insert_one(user_info)
            #login_user(user, remember=True)
            flash("Account created", category="success")
            return redirect(url_for("views.home"))

    return render_template("sign-up.html")