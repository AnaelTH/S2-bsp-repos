import hashlib,re
from flask import Blueprint,redirect,request,session,flash
from .db import get_db
from .service import get_action_Result
from .service import login_required

def create_user(Username,Email,Password,Formation="",Institution="",StyleColor="blue"):
    """Adds a new User to the database"""
    db = get_db()
    data = [Username,Email,hashlib.sha256(Password.encode()).hexdigest(),Formation,Institution,StyleColor]
    db.cursor().execute("INSERT INTO Users (Username,Email,PasswordHash,Formation,Institution,StyleColor) VALUES (?,?,?,?,?,?)",data)
    db.commit()

def update_user(UserID,user):
    """Updates user profile fields for every key in a specified user profile dict"""
    db = get_db()
    cursor = db.cursor()
    for key in user:
        if user[key] and key in ["Username","Formation","Institution","Email","PasswordHash","StyleColor"]:
            cursor.execute("UPDATE Users SET "+key+"=? WHERE UserID = ?",[user[key],UserID])
    db.commit()

def delete_user(ID):
    """Removes a user from the database using its email/username/UserID"""
    db = get_db()
    db.cursor().execute("DELETE FROM Users WHERE UserID=? OR Email=? OR Username=?;",[ID,ID,ID])
    db.commit()

def get_groups_data(UserID):
    """return user's joined group data: Name,StyleColor"""
    db = get_db()
    cursor = db.cursor()
    group_id_list = cursor.execute("SELECT GroupID FROM Members WHERE UserID = ?",[UserID]).fetchall()
    group_data = {}

    for group_id in group_id_list:
        name,style_color = cursor.execute("SELECT Name,StyleColor FROM Groups WHERE GroupID = ?",[group_id[0]]).fetchone()
        if name:
            #shaping group id into a 10 digits string
            base_id = str(group_id[0])
            group_data[base_id] =  (name,style_color)

    return group_data

bp = Blueprint("users",__name__,url_prefix="/users")

@bp.route("/",methods=["POST"])
@login_required
def editprofile():
    """edits and updates user profile details"""  
    user_id = session["UserID"]
    #retrieving old data
    db = get_db()
    cursor = db.cursor()
    old_user_data = {}
    old_user_data["Username"],old_user_data["Email"],old_user_data["PasswordHash"],old_user_data["Formation"],old_user_data["Institution"],old_user_data["StyleColor"] = cursor.execute("SELECT Username,Email,PasswordHash,Formation,Institution,StyleColor FROM Users WHERE UserID = ?",[user_id]).fetchone()

    user_data = {
        "Username":request.form.get("username").strip(),"Email":request.form.get("email"),"Formation":request.form.get("formation"),
        "Institution":request.form.get("institution"),"StyleColor":request.form.get("stylecolor"),
        "PasswordHash": request.form.get("new-password")
        }
    user_data_copy = user_data.copy()

    #retrieving message data
    old_form_password = request.form.get("old-password")

    #Filtering all user profile fields
    issues = {}

    #checking username
    if not re.match("^[a-zA-Z0-9._]{6,20}$",user_data["Username"]):
        issues["usernameerror"] = "Doesn't match format"
    elif user_data["Username"] == old_user_data["Username"]:
        user_data.pop("Username")

    #checking email  
    if not re.match(r"^[a-zA-Z0-9._%+-]{1,}+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",user_data["Email"]):
        issues["emailerror"] = "Doesn't match format"
    elif user_data["Email"] == old_user_data["Email"]:
        user_data.pop("Email")
    
    #checking passwords
    if user_data["PasswordHash"] == "":
        #new password is empty, thus no changes required
        user_data.pop("PasswordHash")
    elif old_form_password == "":
        #old password is empty, thus no changes required
        issues["oldpassworderror"] = "Required"
    elif old_user_data["PasswordHash"] != hashlib.sha256(old_form_password.encode()).hexdigest():
        #incorrect old password
        issues["oldpassworderror"] = "Incorrect"
    elif not re.match("^(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,64}$", user_data["PasswordHash"]):
        issues["newpassworderror"] = "Doesn't match format"
    elif user_data["PasswordHash"] == old_form_password:
        issues["newpassworderror"] = "Not new"

    #checking formation
    if not re.match("^.{0,40}$",user_data["Formation"]):
        issues["formationerror"] = "Doesn't match format"
    elif user_data["Formation"] == old_user_data["Formation"]:
        user_data.pop("Formation")
    
    #checking institution
    if not re.match("^.{0,40}$",user_data["Institution"]):
        issues["institutionerror"] = "Doesn't match format"
    elif user_data["Institution"] == old_user_data["Institution"]:
        user_data.pop("Institution")
    
    #checking style color
    if user_data["StyleColor"] == old_user_data["StyleColor"]:
        user_data.pop("StyleColor")
        
    #fixing password format
    if "PasswordHash" in user_data :
        new_password = user_data["PasswordHash"]
        user_data["PasswordHash"] = hashlib.sha256(new_password.encode()).hexdigest()

    if len(issues) > 0:
        issues_dict = {"edit":issues}
        action_result = get_action_Result()
        action_result["EditProfile"] = {"user":user_data_copy,"issues":issues_dict}
        flash("Profile edition failed","error")
        return redirect("/home")

    #Provided fields are Correct
    update_user(user_id,user_data)

    #cleaning up user profile dict
    #No need to send user's passwordhash
    user_data.pop("PasswordHash",None)
    #No need to send empty user profile fields
    for key in old_user_data:
        try:
            if user_data[key] == None:
                user_data[key] = old_user_data[key]
        except KeyError:
            user_data[key] = old_user_data[key]

    action_result = get_action_Result()
    action_result["EditProfile"] = {"user":user_data}
    flash("Profile successfully edited","success")
    return redirect("/home")

@bp.route("/groupsdata",methods = ["GET"])
@login_required
def getGroups():
    """fetch user's joined groups data"""
    group_data = get_groups_data(session["UserID"])
    data = {"GroupData": group_data}
    return data

