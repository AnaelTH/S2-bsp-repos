from flask import Blueprint,redirect,request,session,flash
from .db import get_db
from .service import login_required,group_exists

def create_member(UserID,GroupID,Role="Member"):
    """Adds a new member to a group"""
    db = get_db()
    data = [UserID,GroupID,Role]
    db.cursor().execute("INSERT INTO Members (UserID,GroupID,Role) VALUES (?,?,?)",data)
    db.commit()

def remove_member(group_id,user_id):
    """removes a member from database"""
    db = get_db()
    cursor = db.cursor()
    sessions_data = cursor.execute("SELECT SessionID FROM Sessions WHERE GroupID=?",[group_id]).fetchall()
    tasks_data = cursor.execute("SELECT TaskID FROM Tasks WHERE GroupID=?",[group_id]).fetchall()

    for data in sessions_data:
        cursor.execute("DELETE FROM Attendees WHERE SessionID = ? AND UserID=?",[data[0],user_id])
    for data in tasks_data:
        cursor.execute("DELETE FROM Assignees WHERE TaskID = ? AND UserID=?",[data[0],user_id])

    cursor.execute("DELETE FROM Members WHERE GroupID = ? AND UserID=?",[group_id,user_id])
    db.commit()
def update_role(user_id,group_id,new_role):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE Members SET Role = ? WHERE UserID = ? AND GroupID = ?",[new_role,user_id,group_id])
    db.commit()
bp = Blueprint("members",__name__)

@bp.route("/groups/<group_id>/leave",methods=["POST"])
@login_required
@group_exists
def leave_group(group_id):
    """Removes member from group"""
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()
    #checking if user is in group
    member_data = cursor.execute("SELECT UserID FROM Members WHERE GroupID = ? AND UserID = ?",[group_id,user_id]).fetchone()
    if not member_data:
        flash("You are not a member","error")
        return redirect("/groups/"+group_id)
    #we now can remove member from group
    remove_member(group_id,user_id)
    flash("Successfully left group","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/members/<member_id>/role",methods=["POST"])
@login_required
@group_exists
def set_role(group_id,member_id):
    """Changes member role to Admin/Member"""
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()

    #checking user is in group
    member_data = cursor.execute("SELECT Role FROM Members WHERE GroupID = ? AND UserID = ?",[group_id,user_id]).fetchone()
    if not member_data:
        flash("You are not a member","error")
        return redirect("/groups/"+group_id)
    #checking user role
    if not (member_data[0] in ["Owner"]):
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    #checking target member exists

    target_member_data = cursor.execute("SELECT Role,Users.Username FROM Members INNER JOIN Users ON Users.UserID = Members.UserID WHERE Members.UserID = ? AND GroupID = ?",[member_id,group_id]).fetchone()
    if not target_member_data:
        flash("Member does not exist","error")
        return redirect("/groups/"+group_id)
    
    #getting form data
    new_role = request.form.get("Role")
    
    #checking new role
    if not new_role in ["Admin","Member"]:
        flash("Invalid role"+new_role,"error")
        return redirect("/groups/"+group_id)
    
    if new_role == target_member_data[0]:
        flash(target_member_data[1]+" is already "+new_role,"error")
        return redirect("/groups/"+group_id)
    
    update_role(member_id,group_id,new_role)
    flash(target_member_data[1]+" role updated to "+new_role,"success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/members/<member_id>/kick",methods=["POST"])
@login_required
@group_exists
def kick_member(group_id,member_id):
    """Removes member from group"""
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()

    #checking user is in group
    member_data = cursor.execute("SELECT Role FROM Members WHERE GroupID = ? AND UserID = ?",[group_id,user_id]).fetchone()
    if not member_data:
        flash("You are not a member","error")
        return redirect("/groups/"+group_id)
    #checking user role
    if not (member_data[0] in ["Admin","Owner"]):
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    #checking target member exists
    target_member_data = cursor.execute("SELECT Users.UserID,Users.Username,Members.Role FROM Members INNER JOIN Users ON Users.UserID = Members.UserID WHERE Members.UserID = ? AND GroupID = ?",[member_id,group_id]).fetchone()
    if not target_member_data:
        flash("Member does not exist","error")
        return redirect("/groups/"+group_id)
    #checking target member role:
    if target_member_data[2] =="Owner":
        flash("Cannot kick the owner","error")
        return redirect("/groups/"+group_id)
    #checking target member is not user:
    if target_member_data[0] == user_id:
        flash("Cannot kick yourself","error")
        return redirect("/groups/"+group_id)

    remove_member(group_id,target_member_data[0])
    flash("Successfully kicked "+target_member_data[1],"success")
    return redirect("/groups/"+group_id)

