from .db import get_db
from .service import get_action_Result,login_required
from flask import Blueprint,render_template,session,redirect

def fetch_user_group_data(user_id,limit=10):
    """Returns users' joined groups data : due tasks,upcoming sessions and joined groups"""
    db = get_db() 
    cursor = db.cursor()
    group_data = {"UpcomingSessions":[],"JoinedGroups":[],"DueTasks":[]}
    
    #fetching joined groups data
    joined_groups_fetch = None
    if limit != None:   
        joined_groups_fetch = cursor.execute("SELECT Groups.GroupID,Name,StyleColor FROM Groups INNER JOIN Members ON Members.GroupID = Groups.GroupID WHERE Members.UserID = ? ORDER BY CreationDate ASC LIMIT ?",[user_id,limit]).fetchall()
    else:
        joined_groups_fetch = cursor.execute("SELECT Groups.GroupID,Name,StyleColor FROM Groups INNER JOIN Members ON Members.GroupID = Groups.GroupID WHERE Members.UserID = ? ORDER BY CreationDate ASC",[user_id]).fetchall()
    for joined_group_data in joined_groups_fetch:
        group_data["JoinedGroups"].append({"Name":joined_group_data[1],"GroupID":joined_group_data[0],"StyleColor":joined_group_data[2]})
    
    #fetching Upcoming Sessions:
    upcoming_sessions_fetch = None
    if limit != None:
        upcoming_sessions_fetch = cursor.execute("SELECT Sessions.SessionID,Name,Date,StartTime,EndTime,Location,GroupID FROM Sessions INNER JOIN Attendees ON Attendees.SessionID = Sessions.SessionID WHERE Attendees.UserID = ? AND (Date > CURRENT_DATE OR (Date > CURRENT_DATE AND EndTime > CURRENT_TIME)) ORDER BY Date ASC,StartTime ASC,EndTime ASC LIMIT ?",[user_id,limit]).fetchall()
    else:
        upcoming_sessions_fetch = cursor.execute("SELECT Sessions.SessionID,Name,Date,StartTime,EndTime,Location,GroupID FROM Sessions INNER JOIN Attendees ON Attendees.SessionID = Sessions.SessionID WHERE Attendees.UserID = ? AND (Date > CURRENT_DATE OR (Date > CURRENT_DATE AND EndTime > CURRENT_TIME)) ORDER BY Date ASC,StartTime ASC,EndTime ASC",[user_id]).fetchall()
    
    for session_data in upcoming_sessions_fetch:
        group_data["UpcomingSessions"].append({"SessionID":session_data[0],"Name":session_data[1],"Date":session_data[2].isoformat(),"StartTime":session_data[3],"EndTime":session_data[4],"Location":session_data[5],"GroupID":session_data[6]})
    
    #fetching  Due tasks:
    due_tasks_fetch = None
    if limit != None:
        due_tasks_fetch = cursor.execute("SELECT Tasks.TaskID,Name,DueDateTime,Tasks.GroupID FROM Tasks INNER JOIN Assignees ON Assignees.TaskID = Tasks.TaskID WHERE Assignees.UserID = ? AND DueDateTime > CURRENT_TIMESTAMP ORDER BY DueDateTime ASC LIMIT ?",[user_id,limit]).fetchall()
    else:
        due_tasks_fetch = cursor.execute("SELECT Tasks.TaskID,Name,DueDateTime,Tasks.GroupID FROM Tasks INNER JOIN Assignees ON Assignees.TaskID = Tasks.TaskID WHERE Assignees.UserID = ? AND DueDateTime > CURRENT_TIMESTAMP ORDER BY DueDateTime ASC",[user_id]).fetchall()
    for task_data in due_tasks_fetch:
        group_data["DueTasks"].append({"TaskID":task_data[0],"Name":task_data[1],"DueDateTime":task_data[2],"GroupID":task_data[3]})

    return group_data

