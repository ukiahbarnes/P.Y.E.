from flask import Flask, render_template, redirect, url_for, request, session,flash
import os
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pye.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class.id"))
    date = db.Column(db.String(8), unique=False, nullable=True)



# db.create_all()

def getItemsByClass(course):
    format_str = "%Y-%m-%d"  # The format
    items = []
    dates = []
    classitems = db.session.query(Item).filter_by(class_id=course.id).all()
    for classitem in classitems:
        date = datetime.datetime.strptime(classitem.date, format_str)
        dates.append(date)
    dates.sort()
    for date in dates:
        item = (
            db.session.query(Item).filter_by(class_id=course.id).filter_by(date=date.strftime(format_str)).first()
        )
        items.append(item)
    return items




def getClasses():
    user_id = db.session.query(User).filter_by(username=session["username"]).first().id
    classes = db.session.query(Class).filter(Class.user_id == user_id).all()
    return classes

def getItemsClassDict():
    classes = getClasses()
    dictionary = {}
    for course in classes:
        items = getItemsByClass(course)
        dictionary.update({course: items})
    return dictionary

def getItems():
    classes = getClasses()
    items = []
    for eachclass in classes:
        classitems = db.session.query(Item).filter_by(class_id=eachclass.class_id).all()
        for classitem in classitems:
            items.append(classitem)
    return items

@app.route("/")
def home():
    if "logged_in" not in session or session["logged_in"] == False:
        session["username"] = None
        return render_template("login.html")
    else:
        return render_template("home.html",username=session["username"],dict=getItemsClassDict())

@app.route("/home")
def homeroute():
    return home()

@app.route("/login", methods=["POST","GET"])
def do_admin_login():
    if request.method == "GET":
        return home()
    username = request.form["username"]
    found_user = db.session.query(User).filter_by(username=username).first()
    if found_user:
        if request.form["password"] == found_user.password:
            session["logged_in"] = True
            session["username"] = username
            return home()
        else:
            flash("wrong password!")
            return home()
    else:
        return render_template("login.html")


@app.route("/create_account", methods=["POST"])
def create_account():
    username = request.form["username"]
    found_user = db.session.query(User).filter_by(username=username).first()
    if found_user:
        return render_template("error404.html")
    password = request.form["password"]
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    session["logged_in"] = True
    session["username"] = username
    return home()

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/addClass")
def addClass():
    if "logged_in" not in session or session["logged_in"] == False:
        session["username"] = None
        return render_template("login.html")
    else:
        return render_template("addClass.html")

@app.route("/addAssignment")
def addAssignment():
    if "logged_in" not in session or session["logged_in"] == False:
        session["username"] = None
        return render_template("login.html")
    else:
        return render_template("addAssignment.html",dict=getItemsClassDict())


def logout():
    session["logged_in"] = False
    session["username"] = None
    return home()

@app.route("/logout")
def log_out():
    session["logged_in"] = False
    session["username"] = None
    return home()

@app.route("/create_item", methods=["POST","GET"])
def create_item():
    if request.method == "GET":
        return home()
    item_name = request.form["name"]
    classname = request.form["classname"]
    date = request.form["date"]
    db.session.add(Item(name=item_name,date=date,class_id=db.session.query(Class).filter_by(name=classname).first().id))
    db.session.commit()
    return redirect("/home")


    
@app.route("/create_class", methods=["POST","GET"])
def create_class():
    if request.method == "GET":
        return home()
    classname = request.form["classname"]
    user_id = db.session.query(User).filter_by(username=session["username"]).first().id
    db.session.add(Class(name=classname, user_id=user_id))
    db.session.commit()
    return redirect("/home")



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host="0.0.0.0", port=8000)
    db.create_all()

