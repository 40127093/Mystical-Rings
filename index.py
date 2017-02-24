# importing necessary libraries

import ConfigParser , os
import logging

from functools import wraps

from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, flash, url_for,session
app = Flask(__name__)
app.secret_key = 'supersecret'

from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER

# routing to individual pages

@app.route("/")
def root():
  this_route = url_for('.root')
  app.logger.info("Logging a test message from " + this_route)
  return render_template('pamela-love.html'), 200


@app.route("/pamela-love/")
def pl():
  return render_template('pamela-love.html'), 200


@app.route("/mania-mania/") 
def mm():
  return render_template('mania-mania.html'), 200


@app.route("/eilisain-jewelry/")
def ej():
  return render_template('eilisain.html'), 200


@app.route("/blood-milk-jewels/")
def bmj():
  return render_template('blood-milk-jewels.html'), 200


@app.route("/omnia-oddities/")
def oo():
  return render_template('omnia-oddities.html'), 200


# uploading images function that uses an external library to store files under
# their original name. Addition of a message flashing feature to indicate to the users the successful
# upload of their images


@app.route("/upload/", methods=['POST','GET'])
def upload():
 try:
  if request.method == 'POST':
     f= request.files['datafile']
     filename = secure_filename(f.filename)
     f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
     flash('Image uploaded successfully!')
     return redirect(url_for('uploaded'))
  else:
     uploads = os.listdir('static/uploads/')
     page = render_template('upload-service.html', uploads = uploads)
     return page, 200
 except IOError, e:
     print "Error: no file was selected, please go back and try again!"
     sys.exit(1)


# function that helps us retrieve the template with the flashed message and
# redirects us again to the upload-service.html template to see the updated
# photo collection after the latest user upload

@app.route('/upload-successful')
def uploaded():
  return redirect(url_for('upload'))

# function that redirects the user to the About Us page

@app.route('/about-us')
def aboutUs():
  return render_template('aboutUs.html')

@app.route('/error')
def IOError():
  return redirect(url_for('upload'))

# custom error handling

@app.errorhandler(404)
def page_not_found(error):
  return render_template('errorPage.html'), 404


# GET-POST requests using a feedback form

@app.route("/contactUs/", methods=['POST','GET'])
def contactUs():
  if request.method == 'POST':
    print request.form
    name = request.form['first_name']
    return render_template('POST-response.html', name = name)
  else:
    page = render_template('contactUs.html')
    return page


# parsing configuration details from an external file

def init (app):
  config = ConfigParser.ConfigParser()
  try:
    config_location = "etc/defaults.cfg"
    config.read(config_location)

    app.config['DEBUG'] = config.get("config", "debug")
    app.config['ip_address'] = config.get("config", "ip_address")
    app.config['port'] = config.get("config", "port")
    app.config['url'] = config.get("config", "url")

    app.config['log_file'] = config.get("logging", "name")
    app.config['log_location'] = config.get("logging", "location")
    app.config['log_level'] = config.get("logging", "level")

  except:
    print "Could not read configuration file from: " , config_location


# setting up a logging feature to record action logs into a text file    

def logs(app):
  log_pathname = app.config['log_location']+ app.config['log_file']
  file_handler = RotatingFileHandler(log_pathname, maxBytes=1024*1024*10 ,
  backupCount=1024)
  file_handler.setLevel( app.config['log_level'])
  formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s")
  file_handler.setFormatter(formatter)
  app.logger.setLevel(app.config['log_level'])
  app.logger.addHandler(file_handler)


# setting up an authentication mechanism to control user access rights

   # hardcoding the login credentials

valid_email = 'super-user@napier.ac.uk'
valid_pwhash = 'password'

   # authentication mechanism

def check_auth(email, password):
    if(email == valid_email and 
        password == valid_pwhash):
            return True
    return False

   # setting the status of the user
   
def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        status = session.get('logged_in', False)
        if not status:
            return redirect(url_for('.login'))
        return f(*args, **kwargs)
    return decorated

  # function that controls the logout user request

@app.route('/logout/')
def logout():
    session['logged_in'] = False
 #  return redirect(url_for('.root'))
    flash("You have successfully logged out from our website. Some features will not be available to you. To see the full content or this website please login again")
    return redirect(url_for('.logged_out'))

 # function that redirects the user to the logout page

@app.route("/logged-out/")
def logged_out():
    return render_template('logged-out.html')

  # redirect function for the logged-in users

@app.route("/super-user/")
@requires_login
def secret():
    return render_template('logged-in.html')

  # function that controls the login request

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['email']
        pw = request.form['password']
        
        if check_auth(request.form['email'], request.form['password']):
            session['logged_in'] = True
            flash("Congratulations, you are not logged in! You may enjoy the full content of this website")
            return redirect(url_for('.secret'))
        else:  
            error = 'Invalid Credentials, please try again!' 
    return render_template('login.html', error=error)

# initialisation function

if __name__ == "__main__":
  init(app)
  logs(app)
  app.run(
    host = app.config['ip_address'],
    port = int(app.config['port']))
