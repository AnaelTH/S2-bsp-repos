from functools import wraps
from flask import Blueprint,redirect,request,session,flash
from .db import get_db
from .service import login_required,group_exists
from .members import create_member

def user_not_in_group(view):
    @wraps(view)
    def wrapped(group_id,*args,**kwargs):
        db = get_db()
        cursor = db.cursor()
        user_id = session.get("UserID")
        member_data = cursor.execute("SELECT UserID FROM Members WHERE GroupID = ? AND UserID = ?",[group_id,user_id]).fetchone()
        if member_data:
            flash("Already joined group","error")
            return redirect("/groups/"+group_id)
        return view(group_id,*args,**kwargs)
    return wrapped

def create_request(user_id,group_id):
    """Creates a group request"""
    db = get_db()
    cursor = db.cursor()
    data = [user_id,group_id]
    cursor.execute("INSERT INTO Requests (UserID,GroupID) VALUES (?,?)",data)
    db.commit()

def remove_request(user_id,group_id):
    """removes a group request from database"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Requests WHERE UserID = ? AND GroupID = ?",[user_id,group_id])
    db.commit()

bp = Blueprint("requests",__name__)

@bp.route("/groups/<group_id>/join",methods=["POST"])
@login_required
@group_exists
@user_not_in_group
def join_group(group_id):
    """Add user as public group member"""
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()

    #checking if group is not private
    group_data = cursor.execute("SELECT IsPrivate FROM Groups WHERE GroupID =?;",[group_id]).fetchone()
    if group_data[0]:
        flash("Can't directly join, group is private","error")
        return redirect("/groups/"+group_id)
    
    #User can join
    create_member(user_id,group_id)
    flash("Group successfully joined","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/requests",methods=["POST"])
@login_required
@group_exists
@user_not_in_group
def request_join(group_id):
    """Create join request on private group """
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()
    #checking if group is private
    group_data = cursor.execute("SELECT IsPrivate FROM Groups WHERE GroupID =?;",[group_id]).fetchone()
    if not group_data[0]:
        flash("No need to request join, group is not private","error")
        return redirect("/groups/"+group_id)
    
    #checking if user did not request
    request_data = cursor.execute("SELECT UserID FROM Requests WHERE GroupID = ? AND UserID = ?",[group_id,user_id]).fetchone()
    if request_data:
        flash("Already requested group","error")
        return redirect("/groups/"+group_id)

    #User can send request
    create_request(user_id,group_id)
    flash("Join request sent","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/requests/<request_id>",methods=["POST"])
@login_required
@group_exists
def handle_request(group_id,request_id):
    """Accept or Decline join request"""
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()
    #checking if group is private
    group_data = cursor.execute("SELECT IsPrivate FROM Groups WHERE GroupID =?;",[group_id]).fetchone()
    if not group_data[0]:
        flash("No need to request join, group is not private","error")
        return redirect("/groups/"+group_id)

    #checking if user is owner/admin
    member_data = cursor.execute("SELECT Role FROM Members WHERE GroupID = ? AND UserID = ?",[group_id,user_id]).fetchone()
    if not (member_data[0] in ["Admin","Owner"] ):
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    
    #checking if join request exists
    request_data = cursor.execute("SELECT UserID FROM Requests WHERE GroupID = ? AND UserID = ?",[group_id,request_id]).fetchone()
    if not request_data:
        flash("Join request not found","error")
        return redirect("/groups/"+group_id)
    
    #checking operation choice
    operation = request.form.get("operation")
    if not operation in ["accept","decline"]:
        flash("Invalid operation","error")
        return redirect("/home")
    
    #we can proceed
    message = "Join successfully request declined"
    remove_request(request_id,group_id)
    if (operation == "accept"):
        message = "Join successfully request accepted"
        create_member(request_id,group_id)

    flash(message,"success")
    return redirect("/groups/"+group_id)

