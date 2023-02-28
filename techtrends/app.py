import sqlite3
import logging
import json
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    connection = get_db_connection()    
    if post is None:
      logging.warning(f'Non-existing article accessed - Article ID: {post_id}')
      return render_template('404.html'), 404
    else:
      logging.info('Article '+ post['title'] +' retrieved!')
      connection.close()
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('About Us page is retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))           
            connection.commit()
            connection.close()
            logging.info(f'New article is created with Title: {title}')  
            return redirect(url_for('index'))
    
    return render_template('create.html')

@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Status request successfull')
    app.logger.debug('DEBUG message')
    return response

@app.route('/metrics')
def metrics():
    # execute the queries to get the required metrics
    connection = get_db_connection()
    cursor = connection.execute("SELECT COUNT(*) FROM posts")
    post_count = cursor.fetchone()[0]
    cursor = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    db_connection_count = cursor.fetchone()[0]
    
    # create the JSON response
    response = {'db_connection_count': db_connection_count, 'post_count': post_count}
    
    # return the JSON response with a 200 status code
    return jsonify(response), 200


# set logger to handle STDOUT and STDERR 
stdout_logger = logging.Logger(name="stdout_logger", level=logging.DEBUG)
stderr_logger = logging.Logger(name="stderr_logger", level=logging.DEBUG)

stdout_handler = logging.StreamHandler(stream=sys.stdout)
stderr_handler = logging.StreamHandler(stream=sys.stderr)

stdout_logger.addHandler(hdlr=stdout_handler)
stderr_logger.addHandler(hdlr=stderr_handler)
 # format output
stdout_logger.info(sys.stdout)
stderr_logger.info(sys.stderr)

# logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(asctime)s-%(message)s')


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')