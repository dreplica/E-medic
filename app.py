
# import cs50
from flask import Flask, render_template,redirect,session,request
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

class users(db.model):
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

@app.route('/')
def index():
   return render_template("index.html",name="david")

@app.route('/login',methods=['GET','POST'])
def login():
   if request.methods == 'POST':
      name = request.form['username']
      password = request.form['password']
      if not name and not password:
         user = user.query.filter_by(user_id=name).first()
      if len(user) != 0:
         if check_password_hash(user[0][password],password):
            #to save user's session
            session['user_id'] = user[0]['user_id']
            # need the history session to query for current doc and current treatment
            history = history.query.filter_by(user_id=name).first()
            # to get current doc info
            doc = session.query(users,info) 
            return render_template('home.html',id=session['user_id'])
      return apology("username and password does not match",400)
   return render_template('login.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
   if session["user_id"]:
      session.clear()
      return redirect('index.html')
   return apology('sorry you"re not on this service',400)