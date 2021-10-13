import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/dashboard")
def dashboard():
    dashboard = list(mongo.db.plans.find())
    return render_template("dashboard.html", dashboard=dashboard)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))

        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(signup)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Sign Up Complete!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_plan", methods=["GET", "POST"])
def add_plan():
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        plan = {
            "section_name": request.form.get("section_name"),
            "plan_name": request.form.get("plan_name"),
            "plan_description": request.form.get("plan_description"),
            "is_urgent": is_urgent,
            "end_date": request.form.get("end_date"),
            "created_by": session["user"]
            }

        mongo.db.plans.insert_one(plan)
        flash("Plan Successfuly Added!")
        return redirect(url_for("dashboard"))

    sections = mongo.db.sections.find().sort("section_name", 1)
    return render_template("add_plan.html", sections=sections)


@app.route("/edit_plan/<dash_id>", methods=["GET", "POST"])
def edit_plan(dash_id):

    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        submit = {
            "section_name": request.form.get("section_name"),
            "plan_name": request.form.get("plan_name"),
            "plan_description": request.form.get("plan_description"),
            "is_urgent": is_urgent,
            "end_date": request.form.get("end_date"),
            "created_by": session["user"]
            }
            
        mongo.db.plans.update({"_id": ObjectId(dash_id)}, submit)
        flash("Plan Successfuly Updated!")

    dash = mongo.db.plans.find_one({"_id": ObjectId(dash_id)})
    sections = mongo.db.sections.find().sort("section_name", 1)
    return render_template("edit_plan.html", dash=dash, sections=sections)


@app.route("/delete_plan/<dash_id>")
def delete_plan(dash_id):
    mongo.db.plans.remove({"_id": ObjectId(dash_id)})
    flash("Succesfully Finished Plan")
    return redirect(url_for("dashboard"))


@app.route("/get_sections")
def get_sections(): 
    sections = list(mongo.db.sections.find().sort("section_name", 1))
    return render_template("sections.html", sections=sections)


@app.route("/add_section", methods=["GET", "POST"])
def add_section():
    if request.method == "POST":
        section = {
            "section_name": request.form.get("section_name")
        }
        mongo.db.sections.insert_one(section)
        flash("New Section Added")
        return redirect(url_for("get_sections"))

    return render_template("add_section.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
