from flask import Blueprint, render_template, request, flash
from pymongo import MongoClient

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@auth.route("/logout")
def logout():
    return "<p>Logout</p>"

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        username = request.form.get("username")

        if len(firstName) < 3:
            flash("First name too short. Must be at least 3 characters", category="error")
        elif len(lastName) < 3:
           flash("Last name too short. Must be at least 3 characters", category="error") 
        elif len(email) < 4:
            flash("Email too short. Must be at least 4 characters.", category="error")
        elif len(username) < 3:
            flash("Username too short. Must be at least 3 characters.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 7:
            flash("Password too short. Must be at least 7 characters", category="error")
        else:
            flash("Account created", category="success")

    return render_template("sign-up.html")