#===========================================================
# YOUR PROJECT TITLE HERE
# Harry Stringer
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================


from flask import Flask, render_template, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.auth    import login_required
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now

# GIT BASH
# source venv/Scripts/activate
# flask run --debug

# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Landing page route
#-----------------------------------------------------------
@app.get("/")
def index():
    return render_template("pages/landing.jinja")


#-----------------------------------------------------------
# Home page route (posts feed)
#-----------------------------------------------------------
@app.get("/home/")

def home():
    with connect_db() as client:
        # Get all the things from the DB
        sql = """
            SELECT 
                posts.id AS p_id,
                posts.author,
                posts.title,
                posts.content,
                posts.video_id,
                posts.min_tier,
                users.id AS u_id,
                users.username,
                users.tier 
            FROM posts
            JOIN users ON posts.author = users.id
            ORDER BY posts.date DESC
        """
        params=[]
        result = client.execute(sql, params)
        posts = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", posts=posts)

#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/post/<int:id>")
def show_one_post(id):
    with connect_db() as client:
        # Get the thing details from the DB, including the owner info
        sql = """
            SELECT 
                posts.id AS p_id,
                posts.author,
                posts.title,
                posts.content,
                posts.video_id,
                posts.min_tier,
                posts.date,
                users.id AS u_id,
                users.username
            FROM posts
            JOIN users ON posts.author = users.id
            WHERE posts.id=?
        """
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            post = result.rows[0]

        else:
            # No, so show error
            return not_found_error()
        
        # Get the thing details from the DB, including the owner info
        sql = """
            SELECT 
                comments.id      AS c_id,
                comments.author  AS c_author,
                users.username   AS c_username,
                comments.content AS c_content,
                comments.date    AS c_date
                
            FROM comments
            JOIN users ON comments.author = users.id
            WHERE comments.post=?
        """
        params = [id]
        result = client.execute(sql, params)
        comments = result.rows
        
        return render_template("pages/post.jinja", post=post, comments=comments)

#-----------------------------------------------------------
# Route for making a post
# - Restricted to logged in users
#-----------------------------------------------------------
@app.post("/add-comment/<int:id>")
@login_required
def add_a_comment(id):
    # Get the data from the form
    content = request.form.get("content")

    # Sanitise the text inputs
    content = html.escape(content)

    # Get the user information from the session
    user_id = session["user_id"]

    post = id

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO comments (author, post, content) VALUES (?, ?, ?)"
        params = [user_id, post, content]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Comment created", "success")
        return redirect(f"/post/{post}")


#-----------------------------------------------------------
# Route for deleting a comment
# - Post ID included in the route so that when the comment is deleted the user is redirected to the same post after deleting the comment
# - Restricted to logged in users who authored the comment
#-----------------------------------------------------------
@app.get("/delete-comment/<int:p_id>/<int:c_id>")
@login_required
def delete_a_comment(p_id, c_id):
    # Get the user id from the session
    author = session["user_id"]

    with connect_db() as client:
        # Delete the comment from the DB 
        sql = "DELETE FROM comments WHERE id=? AND author=?"
        params = [c_id, author]
        client.execute(sql, params)

        # Go back to the post that the comment used to be on
        flash("Comment deleted", "success")
        return redirect(f"/post/{p_id}")



#-----------------------------------------------------------
# Make a post form route
#-----------------------------------------------------------
@app.get("/new-post/")
def make_a_post_form():
    return render_template("pages/post-new.jinja")

#-----------------------------------------------------------
# Route for making a post
# - Restricted to logged in users
#-----------------------------------------------------------
@app.post("/add-post")
@login_required
def add_a_post():
    # Get the data from the form
    title   = request.form.get("title")
    content = request.form.get("content")
    video   = request.form.get("video")
    tier    = request.form.get("tier")

    # Extract the yt video code from given url
    if video:
        vSplit = video.split("?v=")
        vSplit = vSplit[1].split("&")
        video = vSplit[0]

    # Sanitise the text inputs
    title = html.escape(title)
    content = html.escape(content)
    video = html.escape(video)

    # Get the user information from the session
    user_id = session["user_id"]

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO posts (author, title, content, video_id, min_tier) VALUES (?, ?, ?, ?, ?)"
        params = [user_id, title, content, video, tier]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Post '{title}' created", "success")
        return redirect("/home")
    
#-----------------------------------------------------------
# Route for deleting a post, Id given in the route
# - Restricted to logged in users
#-----------------------------------------------------------
@app.get("/delete-post/<int:id>")
@login_required
def delete_a_post(id):
    # Get the user id from the session
    author = session["user_id"]

    with connect_db() as client:
        # Delete the thing from the DB o
        sql = "DELETE FROM posts WHERE id=? AND author=?"
        params = [id, author]
        client.execute(sql, params)

        # Go back to the home page
        flash("Post deleted", "success")
        return redirect("/home")


