from flask import Blueprint,request
from .db import get_db

def fetch_group_data(query,privacy,level):
    """return group search results """
    data = []
    privacy_filter = ""
    if privacy:
        if privacy == "private":
            privacy_filter = " AND IsPrivate = 1 "
        else:
            privacy_filter = " AND IsPrivate = 0 "
    
    level_filter = ""
    if level:
        level_filter = "AND StudyLevel = '"+level +"' "

    fetch_query = "SELECT GroupID,Name,Subject,Description,StyleColor,IsPrivate,StudyLevel " \
    "FROM Groups " \
    "WHERE (LOWER(Name) LIKE '%'||LOWER(?)||'%' OR LOWER(Subject) LIKE '%'||LOWER(?)||'%' OR LOWER(Description) LIKE '%'||LOWER(?)||'%' )" + level_filter + privacy_filter+ \
    " ORDER BY CreationDate ASC"
    
    db = get_db()
    cursor = db.cursor()
    fetch_result = cursor.execute(fetch_query,[query,query,query]).fetchall()
    for group_data in fetch_result:
        group_dict = {"GroupID":group_data[0],"Name":group_data[1],"Subject":group_data[2],"Description":group_data[3],
                      "StyleColor":group_data[4],"IsPrivate":group_data[5],"StudyLevel":group_data[6]}
        
        #adding group member count
        group_dict["MemberCount"] = cursor.execute("SELECT COUNT(UserID) FROM Members WHERE GroupID = ?",[group_dict["GroupID"]]).fetchone()[0]

        data.append(group_dict)
    return data

bp = Blueprint("search",__name__)

@bp.route("/search",methods=["GET"])
def group_search():
    """Search & return group search data"""
    query = request.args.get("query")
    privacy = request.args.get("privacy")
    level = request.args.get("level")
    
    #checking privacy field
    if not (privacy in ["public","private"]):
        privacy = None
    #checking study level field
    if not (level in ["High Shool","Bachelor","Master"]):
        level = None

    return fetch_group_data(query,privacy,level)