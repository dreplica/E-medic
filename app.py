import os
import datetime
import csv
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,url_for, send_from_directory
from flask_session import Session
import folium
from werkzeug.utils import secure_filename
from tempfile import mkdtemp
from flask_socketio import SocketIO, send,join_room,leave_room,emit
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

UPLOAD_FOLDER = "static"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Ensure templates are auto-reloaded and picture folder
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
# app.secret_key = 'mysecret key'

Session(app)

app.config['SECRET_KEY'] = 'mysecretkey'
socketio = SocketIO(app,cors_allowed_origins="*") 

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///emed.db")


db.execute("CREATE TABLE IF NOT EXISTS message (id INTEGER PRIMARY KEY AUTOINCREMENT,msg TEXT NOT NULL,send VARCHAR(255) NOT NULL, recieve VARCHAR(255) NOT NULL,hash INTEGER  NOT NULL ,date datetime default current_timestamp )")
db.execute("create table if not exists map(id integer primary key autoincrement, user_id varchar(255),coord1 text not null, coord2 text not null)")
db.execute('create table if not exists hash(hash integer primary key autoincrement,user_id TEXT NOT NULL,doc Text NOT NULL)')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
   return render_template("index.html")


# we are goin to make a jquery ajax post here and another for ajax get
#on recieving data, it should upload it to the database with a 
#immediately a user sends a message it should be recieved and sent back to the reciever

#on get it should just search database and update the user message box
#every one second it makes a get request to db fo recent message
@app.route('/reply', methods=['GET','POST'])
def reply():
   if not 'user_id' in session:
      return redirect('/')
   number = 0#to watch out for post
   hash = '' #to watch out for incoming message hash
   typ = db.execute('select type from users where user_id =:us',us=session['user_id'] )#to  watch out for user typ
   print(typ)
   if request.method == 'POST':
      msg = request.form.get('msg')
      send = request.form.get('sender')
      rec = request.form.get('receiver')
      hash = request.form.get('hash')
      db.execute('insert into message (msg,send,recieve,hash,date) values(:m,:s,:r,:h,:d)',m = msg,s = send,r = rec,h = hash,d = datetime.datetime.now())
      #if send != session['user_id']:
      number += 1
#still have to work here as i have not specified
   if request.args.get('check') == 1:
      print('hello send me the message')
      if number != 0:#if theres a post, return it to the jquery get 
         msg = db.execute('select * from message where hash =:h', h = hash)
         number = 0;
         return jsonify({'msg': msg[-1], 'user': session['user_id'],'hash':hash})

   if request.args.get('name'):#if there is a refernce or click on a doctor, open the docs message 
         check_name = db.execute('select type from users where user_id =:us',us=request.args.get('name') )#check for the type,

         if check_name[0]['type'] == 'pat':#check if the name is a patient
              hash = db.execute('select hash from hash where user_id =:us and doc =:doc',us =request.args.get('name'), doc = session['user_id'] )
              if len(hash) == 0:
                 db.execute('insert into hash (user_id,doc) values(:us,:doc)', us=request.args.get('name'),doc = session['user_id'])
                # return redirect('/reply?name='+request.args.get('name'))
              msg = db.execute('select * from message where hash =:h',h = hash[0]['hash'])
              return jsonify({'msg' :msg, 'user' :session['user_id'],'hash':hash[0]['hash']})

         else:#check if the name is a doc
               hash = db.execute('select hash from hash where user_id =:us and doc =:doc',us = session['user_id'],doc =request.args.get('name') )
               if len(hash) == 0:
                 db.execute('insert into hash (user_id,doc) values(:us,:doc)', us=session['user_id'],doc = request.args.get('name'))
                # return redirect('/reply?name='+request.args.get('name'))
               msg = db.execute('select * from message where hash =:h',h = hash[0]['hash'])
               return jsonify({'msg' :msg, 'user' :session['user_id'],'hash':hash[0]['hash']})

   if request.args.get('doc'):#if there is a refernce or click on a doctor, open the message to commmunicate with doc
         print('hello i am here')
         hash = db.execute('select hash from hash where user_id =:us and doc =:doc',us = session['user_id'],doc =request.args.get('doc') )
         if len(hash) == 0:
                 db.execute('insert into hash (user_id,doc) values(:us,:doc)', us=session['user_id'],doc = request.args.get('doc'))
         friends =  db.execute('select doc from hash where user_id =:us',us = session['user_id'])
         print(friends)
         return render_template('reply.html', friends = friends, typ = typ[0]['type'],user = session['user_id'])

   else:#else just open the message and pass data files
      if typ[0]['type'] == 'pat':#check if the person is a patient'
             friends =  db.execute('select doc from hash where user_id =:us',us = session['user_id'])
             print(friends)
             return render_template('reply.html', friends = friends, typ = typ[0]['type'],user = session['user_id'])
      else:#check if the person is a doc
             print("a docotr")
             friends =  db.execute('select user_id from hash where doc =:doc',doc = session['user_id'])
             print(friends)
             return render_template('reply.html', friends = friends, typ = typ[0]['type'],user = session['user_id'])
             

