import copy,re
from .db import get_db
from .service import get_action_Result,login_required,group_exists,user_is_owner
from .members import create_member
from flask import Blueprint,redirect,render_template,request,session,flash

def fetch_request_data(group_id):
    db = get_db()
    cursor = db.cursor()
    group_requests = cursor.execute("SELECT Users.UserID,Users.Username,Users.Email,Users.StyleColor FROM Users INNER JOIN Requests ON Requests.UserID = Users.UserID WHERE Requests.GroupID = ?",[group_id]).fetchall()
    data = {}
    for request_data in group_requests:
        data[request_data[0]] = {"Username":request_data[1],"Email":request_data[2],"StyleColor":request_data[3]}
    return data

def fetch_task_data(group_id):
    db = get_db()
    cursor = db.cursor()
    group_members_count = cursor.execute("SELECT COUNT(UserID) FROM Members WHERE GroupID = ?",[group_id]).fetchone()[0]
    group_tasks = cursor.execute("SELECT TaskID,Name,DueDateTime,Description FROM Tasks WHERE GroupID = ? ORDER BY DueDateTime ASC",[group_id]).fetchall()
    data = []
    keys = ["TaskID","Name","DueDateTime","Description"]
    for task_data in group_tasks:
        taskdict = {}
        for i in range(0,4):
            taskdict[keys[i]] = task_data[i]
        #building assignees dict
        assignees_dict = {}
        assignees = cursor.execute("SELECT Users.Username,Assignees.TaskStatus FROM Users INNER JOIN Assignees ON Users.UserID = Assignees.UserID WHERE Assignees.TaskID = ?",[task_data[0]]).fetchall()

        for assignee_data in assignees:
            assignees_dict[assignee_data[0]] = assignee_data[1]
        taskdict["AssigneesDict"] = assignees_dict

        # building assignees list string
        assignees_count = cursor.execute("SELECT COUNT(UserID) FROM Assignees WHERE TaskID = ?",[task_data[0]]).fetchone()
        if assignees_count and assignees_count[0]:
            
            assignees_string = ""
            assignees_count = assignees_count[0]

            if assignees_count != group_members_count:
                for assignee_data in assignees:
                    assignees_string = assignees_string +", "+assignee_data[0]
            else:
                assignees_string = "Everyone"
            assignees_string = assignees_string.strip(", ")
            taskdict["AssigneesString"] = assignees_string
        else:
            taskdict["AssigneesString"] = "None"
        #fetching current user task status
        user_id = session.get("UserID")
        if user_id:
            #check if user is an assignee
            assignee_data = cursor.execute("SELECT UserID,TaskStatus FROM Assignees WHERE UserID = ? AND TaskID = ?",[user_id,task_data[0]]).fetchone()
            if assignee_data:
                taskdict["UserTaskStatus"] = assignee_data[1]
        data.append(taskdict)
    return data

def fetch_member_data(group_id):
    #fetching member list
    members_fetch = get_db().execute("SELECT Users.Username,Users.UserID,Users.StyleColor,Users.Email,Members.Role FROM Users INNER JOIN Members ON Users.UserID = Members.UserID WHERE GroupID = ?",[group_id]).fetchall()
    members_data = {}

    if members_fetch:
        for member_data in members_fetch:
            #storing user id,stylecolor,email & role
            members_data[member_data[1]] = (member_data[0],member_data[2],member_data[3],member_data[4])
    return members_data

def fetch_session_data(group_id):
    db = get_db()
    cursor = db.cursor()
    #fetching session list
    session_list = []
    group_sessions = cursor.execute("SELECT SessionID,Name,Date,StartTime,EndTime,Location,Description FROM Sessions WHERE GroupID = ? ORDER BY Date ASC,StartTime ASC,EndTime ASC",[group_id]).fetchall()
    keys = ["SessionID","Name","Date","StartTime","EndTime","Location","Description"]
    for session_data in group_sessions:
        session_dict = {}
        for i in range(0,7):
            session_dict[keys[i]] = session_data[i]
        #fixing data format:
        session_dict["Date"] = session_dict["Date"].isoformat()

        #fetching attendees count
        attendees = cursor.execute("SELECT COUNT(UserID) FROM Attendees WHERE SessionID = ?",[session_data[0]]).fetchone()
        if attendees:
            session_dict["Attendees"] = attendees[0]
        #getting user attendancy status:
        session_dict["IsUserAttending"] = False
        user_id = session.get("UserID")
        if user_id:
            attendant_data = cursor.execute("SELECT UserID FROM Attendees WHERE SessionID = ? AND UserID = ?",[session_data[0],user_id]).fetchone()
            if attendant_data:
                session_dict["IsUserAttending"] = True
        session_list.append(session_dict)
    return session_list

