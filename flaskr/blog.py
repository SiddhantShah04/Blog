from flask import (Blueprint,g,Flask,redirect,request,session)
from werkzeug.exceptions import abort
import json
from flaskr.auth import login_required
import datetime
from flaskr.db import get_db

bp = Blueprint('blog',__name__)

@bp.route("/blog")  
def index():
    #username = g.user["username"]
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    result = []
    
    for row in posts:
        result.append({"id":row["id"], "authorId":row["author_id"],"username":row["username"],"title":row["title"],"body":row["body"],"date":row["created"].strftime('%Y-%m-%d')})
    
    try:
        id = session['user_id']
        result.append({"id": id})
    except:
        result.append({"id": 0})
    
    result=json.dumps(result)
    return(result)

@bp.route('/create',methods=["GET","POST"])
@login_required
def create():
    if(request.method=="POST"):
        res = request.get_json()
        title = res['title']
        body = res['body']
        error = None
        if(not title):
            error = "title is required"
        if(error is not None):
            return(error)
        else:
            db = get_db()
            db.execute('INSERT INTO post(title,body,author_id) VALUES(?,?,?)',(title,body,g.user[0],))
            db.commit()
            return("true")
        
    return(error)

@bp.route('/update',methods=["GET","POST"])
@login_required
def update():
    if request.method == 'POST':
        res = request.get_json()
        title = res['newtitle']
        body = res['newpost']
        id = res["id"]
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return("true")

    return(post)

@bp.route('/delete',methods=["GET","POST"])
@login_required
def delete():
    res = request.get_json()
    id = int(res["id"]) 
    db = get_db()

    
    db.execute('DELETE FROM post WHERE  id=?',(id,))
    db.commit()
     
    
    return("true")