@app.route('/login',methods=['GET','POST'])
def login():
   session.clear()
   if request.method == 'POST':
      name = request.form.get('username')
      password = request.form.get('password')
      
      usererror = "Enter username"
      passworderror = "Enter password"
      invalid = "Invalid username and password"

      if not name:
         return render_template("login.html", issue1=usererror)
      elif not password:
         return render_template("login.html", issue2=passworderror)

      user = db.execute("Select * from users where user_id=:us", us=name)
      
      if len(user) != 1 or not check_password_hash(user[0]['password'], password):
         return render_template("login.html", issue3=invalid)
         
      session['user_id'] = user[0]['user_id']
      if user[0]['type'] == 'pat':
         print(user[0]['type'])
         return redirect('/patient')#,history = consult)
      else:
         return redirect('/doctor')
   return render_template("login.html")


@app.route('/logout')
def logout():
   session.clear()
   return redirect('/') 


@app.route('/doctor',methods=['GET','POST'])
def doctor(): 
   if request.method == 'GET':      
      if 'user_id' in session:
         user_id = session['user_id']
         lat = request.args.get('lat')         
         if lat:
            user_id = session['user_id']
            lng = request.args.get('lng')
            check_map = db.execute("select user_id from map where user_id =:us",us=user_id)

            if len(check_map) != 0: 
               db.execute("UPDATE map SET coord1 =:lat,coord2 =:lng where user_id =:us",us=user_id,lat = lat,lng = lng)
            else:
               db.execute('INSERT INTO map(user_id,coord1,coord2)values(:us,:la,:lng)',us = user_id,la = lat,lng = lng)

         user = db.execute('select * from users where user_id=:us',us = user_id)
         row = db.execute("select * from info where user_id=:us", us=user_id)
         pat =  db.execute("select * from consultation where doc=:us", us = user_id)

         if len(pat) == 0:
            return render_template('doctor.html',user=user, row=row)
         pat_one = pat[-1]
         pat_info = db.execute("select * from info where user_id =:pat", pat = pat_one['user_id'])
         if len(pat_info) != 0:
            return render_template('doctor.html',user=user, row=row, pat=pat, pat_one = pat_one, pat_info=pat_info)    
         else:
            return render_template('doctor.html', user=user, row=row)
   
   return redirect('/')


@app.route('/patient',methods=['GET','POST'])
def patient():
   if request.method == 'GET':
      if 'user_id' in session:
         lat = request.args.get('lat')
         user_id = session['user_id']
         if lat:
            user_id = session['user_id']
            lng = request.args.get('lng')
            check_map = db.execute("select user_id from map where user_id =:us",us=user_id)
            if len(check_map) != 0: 
               db.execute("UPDATE map SET coord1 =:lat,coord2 =:lng where user_id =:us",us=user_id,lat = lat,lng = lng)
            else:
               db.execute('INSERT INTO map(user_id,coord1,coord2)values(:us,:la,:lng)',us = user_id,la = lat,lng = lng)

         user = db.execute('select * from users where user_id=:us',us = user_id)
         row = db.execute("select * from info where user_id=:us", us=user_id)
         doc =  db.execute('select * from consultation where user_id=:us',us = user_id)
         
         if len(doc) == 0:
            return render_template('patient.html', user=user, row=row)
         doc_one  = doc[-1]   
         doc_info = db.execute('select * from info where user_id =:doc',doc = doc_one['doc'])
         if len(doc_info) != 0:             
             return render_template('patient.html', user=user, row=row, doc = doc, doc_one = doc_one, doc_info = doc_info)
         else:
            return render_template('patient.html', user=user, row=row)
   return redirect("/")  

