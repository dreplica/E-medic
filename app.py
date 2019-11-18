
# import cs50
from flask import Flask, render_template,redirect,session,request
import csv
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
# alchemy is the connection we are to use btw sqlite and python 
from flask_sqlalchemy import SQLAlchemy
# from import the function to encrypt and decrypt password 
app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# you need to import sql to give it to a database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medic.db'
#commence app with database
db = SQLAlchemy(app)

def apology(issue,code):
    return (str(issue)+"is to this code"+str(code))

# class info(db.Model):
#     id = db.column( db.Integer, primary_key = True)
#     user_id = db.column()
#     user_id = db.column()
#     user_id = db.column()
#     user_id = db.column()
#     def __repr__(self):
#         return '<users %r>' % info.user_id

class users(db.Model):
    id = db.Column( db.Integer,primary_key = True)
    user_id = db.Column(db.String(100))
    email = db.Column(db.String(100))
    typ = db.Column(db.String(10))
    password = db.Column(db.String(100))
    def __repr__(self):
        return '<user %r>' % self.user_id

class med_his(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String(100))
    b_type = db.Column(db.String(10))
    g_type = db.Column(db.String(10))
    Med_cond = db.Column(db.String(250))
    def __repr__(self):
        return '<med_his %r>' % self.b_type

@app.route('/')
def index():
   return render_template("index.html",name="david")

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
   return render_template('login.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
   if session["user_id"]:
      session.clear()
      return redirect('index.html')
   return apology('sorry you"re not on this service',400)

@app.route('/register', methods=['GET',"POST"])
def register():
   file = open('states.csv','r')
   reader = csv.reader(file)
   states = list(reader)
   if request.method == 'POST':
      user_id = request.form.get('username')
      email = request.form.get('email')
      passw = request.form.get('password')
      typ = request.form.get('type')
      session['user_id'] = request.form.get['username']
      user = users(user_id,)
      db.session.add(users,email,typ,passw)
      return render_template('index.html')
   else:
      return render_template('register.html', states=states) 

# out of the context
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
   db.create_all()
   app.run(debug = True)

