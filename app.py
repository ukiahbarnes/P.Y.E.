from flask import Flask, render_template, redirect, url_for, request, session,flash
import os 
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from tabledef import *


app = Flask(__name__)
engine = create_engine('sqlite:///pye.db',echo=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

Session = sessionmaker(bind=engine)
db = Session()

#testing
ukiah = User("ukiah","yousaf")
db.add(ukiah)
db.commit()
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"

@app.route('/login', methods=['POST'])
def do_admin_login():
    username = request.form['username']
    found_user = users.query.filter_by(username=username).first()
    if found_user:
        if request.form['password'] == found_user.password:
            session['logged_in'] = True
            session['user'] = username
        else:
            flash('wrong password!')
            return home()



if __name__ == "__main__":
    db.create_all()
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)