@app.route('/print',methods=['GET','POST'])
def printt():
   if 'user_id'  in session:
      consult = db.execute('select * from consultation where user_id =:us', us=session['user_id'])
      user = db.execute('select * from users where user_id=:us',us =session['user_id'])
      row = db.execute("select * from info where user_id=:us", us=session['user_id'])
      return render_template('print.html' ,consult = consult,user = user,row = row)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
   if 'user_id' in session:
      user_id = session['user_id']
      user = db.execute('select * from users where user_id=:us',us =user_id)
      row = db.execute("select * from info where user_id=:us", us=user_id)
      return render_template("profile.html", user=user, row=row)
   else:
      return redirect("/")

@app.route('/update', methods=['GET', 'POST'])      
def update():
   user_id = session['user_id']
   pic = db.execute("select photo from info where user_id=:us", us=user_id)   
   oldpass = db.execute("select password from users where user_id=:us", us=user_id)   
   if request.method =="POST":
      if 'user_id' in session:
         email = request.form.get("email")
         number = request.form.get("num")
         mstat = request.form.get("mstat")
         address = request.form.get("loc")
         fille = request.files['picture']         
         password = request.form.get("password")
       
         if password == '':
            newpass = oldpass[0]['password']   
         else:
            newpass = generate_password_hash(password,'pbkdf2:sha256',8)    
        
         if not fille.filename == '':
            fille.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fille.filename)))

         new_image = fille.filename if fille.filename else pic[0]['photo']

         if not email or not number or not address or not new_image:
            return render_template("profile.html")
         else:
            db.execute("UPDATE users SET email=:email, password=:password WHERE user_id=:user_id", user_id=user_id, email=email, password=newpass)
            db.execute("UPDATE info SET phone=:phone, location=:location, m_stat=:mstat, photo=:photo WHERE user_id=:user_id", user_id=user_id, phone=number, mstat=mstat, location=address, photo=new_image)
            return redirect("/profile")
   return render_template("profile.html")   

def sendEmail(to, subject, message):
   message = Mail(
      from_email='info@mediccare.com.ng',
      to_emails=to,
      subject='Sending with Twilio SendGrid is Fun',
      html_content=message or '<strong>and easy to do anywhere, even with Python</strong>')
   try:
      sg = SendGridAPIClient(os.environ.get('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'))
      response = sg.send(message)
      print(response.status_code)
      print(response.body)
      print(response.headers)
   except Exception as e:
      print(str(e))

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
      if fille.filename == '':
         fille.filename = 'none'
      fille.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fille.filename)))

      subject = "Account Activation"
      message = f"<h3>Dear {fname} {lname}</h3><br>\
               <p>You registered to our website and your account has been activated please visit our site</p>"
      
      msg = "Username already exist"
      check = db.execute("SELECT user_id FROM users WHERE user_id=:username", username=userid)
      if check:
         return render_template("p_register.html", msg=msg)

      session['user_id'] = request.form.get('username')
      # user = users(userid)     
      db.execute("INSERT INTO users (user_id,email,password,type,date) VALUES(:us,:em,:pa,:ty,:da)",da = date,us = userid,em =email,pa=passw,ty=typ)
      db.execute("INSERT INTO pat_info (b_gr,g_gr,med_iss,kin_fn,kin_ln,kin_phone,kin_email,kin_loc,user_id) VALUES(:b,:g,:md,:kfn,:kln,:kp,:ke,:kl,:us)",
                  b=blood,g=geno,md=med,kfn=k_fn,kln = k_ln,kp=kp,ke = ke,kl=k_loc,us = userid)
      db.execute("INSERT INTO info (user_id,f_name,l_name,m_stat,phone,location,state,sex,dob,id_name,id_no,photo) Values (:u,:f,:l,:m,:p,:loc,:s,:sx,:dob,:id,:idn,:pic)",
                  u=userid,f=fname,l=lname,m=status,p=pnum, loc=addr, s =state, sx=sex,dob=dob,id=idn,idn=nid,pic=fille.filename)
      sendEmail(email, subject, message)
      return redirect('/patient')
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
      if fille.filename == '':
         fille.filename = 'none'
      fille.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fille.filename)))

      subject = "Account Activation"
      message = f"<h3>Dear {fname} {lname}</h3><br>\
               <p>You registered to our website and your account has been activated please visit our site</p>"

      msg = "Username already exist"
      check = db.execute("SELECT user_id FROM users WHERE user_id=:username", username=userid)
      if check:
         return render_template("p_register.html", msg=msg)

      session['user_id'] = request.form.get('username')
         #  user = users(userid)      

      db.execute("INSERT INTO users (user_id,email,password,type,date) VALUES(:us,:em,:pa,:ty,:da)",da = date,us = userid,em =email,pa=passw,ty=typ)
      db.execute("INSERT INTO doc_info (lic_yr,exp_yr,specialty,hos_aff,cert,link_pub,con_prac,med_sch,b_cert,user_id) VALUES(:l,:e,:sp,:hf,:cert,:lp,:cp,:ms,:bc,:us)",
                  l=l,e=e,sp=sp,hf=hf,cert =cert,lp=lp,cp = cp,ms=ms,bc =bc,us = userid)
      db.execute("INSERT INTO info (user_id,f_name,l_name,m_stat,phone,location,state,sex,dob,id_name,id_no,photo) Values (:u,:f,:l,:m,:p,:loc,:s,:sx,:dob,:id,:idn,:pic)",
                  u=userid,f=fname,l=lname,m=status,p=pnum,loc=addr,s =state, sx=sex,dob=dob,id=idn,idn=nid,pic=fille.filename)
      sendEmail(email, subject, message)            
      return redirect('/doctor')
   return render_template('d_register.html',states=states)


