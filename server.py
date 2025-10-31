
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, jsonify, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from dotenv import load_dotenv; load_dotenv()

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = os.urandom(24)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.139.8.30/proj1part2
#
# For example, if you had username ab1234 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://ab1234:123123@34.139.8.30/proj1part2"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = os.getenv("DB_USER", "")
DATABASE_PASSWRD = os.getenv("DB_PASS", "")
DATABASE_HOST = "34.139.8.30"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

def create_users_table():
    with engine.begin() as conn:
        create_table_command = """
        CREATE TABLE IF NOT EXISTS tc3497.users (
            user_id uuid PRIMARY KEY,
            email text UNIQUE NOT NULL,
            username text,
            password text NOT NULL,
            join_date timestamptz NOT NULL DEFAULT now()
        )
        """
        conn.execute(text(create_table_command))

create_users_table()
#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
	create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	"""
	res = conn.execute(text(create_table_command))
	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
	conn.commit()

@app.before_request
def before_request():
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print(request.args)


	#
	# example of a database query
	#
	select_query = "SELECT name from test"
	cursor = g.conn.execute(text(select_query))
	names = []
	for result in cursor:
		names.append(result[0])
	cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	context = dict(data = names)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html", **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']
	
	# passing params in for each variable into query
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = g.conn.execute(text("SELECT * FROM tc3497.users WHERE email = :email"), {'email': email})
        user_row = cursor.fetchone()
        cursor.close()

        if user_row:
            user = dict(zip(cursor.keys(), user_row))
            if check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                return redirect(url_for('songs_page'))

        flash('Invalid email or password')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form.get('username')

        cursor = g.conn.execute(text("SELECT * FROM tc3497.users WHERE email = :email"), {'email': email})
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash('Email already registered')
            return redirect(url_for('register'))

        user_id = str(uuid.uuid4())
        if not username:
            username = user_id

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        params = {
            'user_id': user_id,
            'email': email,
            'username': username,
            'password': hashed_password,
            'join_date': datetime.utcnow()
        }
        g.conn.execute(text('INSERT INTO tc3497.users(user_id, email, username, password, join_date) VALUES (:user_id, :email, :username, :password, :join_date)'), params)
        g.conn.commit()

        flash('Account created successfully, please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# === 新增：HTML 頁面，直接把 songs 串到模板 ===
@app.route('/songs')
def songs_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # 先抓一些資料（避免一次出太多，先給 200 筆）
    stmt = text("SELECT * FROM tc3497.songs LIMIT 200")
    cursor = g.conn.execute(stmt)
    cols = cursor.keys()                    # 動態取得欄位名稱，不假設 schema
    rows = [dict(zip(cols, row)) for row in cursor]
    cursor.close()
    return render_template("songs.html", cols=cols, rows=rows)

# === 新增：API 端點，回傳 JSON，之後要做前端 fetch 也方便 ===
@app.route('/api/songs')
def api_songs():
    stmt = text("SELECT * FROM tc3497.songs LIMIT 200")
    cursor = g.conn.execute(stmt)
    cols = cursor.keys()
    data = [dict(zip(cols, row)) for row in cursor]
    cursor.close()
    return jsonify(data)


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=True, threaded=threaded)

run()