def fetch_group_data(group_id):
    db = get_db()
    cursor = db.cursor()
    #fetching group info
    base_group_data = cursor.execute("SELECT Name,Subject,Description,IsPrivate,CreationDate,StyleColor,StudyLevel FROM Groups WHERE GroupID =?;",[group_id]).fetchone()
    #fetching  user role & name
    user_role = "NonMember"
    user_name = ""
    user_id = session.get("UserID")
    if user_id:
        member_data = cursor.execute("SELECT Role FROM Members WHERE GroupID =? AND UserID = ?",[group_id,user_id]).fetchone()
        if member_data:
            user_role = member_data[0]
        user_name_data = cursor.execute("SELECT Username FROM Users WHERE UserID=?",[user_id]).fetchone()
        if user_name_data:
            user_name = user_name_data[0]
    
    group_data = {"Name":base_group_data[0],"Subject":base_group_data[1],"Description":base_group_data[2],"IsPrivate":base_group_data[3],
                "CreationDate":base_group_data[4],"StyleColor":base_group_data[5],"StudyLevel":base_group_data[6],"GroupID":group_id,"UserRole":user_role,"Username":user_name,
                "stats":{"Members":"--","Sessions":"--","Tasks":"--"},"Members":fetch_member_data(group_id),"Sessions":fetch_session_data(group_id),"Tasks":fetch_task_data(group_id),
                "Requests":fetch_request_data(group_id)
            }
    
    #computing group stats
    member_count = cursor.execute("SELECT COUNT(*) FROM Members WHERE GroupID = ?",[group_id]).fetchone()
    session_count = cursor.execute("SELECT COUNT(SessionID) FROM Sessions WHERE GroupID = ?",[group_id]).fetchone()
    task_count = cursor.execute("SELECT COUNT(TaskID) FROM Tasks WHERE GroupID = ?",[group_id]).fetchone()
    
    group_data["CreationDate"] = str(group_data["CreationDate"].day)+"/"+str(group_data["CreationDate"].month)+"/"+str(group_data["CreationDate"].year)
    
    if member_count:
        group_data["stats"]["Members"] = member_count[0]
    if session_count:
        group_data["stats"]["Sessions"] = session_count[0]
    if task_count:
        group_data["stats"]["Tasks"] = task_count[0]
        
    return group_data

def create_group(UserID,Name,Subject,Description,StyleColor,isPrivate=1,StudyLevel="High School"):
    """Adds a new Group to the database"""
    db = get_db()
    cursor = db.cursor()
    data = [UserID,Name,Subject,Description,isPrivate,StyleColor,StudyLevel]
    cursor.execute("INSERT INTO Groups (OwnerID,Name,Subject,Description,isPrivate,StyleColor,StudyLevel) VALUES (?,?,?,?,?,?,?)",data)
    db.commit()
    GroupID = cursor.execute("SELECT GroupID FROM Groups WHERE OwnerID = ?",[UserID]).fetchone()[0]
    create_member(UserID,GroupID,"Owner")

def update_group(GroupID,data):
    """Updates group profile fields for every key in a specified group profile dict"""
    db = get_db()
    cursor = db.cursor()
    for key in data:
        if key in ["Name","Subject","Description","IsPrivate","StyleColor","StudyLevel"]:
            cursor.execute("UPDATE Groups SET "+key+"=? WHERE GroupID = ?",[data[key],GroupID])
    db.commit()

def delete_group(group_id):
    """Removes a group from the database using its GroupID"""
    db = get_db()
    cursor = db.cursor()
    session_id_fetch = cursor.execute("SELECT SessionID FROM Sessions WHERE GroupID = ?",[group_id]).fetchall()
    task_id_fetch = cursor.execute("SELECT TaskID FROM Tasks WHERE GroupID = ?",[group_id]).fetchall()

    for task_id in task_id_fetch:
        cursor.execute("DELETE FROM Assignees WHERE TaskID=?;",[task_id[0]])
        cursor.execute("DELETE FROM Tasks WHERE TaskID = ?",[task_id[0]])
    for session_id in session_id_fetch:
        cursor.execute("DELETE FROM Attendees WHERE SessionID=?;",[session_id[0]])
        cursor.execute("DELETE FROM Sessions WHERE SessionID = ?",[session_id[0]])

    cursor.execute("DELETE FROM Requests WHERE GroupID = ?",[group_id])
    cursor.execute("DELETE FROM Members WHERE GroupID=?;",[group_id])
    cursor.execute("DELETE FROM Groups WHERE GroupID=?;",[group_id])
    db.commit()

