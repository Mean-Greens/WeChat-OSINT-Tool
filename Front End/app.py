import os
from pathlib import Path
from flask import Flask, session, render_template, request, redirect, url_for, flash, send_from_directory #CSRFProtect
from dotenv import load_dotenv
import psycopg2
import hashlib
import sys
from markupsafe import Markup
import markdown

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LangFlask.query import query, query_translation
from LangFlask.constants import set_shared_variable, get_shared_variable

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET")
#csrf = CSRFProtect(app)


# ------------------------ Database connection stuff, but no dastabse so commented out to limit bugs for now ------------------------ #


# Enforce user authentication on each request
# @app.before_request
# def default_login_required():
#     # exclude 404 errors and static routes
#     # uses split to handle blueprint static routes as well
#     if not request.endpoint or request.endpoint.rsplit('.', 1)[-1] == 'static':
#         return

#     view = app.view_functions[request.endpoint]

#     if getattr(view, 'login_exempt', False):
#         return

#     if 'userid' not in session:
#         return redirect(url_for('login'))

# Read a markdown file and convert its content to HTML
def read_markdown_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    return markdown.markdown(content)

# Establish and return a connection to the database
def get_db_connection():
   conn = psycopg2.connect(
       host=os.getenv("DB_HOST"),
       user=os.getenv("DB_USER"),
       password=os.getenv("DB_PASSWORD"),
       database=os.getenv("DB_DATABASE")
   )
   return conn

# Render the index page and apply filters if provided
def index():
    filters = {}
    if request.method == "POST":
        # Handle form data
        date_filter = request.form.get("date")
        user_filter = request.form.get("user")
        if date_filter:
            filters['Date'] = date_filter
        if user_filter:
            filters['User'] = user_filter

    return render_template("index.html", filters=filters)

# Load words from the file (maintain original order)
def load_words():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LangFlask/Wordlist.txt"), "r", encoding="utf-8") as file:  # Use UTF-8 encoding for non-English characters
        words = file.read().splitlines()
        chinese_search_terms = file.read().splitlines()[1::2]
    return words

# Add a word to the file
def add_word(new_word):
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LangFlask/Wordlist.txt"), "a", encoding="utf-8") as file:
        chinese_word = query_translation(new_word)
        file.write(new_word + "\n")  # Add the word followed by a newline
        if chinese_word:
            file.write(chinese_word + "\n")

# Retrieve user-specific lists from the database
def get_user_lists():
     # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT listid, listname FROM userlist WHERE userid=%s"
    cursor.execute(query, (str(session["userid"]),))
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# Gets the listid, listname, userid for a specific list
def get_list_info(list_id):
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT listid, listname FROM userlist WHERE (listid = %s AND userid=%s)"
    cursor.execute(query, (list_id, str(session["userid"]),))
    # Get result and close
    result = cursor.fetchone() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# Gets the necessary data to display a user's list
def get_words_in_list(id):
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT ... WHERE (userlist.listid='" + id + "' AND userlist.userid='" + str(session["userid"]) + "')"
    cursor.execute(query)
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# ------------------------ BEGIN ROUTES ------------------------ #
# @app.route("/")
# def home():
#     return render_template("test_search.html")

# Render the test page
@app.route("/")
def test():
    return render_template("test.html")

#@app.route("/newword", methods=['GET', 'POST'])
#def newword():
    #if  request.method == "GET":
        #return render_template("addtowordlist.html")
    #elif request.method == "POST":
        #search_term = request.form['word']
        #results = get_results(word)
        #return render_template("wordlist.html")

# @app.route("/wordlist", methods=['GET', 'POST'])
# def wordlist():
#     if request.method == "GET":
#         words = load_words()
#         return render_template("wordlist.html", words=words)
#     elif request.method == "POST":
#         new_word = request.form.get("new_word", "").strip()
#         if new_word:  # Only add non-empty words
#             add_word(new_word)
#         return redirect(url_for("wordlist"))  # Redirect to avoid form resubmission

@app.route("/wordlist", methods=['GET', 'POST'])
def test_wordlist():
    """
    Handle word list requests.


    This function processes both GET and POST methods:
    - On GET: Loads and displays a formatted list of words.
    - On POST: Adds a new word to the list and redirects back to the list page.


    Returns:
       Response: A rendered HTML template with the word list or a redirect after adding a new word.

    """
    if request.method == "GET":
        words = load_words()
        combined_list = []
        for i in range(0, len(words) - 1, 2):
            combined_list.append(words[i] + ', ' + words[i + 1])
        return render_template("test_wordlist.html", words=combined_list)
    elif request.method == "POST":
        new_word = request.form.get("new_word", "").strip()
        if new_word:  # Only add non-empty words
            add_word(new_word)
        return redirect(url_for("test_wordlist"))  # Redirect to avoid form resubmission