# #message box side
@app.route('/message',methods=['GET','POST'])
def message():

     if "user_id" in session:
        user = db.execute('select user_id,type from users where user_id =:us',us=session['user_id'])
        row = db.execute("select * from info where user_id=:us", us=session['user_id'])
        print(user)
        rooms = '' 
        if request.method == 'GET': 
           incoming = request.args.get('name')
           check_doc = db.execute('select * from hash where user_id =:us and doc =:doc', us=session['user_id'], doc = incoming)
           if len(check_doc) == 0:
              db.execute('insert into hash (user_id,doc) values(:us,:doc)', us = session['user_id'],doc = incoming)
           rooms =  db.execute('select * from hash where user_id =:us or doc =:us',us = session['user_id'])
           return render_template('message.html',user_id = user[0]['user_id'], row=row,rooms = rooms,type=user[0]['type'],redirected_user = incoming)
        return render_template('message.html',user_id = user[0]['user_id'],row=row, rooms = rooms,type=user[0]['type'])
     return render_template('message.html')

@app.route('/user_checker/<id>')
def userChecker(id):
   user = db.execute("SELECT user_id FROM users WHERE user_id=:username", username=id)
   if user:
      return '<p style="color:red">Username already exists</p>'
   else:
      return '<p style="color:green">Username valid</p>'

@app.route('/email_checker/<id>')
def emailChecker(id):
   email = db.execute("SELECT email FROM users WHERE email=:email", email=id)
   if email:
      return '<p style="color:red">Email already exists</p>'
   else:
      return '<p style="color:green">Email valid</p>'   


@app.route('/map',methods=['GET','POST'])
def loc():
   map = folium.Map(location = [6.5244, 3.3792],zoom_start=12)
   loc = db.execute("select * from map")
   for ma in loc:
      doc_check = db.execute('select type from users where user_id=:id',id=ma['user_id'])
      if ma['user_id'] == session['user_id']:
         folium.Marker([ma['coord1'],ma['coord2']],
         tooltip="<span color:'green'>You</span>",
         icon=folium.Icon(color='green')).add_to(map)
      if doc_check[0]['type'] == 'doc':
         folium.Marker([ma['coord1'],ma['coord2']],popup='<a href="/reply?doc='+ma['user_id']+'">Dr. '+ma['user_id']+'</a>',
         tooltip="click").add_to(map)
   map.save('templates/map.html')
   return render_template('map.html')

@app.route('/consult', methods=['GET','POST'])
def consult():
   if request.method == 'POST':
      if 'user_id' in session:
         name = request.form.get('pname')
         issue = request.form.get('issue')
         date = datetime.datetime.now()
         recomm = request.form.get('recommendation')
         drug = request.form.get('drug')
         date = datetime.datetime.now()
         db.execute('insert into consultation (user_id,issue,recomm,drugs,doc,date) values(:name,:iss,:recco,:dr,:doc,:da)',name =name, iss = issue, recco = recomm, dr = drug,doc = session['user_id'],da = date)
         return redirect('/message')
   return render_template("reply.html")      

#message broadcasting comes here
@socketio.on('message')
def mess(data):
   print(data)
   if data['username']:
       send(data, broadcast=True)

@socketio.on('join')
def join(data):
   join_room(data['active_chat'])
   send({'msg': data['user'] + ' has joined the consulting room', 
             'room':data['active_chat']})

@socketio.on('leave')
def leave(data):

   leave_room(data['active_chat'])
   send({'msg': data['user'] + ' has left the consulting room',
             'room': data['active_chat']})
   
#incase of errors from http or other related,this code below watch out for them
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
   socketio.run(app, debug = True)