#-----------------------------------------------------------
# User's profile page
#-----------------------------------------------------------
@app.get("/user/<int:id>")
def user(id):
    with connect_db() as client:

        # Get all the user info from the DB
        sql = """
            SELECT id, username, tier
            FROM   users
            WHERE  id=?
        """
        params=[id]
        result = client.execute(sql, params)
        if result:
            user = result.rows[0]
        else:
            return not_found_error()
        
        # Get all the user's posts from the DB
        sql = """
            SELECT 
                posts.id AS p_id,
                posts.author,
                posts.title,
                posts.content,
                posts.video_id,
                posts.min_tier,
                posts.date,
                users.id AS u_id,
                'post' AS type
            FROM posts
            
            JOIN users ON posts.author = users.id

            WHERE posts.author=?
        """
        params=[id]
        result = client.execute(sql, params)
        posts = result.rows

        # Get all the user's posts from the DB

        sql = """
            SELECT 
                comments.id AS c_id,
                comments.author,
                comments.post,
                comments.date,
                comments.content,
                NULL AS title,         -- comments don't have titles, videos etc
                NULL AS video_id,
                NULL AS min_tier,
                'comment' AS type
            FROM comments
            WHERE comments.author=?
        """
        params=[id]
        result = client.execute(sql, params)
        comments = result.rows

        # Merge posts and comments into one timeline
        items = posts + comments

        # Sort by date (assuming date is a comparable type, e.g. ISO string or datetime)
        items.sort(key=lambda x: x["date"], reverse=True)  # newest first


        # And show everything on the page
        return render_template(f"pages/user.jinja", user=user, items=items)


#-----------------------------------------------------------
# Admin Dashboard
#-----------------------------------------------------------
@app.get("/admin")
def admin_dashboard():
    
    with connect_db() as client:
        # Delete the thing from the DB o
        sql = "SELECT * FROM users"
        params=[]
        result = client.execute(sql, params)
        users = result.rows

        # Go back to the home page
        return render_template("pages/admin-dashboard.jinja", users=users)
    
    
#-----------------------------------------------------------
# Route for an admin to verify a user
#-----------------------------------------------------------
@app.get("/admin-verify-user/<int:id>")
def admin_verify_user(id):
    
    with connect_db() as client:
        # Delete the thing from the DB o
        sql = """
                UPDATE users 
                SET    verified="1"
                WHERE  id=?
              """
        params=[id]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"User {id} Verified", "success")
        return redirect("/admin")
    

#-----------------------------------------------------------
# Route for an admin to delete a user
#-----------------------------------------------------------
@app.get("/admin-delete-user/<int:id>")
def admin_delete_user(id):
    
    with connect_db() as client:
        # Delete the thing from the DB o
        sql = """
                DELETE 
                FROM users
                WHERE  id=?
              """
        params=[id]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"User {id} Deleted", "success")
        return redirect("/admin")
    
#-----------------------------------------------------------
# Route for an admin to promote another user to admin
#-----------------------------------------------------------
@app.get("/admin-promote-user/<int:id>")
def admin_promote_user(id):
    
    with connect_db() as client:
        # Delete the thing from the DB o
        sql = """
                UPDATE users 
                SET    tier="0"
                WHERE  id=?
              """
        params=[id]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"User {id} Promoted", "success")
        return redirect("/admin")
    


#-----------------------------------------------------------
# User registration form route
#-----------------------------------------------------------
@app.get("/register")
def register_form():
    return render_template("pages/register.jinja")


#-----------------------------------------------------------
# User login form route
#-----------------------------------------------------------
@app.get("/login")
def login_form():
    return render_template("pages/login.jinja")


#-----------------------------------------------------------
# Route for adding a user when registration form submitted
#-----------------------------------------------------------
@app.post("/add-user")
def add_user():
    # Get the data from the form
    name = request.form.get("name")
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    tier = request.form.get("tier")

    with connect_db() as client:
        # Attempt to find an existing record for that user
        sql = "SELECT * FROM users WHERE username = ?"
        params = [username]
        result = client.execute(sql, params)

        # No existing record found, so safe to add the user
        if not result.rows:
            # Sanitise the text
            name = html.escape(name)
            email = html.escape(email)
            username = html.escape(username)
            
            # Salt and hash the password
            hash = generate_password_hash(password)

            # Add the user to the users table
            sql = "INSERT INTO users (name, email, username, password_hash, tier) VALUES (?, ?, ?, ?, ?)"
            params = [name, email, username, hash, tier]
            client.execute(sql, params)

            # And let them know it was successful and they can login
            flash("Registration successful", "success")
            return redirect("/login")

        # Found an existing record, so prompt to try again
        flash("Username already exists. Try again...", "error")
        return redirect("/register")


#-----------------------------------------------------------
# Route for processing a user login
#-----------------------------------------------------------
@app.post("/login-user")
def login_user():
    # Get the login form data
    username = request.form.get("username")
    password = request.form.get("password")

    with connect_db() as client:
        # Attempt to find a record for that user
        sql = "SELECT * FROM users WHERE username = ?"
        params = [username]
        result = client.execute(sql, params)

        # Did we find a record?
        if result.rows:
            # Yes, so check password
            user = result.rows[0]
            hash = user["password_hash"]

            # Hash matches?
            if check_password_hash(hash, password):
                # Yes, so save info in the session
                session["user_id"]   = user["id"]
                session["user_name"] = user["name"]
                session["user_username"] = user["username"]
                session["tier"] = user["tier"]
                session["logged_in"] = True

                if user["tier"] == 0:
                    session["is_admin"] = True
                else:
                    session["is_admin"] = False

                # And head back to the home page
                flash("Login successful", "success")
                return redirect("/home")

        # Either username not found, or password was wrong
        flash("Invalid credentials", "error")
        return redirect("/login")


#-----------------------------------------------------------
# Route for processing a user logout
#-----------------------------------------------------------
@app.get("/logout")
def logout():
    # Clear the details from the session
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("logged_in", None)
    session.pop("is_admin", None)
    session.pop("tier", None)

    # And head back to the home page
    flash("Logged out successfully", "success")
    return redirect("/")

