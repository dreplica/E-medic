import os
import csv
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

def apology(issue,code):
   return (str(issue)+"is to this code"+str(code))
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///emedic.db")

@app.route('/')
def index():
   if session['user_id']:
      treat = db.execute("SELECT * from consultation where user_id =: user",user = session['user_id'])
      if len(treat) != 0:
         doc = db.execute("SELECT doc,issue,photo,specialty, from consultation where user_id =: user",user = treat[0]['doc'])
   return render_template("index.html",treat = treat[0],doc =doc)

@app.route('/login',methods=['GET','POST'])
def login():
   if request.method == 'POST':
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
   return render_template("login.html")

@app.route('/logout',methods=['GET','POST'])
def logout():
   if session["user_id"]:
      session.clear()
      return redirect('index.html')
   return apology('sorry you"re not on this service',400)

@app.route('/p_register',methods=['GET',"POST"])
def p_register():
    file = open('states.csv','r')
    reader = csv.reader(file)
    states = list(reader)
    if request.method == 'POST':
       userid = request.form.get('username')
       email = request.form.get('email')
       passw = request.form.get('password')
       typ = request.form.get('type')
       date = request.form.get('date')
       blood = request.form.get('blood')
       geno = request.form.get('gene')
       med = request.form.get('issues')
       k_fn = request.form.get('firstname')
       k_ln = request.form.get('lastname')
       kp = request.form.get('number')
       ke = request.form.get('kemail')
       k_loc = request.form.get('kadd')
       fname = request.form.get('fname')
       lname = request.form.get('lname')
       dob = request.form.get('dob')
       sex = request.form.get('sex')
       state = request.form.get('states')
       addr = request.form.get('address')
       pnum = request.form.get('pnum')
       status = request.form.get('mstat')
       idn = request.form.get('idname')
       nid = request.form.get('idnum')
       pic = request.form.get('photo')
       session['user_id'] = request.form.get('username')
      #  user = users(userid)
       db.execute("INSERT INTO users (user_id,password,email,type,date) values(:us,:em,:pa,:ty,:da)",da = date,us = userid,em =email,pa=passw,ty=typ)
       db.execute("INSERT INTO pat_info (b_gr,g_gr,med_iss,kin_fn,kin_ln,kin_ph,kin_email,kin_loc) values(:b,:g,:md,:kfn,:kln,:kp,:ke,:kl,:us)",
                   b=blood,g=geno,md=med,kfn=k_fn,kln = k_ln,kp = kphone,ke = kem,kl=k_loc,us = userid)
       db.execute("INSERT INTO info (:u,:f,:l,:m,:p,:l,:s,:sx,:dob,:id,idn,pic)",
                   u=userid,f=fname,l=lname,m=med,p=pnum,s =status, sx=sex,dob=dob,id=idn,idn=nid,pic=pic)
       return render_template('index.html')
    return render_template('p_register.html',states=states) 

# out of the context
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