# Display a list of article files
@app.route("/articles", methods=['GET'])
def articles():
    if request.method == "GET":
        files = os.listdir(Path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), f'Articles/')))
        return render_template("articles.html", files=files)

# Serve an article file from the Articles directory
@app.route("/articles/<path:filename>")
def serve_article(filename):
    return send_from_directory(Path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), f'Articles/')), filename)

# @app.route("/results")
# def results():
#     return render_template("results.html")

# Render the test results page
@app.route("/results")
def test_results():
    return render_template("test_results.html")
 
# @app.route("/search", methods=['GET', 'POST'])
# def search():
#     if request.method == "GET":
#         return render_template('search.html')
#     #once they search
#     elif request.method == "POST":
#         search_term = request.form['search_term']
#         results = query(search_term)
#         return render_template('results.html', results=Markup(results))

@app.route("/search", methods=['GET', 'POST'])
def test_search():
    """
    Handle search requests.


    This function processes search requests using both GET and POST methods.
    - On GET: Renders the search page.
    - On POST: Processes the search term and returns formatted results.


    Returns:
       Response: A rendered HTML template with search results or an empty search page.
    """
    if request.method == "GET":
        return render_template('test.html')
    #once they search
    elif request.method == "POST":
        search_term = request.form['search_term']
        if not search_term:
            return render_template('test.html')
        results = query(search_term)
        html_results = markdown.markdown(results)
        results = Markup(html_results)
        return render_template('test_results.html', results=results, search_term=search_term)

# Retrieve and display user-specific lists
@app.route("/list", methods=["GET"])
def retrieve_lists():
    lists = get_user_lists() # Call defined function to get all items
    return render_template("personalwordlists.html", url=request.base_url, lists=lists)

#@app.route("/filters", methods=['GET', 'POST'])
#def filters():
    #if request.method == "GET":
        #return render_template('filters.html')
    #once they search
    #elif request.method == "POST":
        #search_term = request.form['search_term_1']
        #results = get_results(search_term)
        #return render_template('results.html', results=results)
        #return render_template('results.html')

# Render documentation from a markdown file
@app.route("/doc")
def doc():
    md_content = read_markdown_file(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "HOWTOUSE.md"))
    html_content = markdown.markdown(md_content)
    content = Markup(html_content)
    return render_template("doc.html", content=content)

# Handle 404 errors (Page Not Found)
@app.errorhandler(404)
def not_found(e):
    return "Page not found. Please check the URL.", 404

# Decorator used to exempt route from requiring login
def login_exempt(f):
    f.login_exempt = True
    return f

# ------------------------ Login stuff thats commented out for now since no database and I dont want problems ------------------------ #
@app.route('/login', methods=['GET', 'POST'])
@login_exempt
def login():
    """
    Handle user login.


    This function processes user login requests using both GET and POST methods.
    - On GET: Renders the login page.
    - On POST: Handles authentication by verifying the provided username and password
    against stored values in the database.


    If authentication is successful, the user is logged in and redirected to the home page.
    If authentication fails, an error message is displayed.


    Returns:
        Response: A redirect to the home page if login is successful.
                A rendered login page with an error message if login fails.


    Raises:
        Exception: If a database or connection error occurs during login.


    GET:
        Renders the `login.html` template.


    POST:
        Processes the following form data:
            - username (str): The user's username.
            - password (str): The user's password.


       Workflow:
           1. Fetch the hashed password and salt from the database based on the username.
           2. Verify the provided password using the stored salt and hash.
           3. If verification succeeds:
               - Store user data (username, user ID, email) in the session.
               - Redirect to the home page.
           4. If verification fails:
               - Display an error message using `flash`.
               - Return the `login.html` template.


       If login fails:
           - Displays an error message using `flash`.
           - Returns the `login.html` template.
    """
    # If user is signed in, redirect them to home
    if 'userid' in session:
        return redirect(url_for('home'))
    # Render page for GET
    if request.method == "GET":
        return render_template('login.html')
    # Handle login logic
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Execute the SQL query to fetch the hashed password associated with the username
            query = "SELECT passwordhash, salt, userid, emailaddress FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            # If no result found for the given username, return False
            if not result:
                flash(f"Username or password is invalid", 'error')
                return render_template("login.html")
            
            # Extract the salt and hashed password from the result
            hashed_password_in_db, salt, userid, email = result[:4]

            # Verify the password
            if not verify_password(password, salt, hashed_password_in_db):
                flash("Username or password is invalid", 'error')
                return render_template("login.html")
            
            # Set user as logged in
            session["username"] = username
            session["userid"] = userid
            session["email"] = email

            # Render home page
            return redirect(url_for('home'))

        # Handle errors
        except Exception as err:
            flash(f"Unknown error occured during login.", 'error')
            return render_template("login.html")
        finally:
            conn.close()

