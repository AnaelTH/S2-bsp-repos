import copy,re
import datetime as dt
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Blueprint,redirect,request,session,flash
from .db import get_db
from .service import get_action_Result,login_required,group_exists

def create_session(GroupID,Name,Date,StartTime,EndTime,Location="",Description=""):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Sessions (GroupID,Name,Location,Description,Date,StartTime,EndTime) VALUES (?,?,?,?,?,?,?)",
               [GroupID,Name,Location,Description,Date,StartTime,EndTime])
    db.commit()
def update_session(session_id,data):
    db = get_db()
    cursor = db.cursor()
    for key in data:
        if data[key] and key in ["Name","Location","Description","Date","StartTime","EndTime"]:
            cursor.execute("UPDATE Sessions SET "+key+"=? WHERE SessionID = ?",[data[key],session_id])
    db.commit()
def delete_session(session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Attendees WHERE SessionID = ?",[session_id])
    cursor.execute("DELETE FROM Sessions WHERE SessionID = ?",[session_id])
    db.commit()
def add_attendee(user_id,session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Attendees (UserID,SessionID) VALUES (?,?)",[user_id,session_id])
    db.commit()
def remove_attendee(user_id,session_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Attendees Where UserID = ? AND SessionID = ?",[user_id,session_id])
    db.commit()

bp = Blueprint("sessions",__name__)
@bp.route("/groups/<group_id>/sessions",methods=["POST"])
@login_required
@group_exists
def create_session_view(group_id):
    """Creates session and adds it to the database""" 
    db = get_db()
    cursor = db.cursor() 
    user_id = session.get("UserID")
    
    #checking user rights
    user_role = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?;",[group_id,user_id]).fetchone()

    if not (user_role and user_role[0] in ["Admin","Owner"]) :
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    
    #retrieving message data
    data = {"Name":request.form.get("Name").strip(),"Location":request.form.get("Location"),
                 "Description":request.form.get("Description"),"Date":request.form.get("Date"),
                 "StartTime":request.form.get("StartTime"),"EndTime":request.form.get("EndTime"),"timezone":request.form.get("timezone")}
    #Filtering all session details
    formaterror = "Doesn't match format"
    issues = {}
    #checking Name
    if not re.match(r"^[a-zA-Z0-9\.\+\*°_\(\)\- ]{2,30}$",data["Name"]):
        issues["nameerror"] = formaterror
    
    #checking Location  
    if not re.match("^.{0,30}$",data["Location"]):
        issues["locationerror"] = formaterror

    #checking Description
    if not re.match("^.{0,200}$",data["Description"]):
        issues["descriptionerror"] = formaterror
    
    current_date_time = datetime.now(dt.timezone.utc)
    tz = ZoneInfo(data["timezone"])

    #creating datetime object
    form_start_time = datetime.fromisoformat(f'{data["Date"]}T{data["StartTime"]}')
    form_end_time = datetime.fromisoformat(f'{data["Date"]}T{data["EndTime"]}')
    #specifying timezone offset
    form_start_time = form_start_time.replace(tzinfo=tz)
    form_end_time = form_end_time.replace(tzinfo=tz)

    #converting to Utc
    UTCform_start_time = form_start_time.astimezone(dt.timezone.utc)
    UTCform_end_time = form_end_time.astimezone(dt.timezone.utc)
    
    #checking date:
    if current_date_time.date() > UTCform_start_time.date():
        issues["dateerror"] = "Invalid date"
    #checking time
    if current_date_time > UTCform_start_time:
        issues["starttimeerror"] = "Invalid start time"
    #checking if endtime is earlier than current time
    if current_date_time > UTCform_end_time:
        issues["endtimeerror"] = "Invalid end time"
    #checking if endtime is earlier than starttime
    if UTCform_end_time <= UTCform_start_time:
        issues["endtimeerror"] = "Invalid end time"
    
    if len(issues) > 0:
        action_result = get_action_Result()
        action_result["CreateSession"] = {"createsession":data,"issues":{"createsession":issues}}
        flash("Session creation failed","error")
        return redirect("/groups/"+group_id)
    
    #checking session doesn't overlap another
    fetch_result = cursor.execute("SELECT SessionID FROM Sessions WHERE Date = ? AND StartTime = ? AND EndTime = ?",
                             [UTCform_start_time.date().isoformat(),UTCform_start_time.time().isoformat(timespec="minutes"),UTCform_end_time.time().isoformat(timespec="minutes")]).fetchone()
    if fetch_result:
        issues["dateerror"] = "Time slot already taken"
        issues["endtimeerror"],issues["starttimeerror"] = "",""
        action_result = get_action_Result()
        action_result["CreateSession"] = {"createsession":data,"issues":{"createsession":issues}}
        flash("Session creation failed: Time slot already taken","error")
        return redirect("/groups/"+group_id)
    
    #Provided fields are Correct
    create_session(group_id,data["Name"],UTCform_start_time.date().isoformat(),UTCform_start_time.time().isoformat(timespec="minutes"),UTCform_end_time.time().isoformat(timespec="minutes"),data["Location"],data["Description"])

    flash("Session successfully created","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/sessions/<session_id>",methods=["POST"])
@login_required
@group_exists
def edit_session_view(group_id,session_id):
    """Edits session and updates the database"""  
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()

    #checking user rights
    user_role = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?;",[group_id,user_id]).fetchone()

    if not (user_role and user_role[0] in ["Admin","Owner"]) :
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    #retrieving old data & checking session exists
    old_data = db.execute("SELECT Name,Location,Description,Date,StartTime,EndTime FROM Sessions WHERE SessionID = ?",[session_id]).fetchone()
    if not old_data:
        flash("Session doesn't exist","error")
        return redirect("/groups/"+group_id)
    
    #retrieving message data
    Data = {"url":"/groups/"+group_id+"/sessions/"+session_id,"Name":request.form.get("Name").strip(),"Location":request.form.get("Location"),
                 "Description":request.form.get("Description"),"Date":request.form.get("Date"),
                 "StartTime":request.form.get("StartTime"),"EndTime":request.form.get("EndTime"),"timezone":request.form.get("timezone")}
    received_data_copy = copy.deepcopy(Data)

    #Filtering all session details
    formaterror = "Doesn't match format"
    issues = {}

    #checking Name
    if not re.match(r"^[a-zA-Z0-9\.\+\*°_\(\)\- ]{2,30}$",Data["Name"]):
        issues["nameerror"] = formaterror
    elif Data["Name"] == old_data[0] :
        Data.pop("Name")

    #checking Location  
    if not re.match("^.{0,30}$",Data["Location"]):
        issues["locationerror"] = formaterror
    elif Data["Location"] == old_data[1] :
        Data.pop("Location")

    #checking Description
    if not re.match("^.{0,200}$",Data["Description"]):
        issues["descriptionerror"] = formaterror
    elif Data["Description"] == old_data[2] :
        Data.pop("Description")

    current_date_time = datetime.now(dt.timezone.utc)
    tz = ZoneInfo(Data["timezone"])

    #creating datetime object
    form_start_time = datetime.fromisoformat(f'{Data["Date"]}T{Data["StartTime"]}')
    form_end_time = datetime.fromisoformat(f'{Data["Date"]}T{Data["EndTime"]}')
    #specifying timezone 
    form_start_time = form_start_time.replace(tzinfo=tz)
    form_end_time = form_end_time.replace(tzinfo=tz)

    #converting to Utc
    UTCform_start_time = form_start_time.astimezone(dt.timezone.utc)
    UTCform_end_time = form_end_time.astimezone(dt.timezone.utc)
    
    #checking date:
    if current_date_time.date() > UTCform_start_time.date():
        issues["dateerror"] = "Invalid date"
    #checking time
    if current_date_time > UTCform_start_time:
        issues["starttimeerror"] = "Invalid start time"
    #checking if endtime is earlier than current time
    if current_date_time > UTCform_end_time:
        issues["endtimeerror"] = "Invalid end time"
    #checking if endtime is earlier than starttime
    if UTCform_end_time <= UTCform_start_time:
        issues["endtimeerror"] = "Invalid end time"
    
    if len(issues) > 0:
        action_result = get_action_Result()
        action_result["EditSession"] = {"editsession":received_data_copy,"issues":{"editsession":issues}}
        flash("Session creation failed","error")
        return redirect("/groups/"+group_id)
    
    #checking if values are different
    oldDate,oldStartTime,oldEndTime = old_data[3],old_data[4],old_data[5]
    if oldDate == UTCform_start_time.date().isoformat():
        Data.pop("Date")
    if oldStartTime == UTCform_start_time.time().isoformat(timespec="minutes"):
        Data.pop("StartTime")
    if oldEndTime == UTCform_end_time.time().isoformat(timespec="minutes"):
        Data.pop("EndTime")

    #checking session doesn't overlap another
    fetch_result = db.execute("SELECT SessionID FROM Sessions WHERE Date = ? AND StartTime = ? AND EndTime = ?",
                             [UTCform_start_time.date().isoformat(),UTCform_start_time.time().isoformat(timespec="minutes"),UTCform_end_time.time().isoformat(timespec="minutes")]).fetchone()
    if fetch_result and fetch_result[0] != int(session_id):
        issues["dateerror"] = "Time slot already taken"
        issues["endtimeerror"],issues["starttimeerror"] = "",""
        action_result = get_action_Result()
        action_result["EditSession"] = {"editsession":received_data_copy,"issues":{"editsession":issues}}
        flash("Session edition failed: Time slot already taken","error")
        return redirect("/groups/"+group_id)
    #Provided fields are Correct
    # Fixing data format
    if Data.get("StartTime"): Data["StartTime"]= UTCform_start_time.time().isoformat(timespec="minutes")
    if Data.get("EndTime"): Data["EndTime"]= UTCform_end_time.time().isoformat(timespec="minutes")
    if Data.get("Date"): Data["Date"]= UTCform_start_time.date().isoformat()
    
    update_session(session_id,Data)

    flash("Session successfully edited","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/sessions/<session_id>/delete",methods=["POST"])
@login_required
@group_exists
def delete_session_view(group_id,session_id):
    user_id = session.get("UserID")
    #checking group existence
    db = get_db()
    cursor = db.cursor()
    #checking user rights
    UserRole = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?;",[group_id,user_id]).fetchone()

    if not (UserRole and UserRole[0] in ["Owner","Admin"]) :
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    #checking session exists
    old_data = db.execute("SELECT Name FROM Sessions WHERE SessionID = ?",[session_id]).fetchone()
    if not old_data:
        flash("Session doesn't exist","error")
        return redirect("/groups/"+group_id)
    
    delete_session(session_id)
    flash("Session successfully deleted","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/sessions/<session_id>/attend",methods=["POST"])
@login_required
@group_exists
def attend_session_view(group_id,session_id):
    user_id = session.get("UserID")
    #checking group existence
    db = get_db()
    cursor = db.cursor()
    #checking user rights
    user_role = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?;",[group_id,user_id]).fetchone()

    if not (user_role and user_role[0] in ["Member","Admin","Owner"]) :
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    #checking session exists
    session_data = db.execute("SELECT Name FROM Sessions WHERE SessionID = ?",[session_id]).fetchone()
    if not session_data:
        flash("Session doesn't exist","error")
        return redirect("/groups/"+group_id)
    
    #check if user is not attending session
    attendee_data = db.execute("SELECT UserID FROM Attendees WHERE UserID=? AND SessionID = ?",[user_id,session_id]).fetchone()
    if attendee_data:
        flash("You are already attending that session","error")
        return redirect("/groups/"+group_id)
    #user can attend session

    add_attendee(user_id,session_id)
    flash("Successfully unattended session","success")
    return redirect("/groups/"+group_id)
@bp.route("/groups/<group_id>/sessions/<session_id>/unattend",methods=["POST"])
@login_required
@group_exists
def unattend_session_view(group_id,session_id):
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()
    #checking user rights
    user_role = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?;",[group_id,user_id]).fetchone()
    if not (user_role and user_role[0] in ["Member","Admin","Owner"]) :
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    #checking session exists
    session_data = db.execute("SELECT Name FROM Sessions WHERE SessionID = ?",[session_id]).fetchone()
    if not session_data:
        flash("Session doesn't exist","error")
        return redirect("/groups/"+group_id)
    #check if user is attending session
    attendee_data = db.execute("SELECT UserID FROM Attendees WHERE UserID=? AND SessionID = ?",[user_id,session_id]).fetchone()
    if not attendee_data:
        flash("You are not attending that session","error")
        return redirect("/groups/"+group_id)
    #user can unattend session

    remove_attendee(user_id,session_id)
    flash("Successfully unattended session","success")
    return redirect("/groups/"+group_id)

