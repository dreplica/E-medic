import os
import datetime
import csv
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,url_for
from flask_session import Session
import folium
from werkzeug.utils import secure_filename
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# Configure application
app = Flask(__name__)
map = folium.Map(location = [6.5244, 3.3792],zoom_start=12)
folium.Marker([6.4488294999999995,3.5306864],popup='<strong>Decagon</strong>',tooltip="Decagon").add_to(map)
folium.Marker([6.9999995,4.5306864],popup='<strong>Decagon</strong>',tooltip="dragon").add_to(map)
folium.Marker([6.995,2.06864],popup='<strong>Decagon</strong>',tooltip="dragon").add_to(map)

# Ensure templates are auto-reloaded and picture folder
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
db = SQL("sqlite:///medic.db")

@app.route('/')
def index():
   # if session['user_id']:
   #    treat = db.execute("SELECT * from consultation where user_id =: user",user = session['user_id'])
   #    if len(treat) != 0:
   #       doc = db.execute("SELECT doc,issue,photo,specialty, from consultation where user_id =: user",user = treat[0]['doc'])
   return render_template("index.html",person = ['type','name'])#,treat = treat[0],doc =doc)

@app.route('/login',methods=['GET','POST'])
def login():
   if request.method == 'POST':
      name = request.form.get('username')
      password = request.form.get('password')

      if not name and not password:
         return "please go back and enter appropriate details"

      user = db.execute("Select * from users")

      if len(user) != 0:
         if check_password_hash(user[0]['password'],password):
            session['user_id'] = user[0]['user_id']
            consult = db.execute('Select * from consultation')

            if len(consult) == 0:
               return session['user_id']
            return render_template('index.html',user = user,history = consult)
      return apology("username and password does not match",400)
   return render_template("login.html")

@app.route('/logout',methods=['GET','POST'])
def logout():
   if session["user_id"]:
      session.clear()
      return redirect('index.html')
   return apology('sorry you"re not on this service',400)

# registration for patients
@app.route('/p_register',methods=['GET',"POST"])
def p_register():
    file = open('states.csv','r')
    reader = csv.reader(file)
    states = list(reader)
    if request.method == 'POST':
       userid = request.form.get('username')
       email = request.form.get('email')
       passw = generate_password_hash(request.form.get('password'),'pbkdf2:sha256',8)
       typ = request.form.get('type')
       date = datetime.datetime.now()
       blood = request.form.get('blood')
       geno = request.form.get('gene')
       med = request.form.get('issues')
       k_fn = request.form.get('firstname')
       k_ln = request.form.get('lastname')
       kp = request.form.get('knumber')
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
       fille = request.files['photo']
       pic = request.form.get('photo')
       session['user_id'] = request.form.get('username')
      #  user = users(userid)
       if fille.filename == '':
          fille.filename = 'none'
       fille.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fille.filename)))
       db.execute("INSERT INTO users (user_id,email,password,type,date) VALUES(:us,:em,:pa,:ty,:da)",da = date,us = userid,em =email,pa=passw,ty=typ)
       db.execute("INSERT INTO pat_info (b_gr,g_gr,med_iss,kin_fn,kin_ln,kin_phone,kin_email,kin_loc,user_id) VALUES(:b,:g,:md,:kfn,:kln,:kp,:ke,:kl,:us)",
                   b=blood,g=geno,md=med,kfn=k_fn,kln = k_ln,kp=kp,ke = ke,kl=k_loc,us = userid)
       db.execute("INSERT INTO info (user_id,f_name,l_name,m_stat,phone,location,state,sex,dob,id_name,id_no,photo) Values (:u,:f,:l,:m,:p,:l,:s,:sx,:dob,:id,:idn,:pic)",
                   u=userid,f=fname,l=lname,m=status,p=pnum,s =state, sx=sex,dob=dob,id=idn,idn=nid,pic=fille.filename)
       return render_template('index.html')
    return render_template('p_register.html',states=states) 

#registration for doctors
@app.route('/d_register',methods=['GET',"POST"])
def d_register():
    file = open('states.csv','r')
    reader = csv.reader(file)
    states = list(reader)
    if request.method == 'POST':
       userid = request.form.get('username')
       email = request.form.get('email')
       passw = generate_password_hash(request.form.get('password'),'pbkdf2:sha256',8)
       typ = request.form.get('type')
       date = datetime.datetime.now()
       fname = request.form.get('fname')
       lname = request.form.get('lname')
       dob = request.form.get('dob')
       sex = request.form.get('sex')
       state = request.form.get('states')
       addr = request.form.get('address')
       pnum = request.form.get('pnum')
       status = request.form.get('mstat')
       l = request.form.get('year1')
       e = request.form.get('year2')
       idn = request.form.get('idname')
       nid = request.form.get('idnum')
       sp = request.form.get('speciality')
       hf = request.form.get('hospital')
       cert = request.form.get('certificate')
       lp = request.form.get('link')
       cp = request.form.get('country')
       ms = request.form.get('school')
       bc = request.form.get('board')
       us = request.form.get('idnum')
       fille = request.files['photo']
       session['user_id'] = request.form.get('username')
      #  user = users(userid)
       if fille.filename == '':
          fille.filename = 'none'
       fille.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fille.filename)))
       db.execute("INSERT INTO users (user_id,email,password,type,date) VALUES(:us,:em,:pa,:ty,:da)",da = date,us = userid,em =email,pa=passw,ty=typ)
       db.execute("INSERT INTO doc_info (lic_yr,exp_yr,specialty,hos_aff,cert,link_pub,con_prac,med_sch,b_cert,user_id) VALUES(:l,:e,:sp,:hf,:cert,:lp,:cp,:ms,:bc,:us)",
                   l=l,e=e,sp=sp,hf=hf,cert =cert,lp=lp,cp = cp,ms=ms,bc =bc,us = userid)
       db.execute("INSERT INTO info (user_id,f_name,l_name,m_stat,phone,location,state,sex,dob,id_name,id_no,photo) Values (:u,:f,:l,:m,:p,:l,:s,:sx,:dob,:id,:idn,:pic)",
                   u=userid,f=fname,l=lname,m=status,p=pnum,s =states, sx=sex,dob=dob,id=idn,idn=nid,pic=fille.filename)
       return render_template('index.html')
    return render_template('d_register.html',states=states)

@app.route('/message',methods=['GET','POST'])
def message():
   if request.method == 'POST':
      if session['user_id']:
         current = request.form.get('message')
         user = db.execute('select user_id from message where user_id =:sess',sess = session['user_id'])
         if len(user) != 0:
            db.execute('insert into messge (sender,reciever,mess) values(:se,re,me)',se=:cu)
            mess = db.execute('select sender,reciever, message from message where sender =:sess or reciever =: sess order by date',sess = session['user_id'])

map.save('map.html')
# out of the context
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


