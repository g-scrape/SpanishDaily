from flask import Flask, render_template, flash, redirect, url_for, session, request
#from data import Articles
from wtforms import Form, StringField, SelectField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import mysql.connector
import os
from itsdangerous import URLSafeSerializer, BadData
import json
from verifyEmail import sendVerificationEmail
from datetime import date

#grab envVars locally or in prod
path = ''
if os.name == 'nt':
    path = 'C:/Users/glens/.spyder-py3/Practice Projects/SpanishDaily/SpanishDaily/home/gharold/utils/env_vars.py'
elif os.name == 'posix':
    path = '/home/gharold/utils/env_vars.py'

exec(open(path).read())
app = Flask(__name__)
app.secret_key='secret123'

connection = mysql.connector.connect(
    host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASS'),
    database=os.environ.get('DB_NAME')
    )

# Index
@app.route('/',  methods=['GET', 'POST'])
def index():
    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME')
        )

    Register = RegisterForm(request.form)
    if request.method == 'POST' and Register.validate():
        email = Register.email.data
        preference = Register.preferences.data
        spanishLevel = Register.spanishLevel.data
        password = sha256_crypt.encrypt(str(Register.password.data))

        # Create cursor
        cur = connection.cursor(buffered=True)

        #check for existing credentials
        cur.execute("SELECT 1 FROM users where email = %s", [email])
        userCheck = cur.fetchone()
        if userCheck is not None:
            flash('This email is already used, please login', 'danger')
            return redirect(url_for('login'))

        # Execute query
        today = date.today()        
        cur.execute("INSERT INTO users(email, password, spanishLevel, sendEmail, signupDate, verifiedEmail) VALUES(%s, %s, %s, %s, %s, %s)", (email, password, spanishLevel, 0, today, 0))
        cur.execute("SELECT userId FROM users WHERE email = %s", [email])

        #idk, the fetchall returns a tuple inside a list so need to index the FK int
        uid = cur.fetchall()

        uid = uid[0][0]

        cur.execute("INSERT INTO preferences(userId, preference) VALUES(%s, %s)", (uid, str(preference)))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        # session['logged_in'] = True
        # session['email'] = email
        # flash('You are now registered and can log in', 'success')
        sendVerificationEmail(email)
        flash('You are now registered! A verification email has been sent to your inbox. Please confirm your email to complete the account setup', 'success')

        # return redirect(url_for('profile'))
    #get samples into /home. Should refactor this to reduce db calls for scalabilility
    cur = connection.cursor(dictionary=True)
    cur.execute('SELECT Url, diff, topic FROM samples')
    samples = cur.fetchall()
    samples = json.dumps(samples)
    
    return render_template('home.html', Register=Register, samples=samples)

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME')
        )
    #declare all genres
    genres = ['Sports', 'News', 'Politics', 'Travel', 'Tech', 'Finance']

    # Create cursor
    cur = connection.cursor(buffered=True, dictionary=True)

    # Get uid
    cur.execute("SELECT userId FROM users WHERE email = %s", [session['email']])

    uid = cur.fetchone()

    uid = uid['userId']

    #Pull preferences based on uid
    cur.execute("SELECT preference FROM preferences WHERE userId = %s", [uid])
    preference = cur.fetchone()
    preference = preference['preference']

    #loop through preferences to determine which are selected vs not
    genres.remove(preference)

    if request.method == 'POST':
        try:
            # Get users selected genre
            updateChoice = request.form['genreChoice']
            #reset preference to the selected choice
            preference = updateChoice
            # Update user's preferences with their selection
            cur.execute("UPDATE preferences SET preference = %s WHERE userId = %s", (updateChoice, uid))
            # Commit to DB
            connection.commit()
            flash('Preference updated to: ' + updateChoice, 'success')
        except:
            print('exception occured')



    # Close connection
    cur.close()

    #preferences = ['Sports', 'News', 'Politics', 'Travel', 'Tech', 'Finance']

    return render_template('profile.html', preference=preference, genres=genres)



# Register Form Class
class RegisterForm(Form):
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Length(min=6, max=50)])
    preferences = SelectField('Preferred Article Topic', choices=[(None, '---'), ('Sports', 'Sports'), ('News', 'News'), ('Politics', 'Politics'), ('Travel', 'Travel'), ('Tech','Tech'), ('Finance','Finance')])

    spanishLevel = SelectField('Article Difficulty Level', choices=[(None, '---'), ('Very Easy','Very Easy'), ('Easy', 'Easy'), ('Fairly Easy', 'Fairly Easy'), ('Standard', 'Standard'), ('Fairly Difficult', 'Fairly Difficult'), ('Difficult', 'Difficult'), ('Very Difficult', 'Very Difficult')])

    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#one time article Form Class
class SampleArticle(Form):
    samplePreference = SelectField('Preferred Article Topic', choices=[(None, '---'), ('Sports', 'Sports'), ('News', 'News'), ('Politics', 'Politics'), ('Travel', 'Travel'), ('Tech','Tech'), ('Finance','Finance')])

    sampleSpanishLevel = SelectField('Article Difficulty Level', choices=[(None, '---'), ('Very Easy','Very Easy'), ('Easy', 'Easy'), ('Fairly Easy', 'Fairly Easy'), ('Standard', 'Standard'), ('Fairly Difficult', 'Fairly Difficult'), ('Difficult', 'Difficult'), ('Very Difficult', 'Very Difficult')])    

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    connection = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME')
        )
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        cur = connection.cursor()

        # Get user by username
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        result = cur.fetchall()
        #Close connection
        cur.close()
        if len(result) > 0:
            # Get stored hash
            password = result[0][2] #hardcoded to password index

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email

                flash('You are now logged in', 'success')
                return redirect(url_for('profile'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'Email not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

# unsubscribe
@app.route('/unsubscribe/<token>')
def unsubscribe(token):
    s = URLSafeSerializer(os.environ.get('SECRET_KEY'), salt='unsubscribe')

    try:
        email = s.loads(token)
        print(email)
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME')
            )

        # Create cursor
        cur = connection.cursor()

        # Get uid
        cur.execute("UPDATE users SET sendEmail = 0 WHERE email = %s", (email,))

        # Commit to DB
        connection.commit()
        flash('You are now unsubscribed', 'info')
    except BadData:

        flash('Token invalid, please login to unsubscribe', 'danger')

    return render_template('unsubscribe.html')

# verify email
@app.route('/verify/<token>')
def verify(token):
    s = URLSafeSerializer(os.environ.get('SECRET_KEY'), salt='verify')
    
    try:
        email = s.loads(token)
        print(email)
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASS'),
            database=os.environ.get('DB_NAME')
            )   
   
        # Create cursor
        cur = connection.cursor()
    
        # Get uid
        cur.execute("UPDATE users SET verifiedEmail = 1, sendEmail = 1 WHERE email = %s", (email,))    
        
        # Commit to DB
        connection.commit()
        flash('Your email is now verified; please log in', 'info')        

    except BadData:
        flash('Token invalid, please register again', 'danger')
   

    return redirect(url_for('login'))

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True, use_reloader=False)