bp = Blueprint("groups",__name__,url_prefix="/groups")

@bp.route("/",methods=["POST"])
@login_required
def create_group_view():
    """Create group and add it to the database, with user set as owner"""  
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()
    #retrieving message data
    form_data = {"Name":request.form.get("Name").strip(),"Subject":request.form.get("Subject"),"Description":request.form.get("Description"),"IsPrivate":request.form.get("IsPrivate"),"StyleColor":request.form.get("StyleColor"),"StudyLevel":request.form.get("StudyLevel")}
    
    #Filtering all group profile fields
    unavailable_error = "Already taken"
    format_error = "Doesn't match format"
    issues = {}
    #checking Name
    if not re.match(r"^[a-zA-Z0-9\.\+\*°_\(\)\- ]{6,30}$",form_data["Name"]):
        issues["nameerror"] = format_error
    elif db.execute("SELECT GroupID FROM Groups WHERE Name =?;",[form_data["Name"]]).fetchone() is not None:
        issues["nameerror"] = unavailable_error

    #checking subject  
    if not re.match("^.{0,30}$",form_data["Subject"]):
        issues["subjecterror"] = format_error

    #checking Description
    if not re.match("^.{0,200}$",form_data["Description"]):
        issues["descriptionerror"] = format_error

    #Checking Stylecolor:
    if not (form_data["StyleColor"] in ["blue","red","green","orange","yellow","pink","cyan","purple"] ):
        form_data["StyleColor"] = "blue"
    
    #checking study level
    if not (form_data["StudyLevel"] in ["High School","Bachelor","Master"]):
        form_data["StudyLevel"] = "High School"
    #Checking IsPrivate field format
    if int(form_data["IsPrivate"] )!= 0:
        form_data["IsPrivate"] = 1

    if len(issues) > 0:
        issues_dict = {"group":issues}
        action_result = get_action_Result()
        action_result["CreateGroup"] = {"data":form_data,"issues":issues_dict}
        flash("Group creation failed","error")
        return redirect("/home")

    #Provided fields are Correct
    create_group(user_id,form_data["Name"],form_data["Subject"],form_data["Description"],form_data["StyleColor"],form_data["IsPrivate"],form_data["StudyLevel"])
    flash("Group successfully created","success")
    return redirect("/home")

@bp.route("/<group_id>",methods=["POST"])
@login_required
@group_exists
@user_is_owner
def edit_group_view(group_id):
    """Update existing group data"""
    old_group_data = fetch_group_data(group_id)
    db = get_db()
    cursor = db.cursor()

    #retrieving data
    form_data = {"Name":request.form.get("Name"),"Subject":request.form.get("Subject"),"Description":request.form.get("Description"),
                "IsPrivate":request.form.get("IsPrivate"),"StyleColor":request.form.get("StyleColor"),"StudyLevel":request.form.get("StudyLevel")}
    
    #checking Data
    unavailable_error = "Already taken"
    format_error = "Doesn't match format"
    issues = {}

    group_data = db.execute("SELECT GroupID FROM Groups WHERE Name =?;",[form_data["Name"]]).fetchone()
    if not re.match(r"^[a-zA-Z0-9\.\+\*°_\(\)\- ]{6,30}$",form_data["Name"]):
        issues["nameerror"] = format_error
    elif group_data and str(group_data[0]) != group_id :
        issues["nameerror"] = unavailable_error

    #checking subject  
    if not re.match("^.{0,30}$",form_data["Subject"]):
        issues["subjecterror"] = format_error
    
    #checking Description
    if not re.match("^.{0,200}$",form_data["Description"]):
        issues["descriptionerror"] = format_error

    #Checking Stylecolor:
    if not (form_data["StyleColor"] in ["blue","red","green","orange","yellow","pink","cyan","purple"] ):
        form_data["StyleColor"] = "green"

    #checking study level
    if not (form_data["StudyLevel"] in ["High School","Bachelor","Master"]):
        form_data["StudyLevel"] = "High School"

    #Checking IsPrivate field format
    if int(form_data["IsPrivate"]) != 0:
        form_data["IsPrivate"] = 1

    if len(issues) > 0:
        #update old group data fields
        for key in form_data:
            if key in old_group_data:
                old_group_data[key] = form_data[key]
            
        issues_dict = {"group":issues}
        action_result = get_action_Result()
        action_result["EditGroup"] = {"data":old_group_data,"issues":issues_dict}
        flash("Group edition failed","error")
        return redirect("/groups/"+group_id)
    
    #checking values differ from original group data
    if old_group_data["Subject"] == form_data["Subject"]:
        form_data.pop("Subject")

    if old_group_data["Description"] == form_data["Description"]:
        form_data.pop("Description")

    if form_data["StyleColor"] == old_group_data["StyleColor"]:
        form_data.pop("StyleColor")
    if old_group_data["IsPrivate"] == form_data["IsPrivate"]:
        form_data.pop("IsPrivate")   
    if old_group_data["Name"] == form_data["Name"]:
        form_data.pop("Name")
    if old_group_data["StudyLevel"] == form_data["StudyLevel"]:
        form_data.pop("StudyLevel")
        
    #No issues 
    update_group(group_id,form_data)
    flash("Group successfully edited","success")
    return redirect("/groups/"+group_id)

