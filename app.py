
import cs50
from flask import FLask, render_template,redirect,sessions
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
# alchemy is the connection we are to use btw sqlite and python 
from flask_sqlalchemy import SQLAlchemy
# from import the function to encrypt and decrypt password 
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# you need to import sql to give it to a database
app.config['SQLALCHEMY_DATABASE_URI'] = 'splite:////medic.db'
#commence app with database
db = SQLAlchemy(app)

def apology(issue,code):
    html = "<div><p>"+code+"</p>"+"<p>"+issue+"</p></div>"
    return render_template('apology.html',html)

class info(db.model):
    id = db.column()
    user_id = db.column()
    user_id = db.column()
    user_id = db.column()
    user_id = db.column()
    def __repr__(self):
        return '<users %r>' % info.user_id

class user(db.model):
    id = db.column()
    user_id = db.column()
    email = db.column()
    type = db.column()
    password = db.column()
    def __repr__(self):
        return '<user %r>' % self.user_id

class med_his(db.model):
    id = db.column()
    user_id = db.column()
    b_type = db.column()
    g_type = db.column()
    Med_cond = db.column()
    def __repr__(self):
        return '<med_his %r>' % self.b_type

