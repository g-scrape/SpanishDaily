from flask import Flask, render_template, flash, redirect, url_for, session, request
#from data import Articles
from wtforms import Form, StringField, SelectField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import mysql.connector
import os

exec(open('/home/gharold/SpanishDaily/env_vars.py').read())
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
        host='gharold.mysql.pythonanywhere-services.com',
        user='gharold',
        password='Weatherdb_96',
        database='gharold$default'
        )
    app.logger.info('in index')
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        preference = form.preferences.data
        password = sha256_crypt.encrypt(str(form.password.data))
        app.logger.info('before cur creation')
        # Create cursor
        cur = connection.cursor(buffered=True)

        #check for existing credentials
        cur.execute("SELECT 1 FROM users where email = %s", [email])
        userCheck = cur.fetchone()
        if userCheck is not None:
            flash('This email is already used, please login', 'danger')
            return redirect(url_for('login'))

        # Execute query
        cur.execute("INSERT INTO users(email, password) VALUES(%s, %s)", (email, password))

        cur.execute("SELECT userId FROM users WHERE email = %s", [email])

        #idk, the fetchall returns a tuple inside a list so need to index the FK int
        uid = cur.fetchall()

        uid = uid[0][0]

        cur.execute("INSERT INTO preferences(userId, preference) VALUES(%s, %s)", (uid, str(preference)))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        session['logged_in'] = True
        session['email'] = email
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('profile'))
    return render_template('home.html', form=form)

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Profile
@app.route('/profile')
def profile():
    connection = mysql.connector.connect(
        host='gharold.mysql.pythonanywhere-services.com',
        user='gharold',
        password='Weatherdb_96',
        database='gharold$default'
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
    preferences = cur.fetchall()

    #loop through preferences to determine which are selected vs not
    for item in preferences:
        if item['preference'] in genres:
            genres.remove(item['preference'])

    # Close connection
    cur.close()

    #preferences = ['Sports', 'News', 'Politics', 'Travel', 'Tech', 'Finance']

    return render_template('profile.html', preferences=preferences, genres=genres)

# Articles
# @app.route('/articles')
# def articles():
#     # Create cursor
#     cur = mysql.connection.cursor()

#     # Get articles
#     result = cur.execute("SELECT * FROM articles")

#     articles = cur.fetchall()

#     if result > 0:
#         return render_template('articles.html', articles=articles)
#     else:
#         msg = 'No Articles Found'
#         return render_template('articles.html', msg=msg)
#     # Close connection
#     cur.close()


# #Single Article
# @app.route('/article/<string:id>/')
# def article(id):
#     # Create cursor
#     cur = mysql.connection.cursor()

#     # Get article
#     result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

#     article = cur.fetchone()

#     return render_template('article.html', article=article)



# Register Form Class
class RegisterForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=50)])
    preferences = SelectField('Preferred Article Topic', choices=[(None, '---'), ('Sports', 'Sports'), ('News', 'News'), ('Politics', 'Politics'), ('Travel', 'Travel'), ('Tech','Tech'), ('Finance','Finance')])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm(request.form)
#     if request.method == 'POST' and form.validate():
#         name = form.name.data
#         email = form.email.data
#         username = form.username.data
#         password = sha256_crypt.encrypt(str(form.password.data))

#         # Create cursor
#         cur = mysql.connection.cursor()



#         # Execute query to create user profile
#         cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

#         # Commit to DB
#         mysql.connection.commit()

#         # Close connection
#         cur.close()
#         session['logged_in'] = True
#         session['email'] = email
#         flash('You are now registered and can log in', 'success')

#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    connection = mysql.connector.connect(
        host='gharold.mysql.pythonanywhere-services.com',
        user='gharold',
        password='Weatherdb_96',
        database='gharold$default'
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


# # Article Form Class
# class ArticleForm(Form):
#     title = StringField('Title', [validators.Length(min=1, max=200)])
#     body = TextAreaField('Body', [validators.Length(min=30)])

# # Add Article
# @app.route('/add_article', methods=['GET', 'POST'])
# @is_logged_in
# def add_article():
#     form = ArticleForm(request.form)
#     if request.method == 'POST' and form.validate():
#         title = form.title.data
#         body = form.body.data

#         # Create Cursor
#         cur = mysql.connection.cursor()

#         # Execute
#         cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))

#         # Commit to DB
#         mysql.connection.commit()

#         #Close connection
#         cur.close()

#         flash('Article Created', 'success')

#         return redirect(url_for('dashboard'))

#     return render_template('add_article.html', form=form)



# # Delete Article
# @app.route('/delete_article/<string:id>', methods=['POST'])
# @is_logged_in
# def delete_article(id):
#     # Create cursor
#     cur = mysql.connection.cursor()

#     # Execute
#     cur.execute("DELETE FROM articles WHERE id = %s", [id])

#     # Commit to DB
#     mysql.connection.commit()

#     #Close connection
#     cur.close()

#     flash('Article Deleted', 'success')

#     return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