@bp.route("/<group_id>",methods=["GET"])
@group_exists
def get_group_view(group_id):
    """Renders group webpage with data from previous operations performed: e.g. edit group,edit task...etc"""
    group_data = fetch_group_data(group_id)
    action_result = get_action_Result()
    
    if action_result.get("EditGroup"):
        group_data = action_result["EditGroup"]["data"]
        issues = action_result["EditGroup"]["issues"]
        action_result.pop("EditGroup")
        
        return render_template("grouppage.html",group = group_data,issues = issues)
    elif action_result.get("CreateSession"):
        createsession = action_result["CreateSession"]["createsession"]
        issues = action_result["CreateSession"]["issues"]

        action_result.pop("CreateSession")
        return render_template("grouppage.html",group = group_data,createsession = createsession,issues = issues)
    elif action_result.get("EditSession"):
        editsession = action_result["EditSession"]["editsession"]
        issues = action_result["EditSession"]["issues"]

        action_result.pop("EditSession")
        return render_template("grouppage.html",group = group_data,editsession = editsession,issues = issues)
    elif action_result.get("CreateTask"):
        createtask = action_result["CreateTask"]["createtask"]
        issues = action_result["CreateTask"]["issues"]

        action_result.pop("CreateTask")
        return render_template("grouppage.html",group = group_data,createtask = createtask,issues = issues)
    elif action_result.get("EditTask"):
        edittask = action_result["EditTask"]["edittask"]
        issues = action_result["EditTask"]["issues"]

        action_result.pop("EditTask")
        return render_template("grouppage.html",group = group_data,edittask = edittask,issues = issues)
    return render_template("grouppage.html",group = group_data)

@bp.route("/<group_id>/delete",methods=["POST"])
@login_required
@group_exists
@user_is_owner
def delete_group_view(group_id):
    """Delete group from database along with its members data"""
    # Deleting group
    delete_group(group_id)
    flash("Group successfully deleted","success")
    return redirect("/home")

@bp.route("/<group_id>/join",methods=["POST"])
@login_required
@group_exists
def join_group(group_id):
    """Adds user as member of a public group"""
    user_id = session.get("UserID")
    db = get_db()
    cursor = db.cursor()
    #checking if user is in group
    member_data = cursor.execute("SELECT UserID FROM Members WHERE GroupID = ? AND UserID = ?",[group_id,user_id]).fetchone()
    if member_data:
        flash("Already joined group","error")
        return redirect("/groups/"+group_id)
    #checking if group is private
    group_data = cursor.execute("SELECT IsPrivate FROM Groups WHERE GroupID =?;",[group_id]).fetchone()
    if group_data[0]:
        flash("Can't directly join, group is private","error")
        return redirect("/groups/"+group_id)
    #User can join
    create_member(user_id,group_id,"Member")
    flash("Group successfully joined","success")
    return redirect("/groups/"+group_id)