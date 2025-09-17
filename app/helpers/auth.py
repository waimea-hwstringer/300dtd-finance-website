#===========================================================
# Auth Related Functions
#===========================================================

from flask import redirect, session, flash
from functools import wraps


#-----------------------------------------------------------
# A decorator function to check user logged in
# - This is determined by a 'logged_in' value being present
#   in the session
#-----------------------------------------------------------
def login_required(func):
    @wraps(func)
    # Wrap a given function...
    def wrapper(*args, **kwargs):

        # Is the user logged in?
        if 'logged_in' in session:
            # Yes, so run function
            return func(*args, **kwargs)

        # No, so go to home page
        flash("You need to be logged in to access that page", "error")
        return redirect("/")

    return wrapper



#-----------------------------------------------------------
# A decorator function to check user logged in
# - This is determined by a 'logged_in' value being present
#   in the session
#-----------------------------------------------------------
def admin_required(func):
    @wraps(func)
    # Wrap a given function...
    def wrapper(*args, **kwargs):

        # Is the user logged in?
        if session.get('is_admin'):
            # Yes, so run function
            return func(*args, **kwargs)

        # No, so go to home page
        flash("You need to be an admin to access this page", "error")
        return redirect("/")

    return wrapper


