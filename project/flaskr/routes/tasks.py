import copy,re
import datetime as dt
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Blueprint,redirect,request,session,flash
from .service import get_action_Result,login_required,group_exists
from .db import get_db

def create_task(GroupID,Name,DueDateTime,Description="",assignees_list={}):
    db = get_db()
    cursor = db.execute("INSERT INTO Tasks (GroupID,Name,DueDateTime,Description) VALUES (?,?,?,?)",[GroupID,Name,DueDateTime,Description])
    task_id = cursor.lastrowid
    cursor = db.cursor()
    for user_name in assignees_list:
        cursor.execute("INSERT INTO Assignees (TaskID,UserID,TaskStatus) VALUES (?,?,?)",[task_id,assignees_list[user_name],"Pending"])
    db.commit()
def update_task(task_id,data,assignees_list = {}):
    db = get_db()
    cursor = db.cursor()
    for key in data:
        if data[key] and key in ["Name","DueDateTime","Description"]:
            cursor.execute("UPDATE Tasks SET "+key+"=? WHERE TaskID = ?",[data[key],task_id])
    old_assignees_fetch = cursor.execute("SELECT Users.Username,Users.UserID,Assignees.TaskStatus FROM Assignees INNER JOIN Users ON Users.UserID = Assignees.UserID  WHERE TaskID = ?",[task_id]).fetchall()

    for old_assignee_data in old_assignees_fetch:
        if not (old_assignee_data[0] in assignees_list):
            cursor.execute("DELETE FROM Assignees WHERE TaskID = ? AND UserID = ?",[task_id,old_assignee_data[1]])
        else:
            assignees_list.pop(old_assignee_data[0])
    
    for user_name in assignees_list:
        cursor.execute("INSERT INTO Assignees (TaskID,UserID,TaskStatus) VALUES (?,?,?)",[task_id,assignees_list[user_name],"Pending"])
    db.commit()
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Assignees WHERE TaskID = ?",[task_id])
    cursor.execute("DELETE FROM Tasks WHERE TaskID = ?",[task_id])
    db.commit()
def update_task_status(task_id,user_id,status):
    db = get_db()
    db.cursor().execute("UPDATE Assignees SET TaskStatus=? WHERE TaskID = ? AND UserID = ?",[status,task_id,user_id])
    db.commit()
bp = Blueprint("tasks",__name__)
@bp.route("/groups/<group_id>/tasks",methods=["POST"])
@login_required
@group_exists
def create_task_view(group_id):
    """Creates task and adds it to the database""" 
    db = get_db()
    cursor = db.cursor() 
    user_id = session.get("UserID")
    #checking user rights
    user_role = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?;",[group_id,user_id]).fetchone()

    if not (user_role and user_role[0] in ["Admin","Owner"]) :
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    
    #retrieving message data
    form_data = {"Name":request.form.get("Name").strip(),"Description":request.form.get("Description"),
            "DueDate":request.form.get("DueDate"),"DueTime":request.form.get("DueTime"),"Assignees":request.form.getlist("Assignees"),"timezone":request.form.get("timezone")}

    #Filtering all task details
    format_error = "Doesn't match format"
    issues = {}

    #checking Assignees are in group:
    assignees_list = {}
    
    for username in form_data["Assignees"]:
        member_data = cursor.execute("SELECT Members.UserID FROM Members INNER JOIN Users ON Users.UserID = Members.UserID WHERE Username = ?",[username]).fetchone()
        if not member_data:
            issues["assigneeserror"] = "Invalid assignees list"
            assignees_list[username] = ""
        else:
            assignees_list[username] = member_data[0] 
    form_data["Assignees"] = assignees_list

    #checking Name
    if not re.match(r"^[a-zA-Z0-9\.\+\*°_\(\)\- ]{2,30}$",form_data["Name"]):
        issues["nameerror"] = format_error
    
    #checking Description
    if not re.match("^.{0,200}$",form_data["Description"]):
        issues["descriptionerror"] = format_error
    
    current_date_time = datetime.now(dt.timezone.utc)
    tz = ZoneInfo(form_data["timezone"])

    #calculating UTC starttime
    form_date_time = datetime.fromisoformat(f'{form_data["DueDate"]}T{form_data["DueTime"]}')
   
    #specifying timezone offset
    form_date_time = form_date_time.replace(tzinfo=tz)

    #converting to Utc
    UTCform_date_time = form_date_time.astimezone(dt.timezone.utc)
    
    #checking date:
    if current_date_time.date() > UTCform_date_time.date():
        issues["duedateerror"] = "Invalid due date"
    #checking time
    if current_date_time > UTCform_date_time:
        issues["duetimeerror"] = "Invalid due time"
    
    #checking task time slot doesn't overlap another
    fetch_result = cursor.execute("SELECT TaskID FROM Tasks WHERE DueDateTime = ?",
                             [UTCform_date_time.isoformat(timespec="minutes")]).fetchone()
    if fetch_result:
        issues["duedateerror"],issues["duetimeerror"] = "Time slot already taken",""

    if len(issues) > 0:
        ActionResult = get_action_Result()
        ActionResult["CreateTask"] = {"createtask":form_data,"issues":{"createtask":issues}}
        flash("Task creation failed","error")
        return redirect("/groups/"+group_id)
    
    #Provided fields are Correct
    create_task(group_id,form_data["Name"],UTCform_date_time.isoformat(timespec="minutes"),form_data["Description"],assignees_list)

    flash("Task successfully created","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/tasks/<task_id>",methods=["POST"])
