from flask import Flask, render_template, redirect, url_for, request, session, flash
import os
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker


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


# db.create_all()

# testing
# ukiah = User(username="ukiah", password="yousaf")
# db.session.add(ukiah)
# db.session.commit()


@app.route("/")
def home():
    if not session.get("logged_in"):
        return db.session.query(User).first().username
    else:
        return "Hello Boss!"


@app.route("/login", methods=["POST"])
def do_admin_login():
    username = request.form["username"]
    found_user = user.query.filter_by(username=username).first()
    if found_user:
        if request.form["password"] == found_user.password:
            session["logged_in"] = True
            session["user"] = username
        else:
            flash("wrong password!")
            return home()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host="0.0.0.0", port=8000)
