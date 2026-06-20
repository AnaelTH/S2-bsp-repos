import datetime as dt
from flask import session,flash,redirect
from functools import wraps
from datetime import datetime
from .db import get_db

def init_action_result():
    session["ActionResult"] = {"Login":None,"Signup":None,"CreateGroup":None,"EditGroup":None,"EditSession":None}

def get_action_Result():
    """Sets up dict in context session containing results of user operations :
    e.g. signup,login...etc."""
    if not session.get("ActionResult"):
        init_action_result()
    return session["ActionResult"]

def login_required(view):
    @wraps(view)
    def wrapped(*args,**kwargs):
        user_id = session.get("UserID")
        if not user_id:
            flash("Login required","error")
            return redirect("/auth")
        else:
# Session expiration check
            timestamp =  session.get("timestamp")
            now = datetime.now(dt.timezone.utc)
            if (now - timestamp).seconds > 3600  :
                session.clear()
                flash("Session expired","error")
                return redirect("/auth")
        return view(*args,**kwargs)
    return wrapped
def group_exists(view):
    @wraps(view)
    def wrapped(group_id,*args,**kwargs):
        db = get_db()
        base_group_data = db.execute("SELECT Name FROM Groups WHERE GroupID =?;",[group_id]).fetchone()
        if not base_group_data:
            flash("Group inexistant","error")
            return redirect("/home")
        return view(group_id,*args,**kwargs)
    return wrapped
def user_is_owner(view):
    @wraps(view)
    def wrapped(group_id,*args,**kwargs):
        db = get_db()
        user_id = session.get("UserID")
        base_group_data = db.execute("SELECT Name FROM Groups WHERE GroupID =? AND OwnerID = ?",[group_id,user_id]).fetchone()
        if not base_group_data:
            flash("Unauthorized","error")
            return redirect("/groups/"+group_id)
        return view(group_id,*args,**kwargs)
    return wrapped
