import functools
from flask import(Blueprint,flash,g,redirect,render_template,request,session,url_for)

from werkzeug.security import check_password_hash,generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Register the user
@bp.route("/register",methods=["POST","GET"])
def register():
    if(request.method == "POST"):
        error = None
        res = request.get_json()
        username = res["email"]
        password = res["password"]
        
        db = get_db()
        
        if(not username):
            error = "Username is required"
        elif(not password):
            error = "Password is required"

        elif(db.execute("SELECT id FROM user WHERE username = ? ",(username,))) .fetchone() is not None:
            error = "User {} is already registered".format(username)
        
        if(error is None):
            db.execute("INSERT INTO user (username,password) VALUES (?,?)",(username,generate_password_hash(password)))
            db.commit()
            return("true")

    return("false")

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        res = request.get_json()
        username = res['email']
        password = res['password']
        db = get_db()
        error = None
        
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
      
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(str(user[2]),str(password)):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            print(session.get('user_id'))
            return("true")

    return('false')

@bp.route("/checkLogin",methods=["GET"])
def checkLogin():
    if(g.user):
        result = g.user[1]
       
        return(result)
    else:
        return("false")

@bp.route('/logout',methods=["GET"])
def logout():
    session.clear()
    return("true")
        
# Registers a function that runs before the view function, no matter what URL is requested.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    print("s",user_id)
    if(user_id is None):
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?',(user_id,)).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return ("false")

        return view(**kwargs)

    return wrapped_view