# Helper function to help verify password hash
def verify_password(password, salt, hashed_password_in_db):
    # Hash the provided password with the salt
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000)
    # Compare the hashed passwords
    return hashed_password.hex() == hashed_password_in_db

# Log users out
@app.route('/logout')
@login_exempt
def logout():
    # Remove session variables
    session.pop('email', None)
    session.pop('username', None)
    session.pop('userid', None)
    return redirect(url_for('login'))

# Handle user registration
@app.route('/register', methods=['GET', 'POST'])
@login_exempt
def register():
    """
    Handle user registration.


   This function processes user registration requests, handling both GET and POST methods.
   - On GET: Renders the registration page.
   - On POST: Handles form submission, validates input, hashes the password, and inserts the new user into the database.


   If registration is successful, the user is logged in and redirected to the home page. 
   If an error occurs during registration, an error message is displayed.


   Returns:
       Response: A redirect to the home page if registration is successful.
                 A rendered registration page with an error message if registration fails.


   Raises:
       Exception: If a database error occurs during user creation.


   GET:
       Renders the `register.html` template.


   POST:
       Processes the following form data:
           - email (str): The user's email address.
           - username (str): The desired username.
           - password (str): The desired password.
           - confirm_password (str): Password confirmation.


       Workflow:
           1. Validates that passwords match.
           2. Hashes the password.
           3. Attempts to insert the user into the database.
           4. Stores user data in the session if successful.
           5. Redirects to the home page.


       If registration fails:
           - Displays an error message using `flash`.
           - Returns the `register.html` template.
    """
    # If user is signed in, send them to the index page
    if 'userid' in session:
        return redirect(url_for('home'))
    # If user is trying to view the page, render the page
    if request.method == "GET":
        return render_template('register.html')
    # Handle logic for user registration
    elif request.method == "POST":
        # Get form values
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirmpassword']

        # Confirm that passwords match
        if password != confirm_password:
            flash("Password and confirm password do not match", 'error')
            return render_template("register.html")

        # Hash the password
        salt, hashed_password = hash_password(password)
        
        # Insert
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (emailaddress, username, passwordhash, salt) VALUES (%s, %s, %s, %s) RETURNING userid;", (email, username, hashed_password, salt))
            conn.commit()
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result == None:
                flash(f"Failed to insert user into database.", 'error')
                print("Failed to create new user in database.")
                return render_template("register.html")
            session["userid"] = result[0]
            session["username"] = username
            session["email"] = email

            # All done, send user home
            return redirect(url_for('home'))
        except Exception as err:
            flash(f"Registration failed: unknown error occured.", 'error')
            return render_template("register.html")
        finally:
            conn.close()

# Helper function to hash passwords
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Generate a random 16-byte salt
    else:
        salt = bytes.fromhex(salt)  # Convert hex string salt back to bytes
    
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex(), hashed_password.hex()

# This function forces the new wordlist to run
@app.route('/force-run', methods=['POST'])
def force_run_endpoint():
    set_shared_variable(True)
    return redirect(url_for("test_wordlist"))

# @app.route("/shelf/list/<id>", methods=['GET'])
# # FIXME only allow to work for logged in user w/ try catch
# def retrieve_list(id):
#     list = get_words_in_list(id)
#     list_info = get_list_info(id)
#     url=request.base_url
#     # Just grab the domain, not anything including a slash or afterwards (for local only, won't work on server b/c htts:// #FIXME)
#     url = url.split("/")[0]
#     return render_template("idkyet.html", list=list, list_info=list_info, url=url) # Return the page to be rendered


# ------------------------ END ROUTES ------------------------ #

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=12345)
