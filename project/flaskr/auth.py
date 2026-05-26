import hashlib,re,click
import datetime as dt

from flask import Blueprint,request,session,render_template,redirect,flash
from datetime import datetime
from .db import get_db 
from .user import create_user
from .service import get_action_Result

bp = Blueprint('auth', __name__, url_prefix='/auth')
            
@bp.route("/",methods=["GET"])
def auth():
    """render authentication page"""
    # handling error messages
    action_result = get_action_Result()
    if action_result.get("Signup"):
        issues = action_result["Signup"]["issues"]
        action_result.pop("Signup")
        return render_template("authpage.html",issues = issues)
    elif action_result.get("Login"):
        loginiderror=action_result["Login"].get("loginiderror") or ""
        loginpassworderror=action_result["Login"].get("loginpassworderror") or ""
        loginusername=action_result["Login"].get("loginusername") or ""
        action_result.pop("Login")

        return render_template("authpage.html",loginiderror=loginiderror,loginusername=loginusername,loginpassworderror=loginpassworderror)
    return render_template("authpage.html")

@bp.route("/logout",methods=["POST"])
def logout():
    """log out user"""
    session.clear()
    return redirect("/home")

@bp.route("/login",methods=["POST"])
def login():    
    """create user login session"""
    #retrieving message data
    id, password = request.form.get("ID").strip(),request.form.get("password")

    #setting up database access
    db = get_db()
    cursor = db.cursor()

    #checking if user exists in database
    user_data_result = cursor.execute("SELECT UserID,PasswordHash FROM Users WHERE Email = ? OR Username = ? ",[id,id]).fetchone()
    
    if not user_data_result:
        #incorrect username/email
        action_result = get_action_Result()
        action_result["Login"] = {"loginusername":id,"loginiderror": "Incorrect username/email"}
        flash("Login failed, invalid username","error")
        return redirect("/auth")
        
    #checking user password
    PasswordCheckresult = user_data_result[1]
    HashedLoginPassword = hashlib.sha256(password.encode()).hexdigest()
    if PasswordCheckresult == HashedLoginPassword:
        session["UserID"] = user_data_result[0]
        session["timestamp"] = datetime.now(dt.timezone.utc) 
        flash("Login successful","success")
        return redirect("/home")
    
    #wrong password was sent
    action_result = get_action_Result()
    action_result["Login"] = {"loginusername":id,"loginpassworderror": "Incorrect password"}
    flash("Login failed, invalid password","error")
    return redirect("/auth")

@bp.route("/signup",methods=["POST"])
def signup():  
    """create new user account"""  
    #retrieving message data
    userData = {"username":request.form["username"].strip(),"email":request.form["email"],"password":request.form["password"],"formation":request.form["formation"],"institution":request.form["institution"]}
    
    #Filtering all user profile fields
    unavailableerror = "Already taken"
    formaterror = "Doesn't match format"
    issues = {}
    #checking username
    if not re.match("^[a-zA-Z0-9._]{6,20}$",userData["username"]):
        issues["signupusernameerror"] = formaterror
    #checking email 
    if not re.match(r"^[a-zA-Z0-9._%+-]{1,}+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",userData["email"]):
        issues["signupemailerror"] = formaterror
    #checking password 
    if not re.match("^(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,64}$",userData["password"]):
        issues["signuppassworderror"] = formaterror
    #checking formation
    if not re.match("^.{0,40}$",userData["formation"]):
        issues["signupformationerror"] = formaterror
    #checking institution
    if not re.match("^.{0,40}$",userData["institution"]):
        issues["signupinstitutionerror"] = formaterror
    
    #setting up database access
    db = get_db()
    cursor = db.cursor()
    
    #checking if username & email exists in database
    user_name_result = cursor.execute("SELECT UserID FROM Users WHERE Username = ?",[userData["username"]]).fetchone()
    email_result = cursor.execute("SELECT UserID FROM Users WHERE Email = ?",[userData["email"]]).fetchone()
    
    if user_name_result:
        #incorrect username
        issues["signupusernameerror"] = unavailableerror

    if email_result:
        #incorrect email
        issues["signupemailerror"] = unavailableerror

    if len(issues) > 0:
        action_result = get_action_Result()
        action_result["Signup"] = {"issues":issues}
        flash("Signup failed","error")
        return redirect("/auth")
    # profile fields are valid
    
    create_user(userData["username"],userData["email"],userData["password"],userData["formation"],userData["institution"],"blue")
    #User successfully created
    flash("User successfully created","success")
    return redirect("/auth")

@bp.cli.command("create")
@click.argument("username")
@click.argument("email")
@click.argument("password")
@click.argument("formation")
@click.argument("institution")
@click.argument("stylecolor")

def create(username,email,password,formation="",institution="",stylecolor="blue"):
    create_user(username,email,password,formation,institution,stylecolor)