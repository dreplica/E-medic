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
# Ensure templates are auto-reloaded and picture folder
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def apology(issue,code):
   return (str(issue)+" "+str(code))
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///emed.db")
db.execute("CREATE TABLE IF NOT EXISTS message (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id VARCHAR(255) NOT NULL,msg TEXT NOT NULL,send VARCHAR(255) NOT NULL, recieve VARCHAR(255) NOT NULL,date datetime default current_timestamp )")
db.execute("create table if not exists map(id integer primary key autoincrement, user_id varchar(255),coord1 text not null, coord2 text not null)")

@app.route('/')
def index():

   return render_template("index.html",person = ['type','name'])


@app.route('/login',methods=['GET','POST'])
def login():
   session.clear()
   if request.method == 'POST':
      name = request.form.get('username')
      password = request.form.get('password')

      if not name and not password:
         return apology("please go back and enter appropriate details",404)

      user = db.execute("Select * from users where user_id=:us", us=name)
      
      if len(user) != 1 or not check_password_hash(user[0]['password'], password):
         return apology("username and password does not match",400)
         
      session['user_id'] = user[0]['user_id']
      if user[0]['type'] == 'pat':
         print(user[0]['type'])
         return redirect('patient')#,history = consult)
      else:
         return redirect('doctor')
   return render_template("login.html")


@app.route('/logout')
def logout():
   session.clear()
   return redirect('/')


@app.route('/doctor',methods=['GET','POST'])
def doctor(): 
   if request.method == 'GET':
      if 'user_id' in session:
         lat = request.args.get('lat')
         user_id = session['user_id']
         if lat:
            user_id = session.get("user_id")
            lng = request.args.get('lng')
            check_map = db.execute("select user_id from map where user_id =:us",us=user_id)

            if len(check_map) != 0: 
               db.execute("UPDATE map SET coord1 =:lat,coord2 =:lng where user_id =:us",us=user_id,coord1 = lat,coord2 = lng)
            db.execute('INSERT INTO map(user_id,coord1,coord2)values(:us,:la,:lng)',us = user_id,la = lat,lng = lng)

      user = db.execute('select * from users where user_id=:us',us = user_id)
      return render_template('doctor.html',user=user)

   user_id = session['user_id']
   user = db.execute('select * from users where user_id=:us',us = user_id)
   return render_template('doctor.html',user=user)


@app.route('/patient',methods=['GET','POST'])
def patient():
   if 'user_id' in session:

      user_id = session.get("user_id")
      user = db.execute('select * from users where user_id=:us',us = user_id)
      return render_template('patient.html', user=user)   

   return redirect('/') 


@app.route('/chats')
def chats():
   if 'user_id' in session:
      user_id = session.get("user_id")
      user = db.execute('select * from users where user_id=:us',us = user_id)
      return render_template("chats.html", user=user)
   return redirect("/")   

@app.route('/profile', methods=['GET', 'POST'])
def profile():
#    if request.method == 'GET':
#          print(session['user_id'])
#          user_id = request.args.get('user')
#          user = db.execute('select * from users where user_id=:us',us = user_id)
#          row = db.execute("select * from info where user_id=:us", us=user_id)
#          print(row)
#          print("this is session 2: ",session['user_id'])
#          return render_template("profile.html", user=user, row=row)
   if 'user_id' in session:
      user_id = session['user_id']
      print("this is session 3: ",session['user_id'])
      user = db.execute('select * from users where user_id=:us',us =user_id)
      row = db.execute("select * from info where user_id=:us", us=user_id)
      print("this is session 4: ",session['user_id'])
      return render_template("profile.html", user=user, row=row)
   return redirect("/")   

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
       session['user_id'] = request.form.get('username')
      #  user = users(userid)
       if fille.filename == '':
          fille.filename = 'none'

       fille.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fille.filename)))
       db.execute("INSERT INTO users (user_id,email,password,type,date) VALUES(:us,:em,:pa,:ty,:da)",da = date,us = userid,em =email,pa=passw,ty=typ)
       db.execute("INSERT INTO pat_info (b_gr,g_gr,med_iss,kin_fn,kin_ln,kin_phone,kin_email,kin_loc,user_id) VALUES(:b,:g,:md,:kfn,:kln,:kp,:ke,:kl,:us)",
                   b=blood,g=geno,md=med,kfn=k_fn,kln = k_ln,kp=kp,ke = ke,kl=k_loc,us = userid)
       db.execute("INSERT INTO info (user_id,f_name,l_name,m_stat,phone,location,state,sex,dob,id_name,id_no,photo) Values (:u,:f,:l,:m,:p,:loc,:s,:sx,:dob,:id,:idn,:pic)",
                   u=userid,f=fname,l=lname,m=status,p=pnum, loc=addr, s =state, sx=sex,dob=dob,id=idn,idn=nid,pic=fille.filename)
       return render_template('patient.html')
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
      #  us = request.form.get('idnum')
       fille = request.files['photo']
       session['user_id'] = request.form.get('username')
      #  user = users(userid)
       if fille.filename == '':
          fille.filename = 'none'

       fille.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fille.filename)))
       db.execute("INSERT INTO users (user_id,email,password,type,date) VALUES(:us,:em,:pa,:ty,:da)",da = date,us = userid,em =email,pa=passw,ty=typ)
       db.execute("INSERT INTO doc_info (lic_yr,exp_yr,specialty,hos_aff,cert,link_pub,con_prac,med_sch,b_cert,user_id) VALUES(:l,:e,:sp,:hf,:cert,:lp,:cp,:ms,:bc,:us)",
                   l=l,e=e,sp=sp,hf=hf,cert =cert,lp=lp,cp = cp,ms=ms,bc =bc,us = userid)
       db.execute("INSERT INTO info (user_id,f_name,l_name,m_stat,phone,location,state,sex,dob,id_name,id_no,photo) Values (:u,:f,:l,:m,:p,:loc,:s,:sx,:dob,:id,:idn,:pic)",
                   u=userid,f=fname,l=lname,m=status,p=pnum,loc=addr,s =state, sx=sex,dob=dob,id=idn,idn=nid,pic=fille.filename)
       return redirect('doctor')
    return render_template('d_register.html',states=states)


#message box side
@app.route('/message',methods=['GET','POST'])
def message():
   if request.method == 'POST':
      if 'user_id' in session:
         current = request.form.get('message')
         rec = request.form.get('reciever')
         user = db.execute('select * from users where user_id =:sess',sess = session['user_id'])
         if len(user) != 0:
           db.execute('insert into message (user_id,send,recieve,msg) values(:se,:re,:se,:me)',me = current,se = session['user_id'],re =rec)
           mess = db.execute('select send,recieve, msg from message where send =:sess or recieve =:sess order by date',sess = session['user_id'])
           return render_template('message.html',mess = mess)
   if request.method == 'GET':
      mess = db.execute('select send,recieve, msg from message where send =:sess or recieve =:sess order by date',sess = session['user_id'])
      return render_template('message.html',mess = mess)


@app.route('/map',methods=['GET','POST'])
def loc():
   map = folium.Map(location = [6.5244, 3.3792],zoom_start=12)
   loc = db.execute("select * from map")

   for ma in loc:
      folium.Marker([ma['coord1'],ma['coord2']],popup='<a href="\profile?user='+ma['user_id']+'">Dr. '+ma['user_id']+'</strong>',tooltip="click").add_to(map)
   
   map.save('templates/map.html')
   return render_template('map.html')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


