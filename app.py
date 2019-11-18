
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'splite:////emedic.db'