def fetch_user_overview_data(user_id):
    """Returns users' joined groups data : due tasks,upcoming sessions and joined groups"""
    db = get_db() 
    cursor = db.cursor()
    group_data = {"UpcomingSessions":[],"JoinedGroups":[],"DueTasks":[]}
    
    #fetching joined groups data
    joined_groups_fetch = cursor.execute("SELECT Groups.GroupID,Name,StyleColor,Description,Subject,CreationDate,StudyLevel,IsPrivate FROM Groups INNER JOIN Members ON Members.GroupID = Groups.GroupID WHERE Members.UserID = ? ORDER BY CreationDate ASC",[user_id]).fetchall()
    for joined_group_data in joined_groups_fetch:
        count = cursor.execute("SELECT COUNT(UserID) FROM Members WHERE GroupID = ?",[joined_group_data[0]]).fetchone()[0]
        group_data["JoinedGroups"].append({"Name":joined_group_data[1],"GroupID":joined_group_data[0],"StyleColor":joined_group_data[2],"Description":joined_group_data[3],"Subject":joined_group_data[4],"CreationDate":joined_group_data[5],"MemberCount":count,"StudyLevel":joined_group_data[6],"IsPrivate":joined_group_data[7]})
    
    #fetching Upcoming Sessions:
    upcoming_sessions_fetch = cursor.execute("SELECT Sessions.SessionID,Name,Date,StartTime,EndTime,Location,Sessions.GroupID FROM Sessions INNER JOIN Attendees ON Attendees.SessionID = Sessions.SessionID WHERE Attendees.UserID = ? AND (Date > CURRENT_DATE OR (Date > CURRENT_DATE AND EndTime > CURRENT_TIME)) ORDER BY Date ASC,StartTime ASC,EndTime ASC",[user_id]).fetchall()
    for session_data in upcoming_sessions_fetch:
        count = cursor.execute("SELECT COUNT(UserID) FROM Attendees WHERE SessionID = ?",[session_data[0]]).fetchone()[0]
        group_data["UpcomingSessions"].append({"SessionID":session_data[0],"Name":session_data[1],"Date":session_data[2].isoformat(),"StartTime":session_data[3],"EndTime":session_data[4],"Location":session_data[5],"GroupID":session_data[6],"AttendeeCount":count})
    
    #fetching  Due tasks:
    due_tasks_fetch = cursor.execute("SELECT Tasks.TaskID,Name,DueDateTime,Tasks.GroupID FROM Tasks INNER JOIN Assignees ON Assignees.TaskID = Tasks.TaskID WHERE Assignees.UserID = ? AND DueDateTime > CURRENT_TIMESTAMP ORDER BY DueDateTime ASC",[user_id]).fetchall()
    keys = ["TaskID","Name","DueDateTime","Description"]
    for task_data in due_tasks_fetch:
        #fetching task assignees data
        group_members_count = db.execute("SELECT COUNT(UserID) FROM Members WHERE GroupID = ?",[task_data[3]]).fetchone()[0]
        assignees_string = "None"

        assignees = db.execute("SELECT Users.Username,Assignees.TaskStatus FROM Users INNER JOIN Assignees ON Users.UserID = Assignees.UserID WHERE Assignees.TaskID = ?",[task_data[0]]).fetchall()
        # building assignees list string
        assignees_count = db.execute("SELECT COUNT(UserID) FROM Assignees WHERE TaskID = ?",[task_data[0]]).fetchone()
        if assignees_count and assignees_count[0]:
            
            assignees_string = ""
            assignees_count = assignees_count[0]

            if assignees_count != group_members_count:
                for assignee_data in assignees:
                    assignees_string = assignees_string +", "+assignee_data[0]
            else:
                assignees_string = "Everyone"
            assignees_string = assignees_string.strip(", ")
        user_task_status = "None"
        #fetching current user task status
        assignee_data = db.execute("SELECT TaskStatus FROM Assignees WHERE UserID = ? AND TaskID = ?",[user_id,task_data[0]]).fetchone()
        if assignee_data:
            user_task_status = assignee_data[0]

        group_data["DueTasks"].append({"TaskID":task_data[0],"Name":task_data[1],"DueDateTime":task_data[2],"GroupID":task_data[3],"AssigneesString":assignees_string,"TaskStatus":user_task_status})

    return group_data


bp = Blueprint("home",__name__,url_prefix="/home")

@bp.route("/",methods=["GET"])
@login_required
def home():
    """renders home page & notifications about previous operations: e.g. edit group, edit session...etc."""
    user_id = session.get("UserID")
    
    #user is logged in.
    db = get_db()
    cursor = db.cursor()
    #fetching user data
    query = "SELECT Username,Email,Formation,Institution,StyleColor FROM Users WHERE UserID = ?"
    user_fetch = cursor.execute(query,[user_id]).fetchone()
    user_data={"Username":user_fetch[0],"Email":user_fetch[1],"Formation":user_fetch[2],"Institution":user_fetch[3],"StyleColor":user_fetch[4]}
    #fetching group data
    group_data = fetch_user_group_data(user_id,10)
    
    #handling previous operation issues
    action_result = get_action_Result()
    if action_result.get("CreateGroup"):
        issues = action_result["CreateGroup"]["issues"]
        creategroup_data  = action_result["CreateGroup"]["data"]
        action_result.pop("CreateGroup")
        
        return render_template("homepage.html",group_data=group_data,user=user_data,creategroup=creategroup_data,issues=issues )
    elif action_result.get("EditProfile"):
        issues = action_result["EditProfile"].get("issues") or {}
        user_data  = action_result["EditProfile"].get("user") or {}
        action_result.pop("EditProfile")
        return render_template("homepage.html",group_data=group_data,user=user_data,issues = issues)
    return render_template("homepage.html",group_data=group_data,user=user_data)
    

@bp.route("/overview",methods=["GET"])
@login_required

def load_stats_overview():
    """renders overview page"""
    user_id = session.get("UserID")
    
    #fetching group data
    group_data = fetch_user_overview_data(user_id)
    
    return render_template("overview.html",group_data=group_data)