@login_required
@group_exists
def edit_task(group_id,task_id):
    """Edits task and updates the database"""  
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()
    #checking user rights
    user_role = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?;",[group_id,user_id]).fetchone()

    if not (user_role and user_role[0] in ["Admin","Owner"]) :
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    #retrieving old data & checking task exists
    old_data = cursor.execute("SELECT Name,Description,DueDateTime FROM Tasks WHERE TaskID = ?",[task_id]).fetchone()
    if not old_data:
        flash("Task doesn't exist","error")
        return redirect("/groups/"+group_id)
    
    #retrieving message data
    form_data = {"url":"/groups/"+group_id+"/tasks/"+task_id,"Name":request.form.get("Name").strip(),
            "Description":request.form.get("Description"),"DueTime":request.form.get("DueTime"),
            "DueDate":request.form.get("DueDate"),"timezone":request.form.get("timezone"),"Assignees":request.form.getlist("Assignees")}
    received_data_copy = copy.deepcopy(form_data)

    #Filtering all task details
    format_error = "Doesn't match format"
    issues = {}

    #checking Assignees are in group:
    assignees_list = {}
    
    for username in form_data["Assignees"]:
        member_data = cursor.execute("SELECT Members.UserID FROM Members INNER JOIN Users ON Users.UserID = Members.UserID WHERE Username = ?",[username]).fetchone()
        if not member_data:
            issues["assigneeserror"] = "Invalid assignees list"
            assignees_list[username] = ""
        else:
            assignees_list[username] = member_data[0] 

    #checking Name
    if not re.match(r"^[a-zA-Z0-9\.\+\*°_\(\)\- ]{2,30}$",form_data["Name"]):
        issues["nameerror"] = format_error
    elif form_data["Name"] == old_data[0] :
        form_data.pop("Name")

    #checking Description
    if not re.match("^.{0,200}$",form_data["Description"]):
        issues["descriptionerror"] = format_error
    elif form_data["Description"] == old_data[1] :
        form_data.pop("Description")

    current_date_time = datetime.now(dt.timezone.utc)
    tz = ZoneInfo(form_data["timezone"])

    #creating datetime object
    form_date_time = datetime.fromisoformat(f'{form_data["DueDate"]}T{form_data["DueTime"]}')
    
    #specifying timezone 
    form_date_time = form_date_time.replace(tzinfo=tz)
    
    #converting to Utc
    UTCform_date_time = form_date_time.astimezone(dt.timezone.utc)

    #checking date:
    if current_date_time.date() > UTCform_date_time.date():
        issues["duedateerror"] = "Invalid due date"
    #checking time
    if current_date_time > UTCform_date_time:
        issues["duetimeerror"] = "Invalid due time"
    #checking task doesn't overlap another
    fetch_result = cursor.execute("SELECT TaskID FROM Tasks WHERE DueDateTime = ?",
                             [UTCform_date_time.isoformat(timespec="minutes")]).fetchone()
    if fetch_result and (fetch_result[0] != int(task_id) ):
        issues["duedateerror"],issues["duetimeerror"] = "Time slot already taken",""

    if len(issues) > 0:
        
        ActionResult = get_action_Result()
        ActionResult["EditTask"] = {"edittask":received_data_copy,"issues":{"edittask":issues}}
        flash("Task edition failed","error")
        return redirect("/groups/"+group_id)
    #checking if values are different
    oldDateTime = old_data[2]
    if oldDateTime == UTCform_date_time.isoformat(timespec="minutes"):
        form_data.pop("DueTime")
        form_data.pop("DueDate")

    #Provided fields are Correct
    # Fixing date format
    if form_data.get("DueTime"): 
        form_data["DueDateTime"]= UTCform_date_time.isoformat(timespec="minutes")
        form_data.pop("DueDate")
        form_data.pop("DueTime")   
    
    update_task(task_id,form_data,assignees_list)

    flash("Task successfully edited","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/tasks/<task_id>/delete",methods=["POST"])
@login_required
@group_exists
def delete_task_view(group_id,task_id):
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()
    #checking user rights
    user_role = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?;",[group_id,user_id]).fetchone()

    if not (user_role and user_role[0] in ["Admin","Owner"]) :
        flash("Unauthorized","error")
        return redirect("/groups/"+group_id)
    #checking task exists
    old_data = cursor.execute("SELECT Name FROM Tasks WHERE TaskID = ?",[task_id]).fetchone()
    if not old_data:
        flash("Task doesn't exist","error")
        return redirect("/groups/"+group_id)
    #Can now delete task
    delete_task(task_id)
    flash("Task successfully deleted","success")
    return redirect("/groups/"+group_id)

@bp.route("/groups/<group_id>/tasks/<task_id>/status",methods=["POST"])
@login_required
@group_exists
def change_task_status(group_id,task_id):
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()

    #checking task exists
    task_data = cursor.execute("SELECT Name FROM Tasks WHERE TaskID = ?",[task_id]).fetchone()
    if not task_data:
        flash("Task doesn't exist","error")
        return redirect("/groups/"+group_id)
    
    #checking user rights
    assignee_data = cursor.execute("SELECT TaskStatus FROM Assignees WHERE TaskID=? AND UserID = ?;",[task_id,user_id]).fetchone()

    if not assignee_data :
        flash("Not assigned to task","error")
        return redirect("/groups/"+group_id)
    form_status = request.form.get("status")

    if assignee_data[0] != form_status and form_status in ["Pending","Completed","InProgress"]:
        update_task_status(task_id,user_id,form_status)
        flash("Task completion status updated","success")
        return redirect("/groups/"+group_id)
    
    #status is invalid
    flash("Invalid task status","error")
    return redirect("/groups/"+group_id)

    

