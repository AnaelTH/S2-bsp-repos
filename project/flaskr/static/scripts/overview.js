//tab selection system
const tabsContainer = document.getElementById("tablist");
let tabList = tabsContainer.children;

let selectedTabName = sessionStorage.getItem("overviewSelectedTab");
let selectedTab = document.getElementById("joinedgrouptab");

if (selectedTabName !== null) {
    selectedTab = document.getElementById(selectedTabName);
}

selectedTab.className = "clickedtab";
document.getElementById(selectedTab.id.slice(0,selectedTab.id.length - 3)+"tabcontent").hidden = false;

for (let index = 0; index < tabList.length; index ++){
    let tabElement = tabList[index]
    tabElement.onclick = function(ev){
        if ( ! selectedTab.isEqualNode(tabElement) ){
            selectedTab.className = "";

            tabElement.className = "clickedtab";
            const newtabType = tabElement.id.slice(0,tabElement.id.length - 3);
            const previousTabType = selectedTab.id.slice(0,selectedTab.id.length - 3);
            
            sessionStorage.setItem("overviewSelectedTab",tabElement.id);

            let previousTabContent = document.getElementById(previousTabType+"tabcontent");
            previousTabContent.hidden = true;
            let newTabContent = document.getElementById(newtabType+"tabcontent");
            newTabContent.hidden = false;

            selectedTab = tabElement;
        }
    }
}

//loading joined groups 

let groupElement = document.getElementById("groupref");

for (let index = 0; index < UserGroupData["JoinedGroups"].length; index++) {
    let groupData = UserGroupData["JoinedGroups"][index];
    let groupID = groupData["GroupID"]
    let newGroupElement = groupElement.cloneNode(true);
    let date = new Date(groupData["CreationDate"]);

    newGroupElement.id = "";
    newGroupElement.style.cssText = "";
    newGroupElement.getElementsByTagName("svg")[0].style.cssText = "fill:"+groupData["StyleColor"] ;

    newGroupElement.getElementsByClassName("groupmembers")[0].innerText = "Members: "+groupData["MemberCount"];
    newGroupElement.getElementsByClassName("creationdate")[0].innerText = "Since " + String(date.getDate()).padStart(2,"0")+"/"+(String(date.getMonth()+1)).padStart(2,"0")+"/"+String(date.getFullYear());;
    newGroupElement.getElementsByClassName("groupdesc")[0].innerText = groupData["Description"];
    newGroupElement.getElementsByClassName("groupsubject")[0].innerText = groupData["Subject"];
    newGroupElement.getElementsByClassName("grouptitle")[0].innerText = groupData["Name"];
    newGroupElement.getElementsByTagName("a")[0].href = "/groups/" + groupID;
    newGroupElement.getElementsByClassName("StudyLevel")[0].className += " "+groupData["StudyLevel"].replace(/ /g,"");
    newGroupElement.getElementsByClassName("StudyLevel")[0].innerText = groupData["StudyLevel"];

    if (groupData["IsPrivate"] == "0") {
        newGroupElement.getElementsByClassName("isprivate")[0].innerText = "public";
        newGroupElement.getElementsByClassName("isprivate")[0].className = "ispublic";
    }

    groupElement.parentNode.appendChild(newGroupElement);
}  

//loading upcoming sessions 
let sessionElement = document.getElementById("sessionref");
for (let index = 0; index < UserGroupData["UpcomingSessions"].length; index++) {
    let sessionData = UserGroupData["UpcomingSessions"][index];
    let sessionID = sessionData["SessionID"];
    let newSessionElement = sessionElement.cloneNode(true);

    let startTime =  new Date(sessionData["Date"]+"T"+sessionData["StartTime"]+":00Z");
    let endTime =  new Date(sessionData["Date"]+"T"+sessionData["EndTime"]+":00Z");
    let linkElement = newSessionElement.getElementsByTagName("a")[0];
    let imageElement = linkElement.getElementsByTagName("img")[0];
    
    newSessionElement.id = "";
    newSessionElement.style.cssText = "";
    newSessionElement.getElementsByClassName("sessiontitle")[0].innerText = sessionData["Name"];
    newSessionElement.getElementsByClassName("sessiondate")[0].innerText = String(startTime.getDate()).padStart(2,"0")+"/"+String(startTime.getMonth() + 1).padStart(2,"0")+"/"+String(startTime.getFullYear());
    newSessionElement.getElementsByClassName("sessiontime")[0].innerText = String(startTime.getHours()).padStart(2,"0")+":"+String(startTime.getMinutes()).padStart(2,"0") + " - " + String(endTime.getHours()).padStart(2,"0")+":"+String(endTime.getMinutes()).padStart(2,"0");
    newSessionElement.getElementsByClassName("sessionlocation")[0].innerText = sessionData["Location"];
    newSessionElement.getElementsByClassName("sessionattendees")[0].innerText = "Attendees: "+sessionData["AttendeeCount"];

    
    linkElement.href = "/groups/" + sessionData["GroupID"] ;
    //Handling link to session
    imageElement.onclick = (ev) => {
        sessionStorage.setItem("selectedTab","sessiontab");
        sessionStorage.setItem("targetListID","sessionelement"+String(sessionData["SessionID"]));
    }
    
    sessionElement.parentElement.append(newSessionElement);
}
//loading due tasks
let taskElement = document.getElementById("taskref");
for (let index = 0; index < UserGroupData["DueTasks"].length; index++) {
    let taskData = UserGroupData["DueTasks"][index];
    let taskID = taskData["TaskID"];
    let newTaskElement = taskElement.cloneNode(true);
    let linkElement = newTaskElement.getElementsByTagName("a")[0];
    let imageElement = linkElement.getElementsByTagName("img")[0];
    let userTaskStatus = taskData["TaskStatus"].toLowerCase()
    
    let dueDateTime = new Date(taskData["DueDateTime"]);
    let dueDateField = String(dueDateTime.getDate())+"/"+String(dueDateTime.getMonth() + 1)+"/"+String(dueDateTime.getFullYear());
    let timeField =  String(dueDateTime.getHours()).padStart(2,"0")+":"+String(dueDateTime.getMinutes()).padStart(2,"0");
    //Handling link to session
    linkElement.href = "/groups/" + taskData["GroupID"];
    imageElement.onclick = (ev) => {
        sessionStorage.setItem("selectedTab","tasktab");
        sessionStorage.setItem("targetListID","taskelement"+String(taskData["TaskID"]));
    }

    newTaskElement.getElementsByClassName("taskassignees")[0].innerText = "Assigned to: "+taskData["AssigneesString"];
    newTaskElement.getElementsByClassName("taskassignees")[0].title = taskData["AssigneesString"];

    newTaskElement.getElementsByClassName(userTaskStatus+"button")[0].className += " selectedstatus";
    newTaskElement.id = "";
    newTaskElement.style.cssText = "";
    newTaskElement.getElementsByClassName("tasktitle")[0].innerText = taskData["Name"];
    newTaskElement.getElementsByClassName("taskduedate")[0].innerText = "Due "+dueDateField;
    newTaskElement.getElementsByClassName("taskduetime")[0].innerText = timeField;
    
    newTaskElement.getElementsByClassName(userTaskStatus+"button")[0].className += " selectedstatus";

    taskElement.parentElement.append(newTaskElement);
}