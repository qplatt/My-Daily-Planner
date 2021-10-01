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
app.secret_key = os.environ.get("SECERT_KEY")

mongo = PyMongo(app)


@app.route("/")


@app.route("/get_plans")
def get_plans():
    plans = mongo.db.plans.find()
    return render_template("plans.html", plans=plans)


@app.route("/signup", methods=["GET", "POST"])
def signup(): 
    return render_template("signup.html")


if __name__ == "__main__": 
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
