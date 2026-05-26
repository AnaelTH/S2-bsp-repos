let curtain = document.getElementById("curtain");
let currentUrl = window.location.href;

//Handling session/tasks displaying
document.addEventListener("DOMContentLoaded", () => {
    if (sessionStorage.getItem("targetListID") !== null){
        targetElement = document.getElementById(sessionStorage.getItem("targetListID"));
        sessionStorage.removeItem("targetListID");
        targetElement.scrollIntoView({behavior:"smooth",block:"center"});
        let ogColor = targetElement.style.borderColor;
        targetElement.style.borderColor = "#00c8ff";
        setTimeout(() => {
            targetElement.style.borderColor = ogColor;
        }, 3000);
    }
});

//Loading Members data:
let taskAssigneeList = document.getElementsByClassName("taskassigneelist");
let createTaskAssigneeList = document.getElementById("createtaskassigneelist");

let MemberElementRef = document.getElementById("groupmemberref");

for (userID in CurrentGroupData["Members"]) {
    memberData = CurrentGroupData["Members"][userID];
    //adding members to task assignee list

    for (assigneeList of taskAssigneeList){
        let taskAssigneeElement = document.getElementById("taskassigneeref").cloneNode(true);
        taskAssigneeElement.style.cssText = "";
        let inputElement = taskAssigneeElement.getElementsByTagName("input")[0];
        let profileImage = taskAssigneeElement.getElementsByTagName("svg")[0];
        let memberUsernameElement = taskAssigneeElement.getElementsByClassName("memberusername")[0];
        
        memberUsernameElement.innerText =  memberData[0];

        inputElement.disabled = false;
        inputElement.value = memberData[0];
        
        //Checking input field value as the result of a potential operation
        if (createTaskAssignees){
            if (assigneeList.id === createTaskAssigneeList.id && memberData[0] in createTaskAssignees ){
                inputElement.checked = true;
            }
        }
        if (editTaskAssignees){
            if (not (assigneeList.id ===createTaskAssigneeList.id) && (memberData[0] in editTaskAssignees)){
                inputElement.checked = true;
            }
        }
        
        profileImage.style.cssText = profileImage.style.cssText + "; fill: "+ memberData[1];
        assigneeList.append(taskAssigneeElement);
    }
    //adding members to members list
    
    let newMemberElement = MemberElementRef.cloneNode(true);
    let memberRoleElement = newMemberElement.getElementsByClassName("memberrole")[0];
    newMemberElement.style.cssText = "";
    newMemberElement.getElementsByClassName("memberusername")[0].innerText = memberData[0];
    newMemberElement.getElementsByClassName("memberemail")[0].innerText = memberData[2];
    newMemberElement.getElementsByClassName("profileimage")[0].style.cssText = "fill: "+memberData[1];
    memberRoleElement.innerText = memberData[3];
    memberRoleElement.className = "memberrole " + memberData[3].toLowerCase();
    
    // edit role buttons
    if (["Owner","Admin"].includes(CurrentGroupData["UserRole"])){
        for (form of newMemberElement.getElementsByClassName("setroleform")){
            form.action = currentUrl+"/members/"+String(userID)+"/role";
        }
        let setMemberButton = newMemberElement.getElementsByClassName("setmemberbutton")[0];
        let setAdminButton = newMemberElement.getElementsByClassName("setadminbutton")[0];
        if (memberData[3] === "Member"){
            setMemberButton.disabled = true;
            setMemberButton.style.cssText = "display:none;";
        } else if (memberData[3] === "Admin"){
            setAdminButton.disabled = true;
            setAdminButton.style.cssText = "display:none;";
        } else {
            setAdminButton.disabled = true;
            setAdminButton.style.cssText = "display:none;";
            setMemberButton.disabled = true;
            setMemberButton.style.cssText = "display:none;";
        }
    //kick button
        let kickForm = newMemberElement.getElementsByClassName("kickform")[0];
        let kickButton = newMemberElement.getElementsByClassName("kickbutton")[0];
        kickForm.action = currentUrl+"/members/"+String(userID)+"/kick";
        if (memberData[3] === "Owner" || CurrentGroupData["Username"] === memberData[0] ){
            kickButton.disabled = true;
            kickButton.style.cssText = "display:none;";
        }
    }

    MemberElementRef.parentElement.append(newMemberElement);
}
//loading requests 

let requestElementRef = document.getElementById("requestelementref");

for (userID in CurrentGroupData["Requests"]){
    let requestData = CurrentGroupData["Requests"][userID]
    

    let newRequestElement = requestElementRef.cloneNode(true);
    newRequestElement.style.cssText = "";
    newRequestElement.getElementsByClassName("requestusername")[0].innerText = requestData["Username"];
    newRequestElement.getElementsByClassName("requestemail")[0].innerText = requestData["Email"];
    newRequestElement.getElementsByTagName("svg")[0].style.cssText = "fill: "+requestData["StyleColor"];

    if (["Owner","Admin"].includes(CurrentGroupData["UserRole"])){
        requestUrl = currentUrl+"/requests/"+String(userID);
        newRequestElement.getElementsByClassName("declinerequestform")[0].action = requestUrl;
        newRequestElement.getElementsByClassName("acceptrequestform")[0].action = requestUrl;
    }

    requestElementRef.parentElement.append(newRequestElement);
}

//loading Sessions

const currentDate = new Date();
const currentStringDate = currentDate.toISOString().split("T")[0];
const currentStringTime = currentDate.toISOString().split("T")[1].slice(0,5);

let deleteSessionMenu =  document.getElementById("deletesessionmenu");
let finalDeleteSessionButton =  document.getElementById("finaldeletesessionbutton");
let cancelDeleteSessionButton = document.getElementById("canceldeletesessionbutton");

let pastSessionRef = document.getElementById("pastsessionref");
let upcommingSessionRef = document.getElementById("upcomingsessionref");

for (let index = 0; index < CurrentGroupData["Sessions"].length; index++) {
    let sessionData = CurrentGroupData["Sessions"][index];
    let sessionID = sessionData["SessionID"];
    let sessionStartTime = new Date(sessionData["Date"]+"T"+sessionData["StartTime"]+":00Z");
    let sessionEndTime = new Date(sessionData["Date"]+"T"+sessionData["EndTime"]+":00Z");

    let sessionDateField = String(sessionStartTime.getDate()).padStart(2,"0")+"/"+(String(sessionStartTime.getMonth()+1)).padStart(2,"0")+"/"+String(sessionStartTime.getFullYear());
    let sessionEndTimeField = String(sessionEndTime.getHours()).padStart(2,"0")+":"+String(sessionEndTime.getMinutes()).padStart(2,"0");
    let sessionStartTimeField = String(sessionStartTime.getHours()).padStart(2,"0")+":"+String(sessionStartTime.getMinutes()).padStart(2,"0");

    let pastSession = (sessionEndTime < currentDate);
    let newSessionElement;
    if (pastSession){
        newSessionElement = pastSessionRef.cloneNode(true);
    } else {
        newSessionElement = upcommingSessionRef.cloneNode(true);
    }
    newSessionElement.id = "sessionelement"+String(sessionID);
    newSessionElement.getElementsByClassName("sessiondate")[0].innerText =sessionDateField;
    newSessionElement.getElementsByClassName("sessionlocation")[0].innerText = sessionData["Location"];
    newSessionElement.getElementsByClassName("sessiontime")[0].innerText = sessionStartTimeField+" - "+sessionEndTimeField;
    newSessionElement.getElementsByClassName("sessionattendees")[0].innerText = sessionData["Attendees"];
    newSessionElement.getElementsByClassName("sessiondesc")[0].innerText = sessionData["Description"];
    newSessionElement.getElementsByClassName("sessiontitle")[0].innerText = sessionData["Name"];

    if (pastSession){
        pastSessionRef.parentNode.append(newSessionElement);
    } else {
        //handling buttons
        //delete session button
        if (["Owner","Admin"].includes(CurrentGroupData["UserRole"])) {
            let deleteSessionButton = newSessionElement.getElementsByClassName("deletebutton")[0];
            let editTabButton = newSessionElement.getElementsByClassName("edittabbutton")[0];
            deleteSessionButton.onclick = (event) => {
                if (curtain.hidden === true){
                    //changing form action url
                    let deleteForm = document.forms["deletesessionform"];
                    deleteForm.action = currentUrl+"/sessions/"+String(sessionID)+"/delete";
                    deleteSessionMenu.hidden = false;
                    curtain.hidden = false;
                }
            }
            cancelDeleteSessionButton.onclick = (event) => {
                deleteSessionMenu.hidden = true;
                curtain.hidden = true;
            }
        }
        
        //attend/unattend buttons

        if (["Member","Owner","Admin"].includes(CurrentGroupData["UserRole"])){
            let attendForm = newSessionElement.getElementsByClassName("attendform");
            let unattendForm= newSessionElement.getElementsByClassName("unattendform");
            if (! sessionData["IsUserAttending"] === true ) {
                attendForm[0].action = currentUrl+"/sessions/"+String(sessionID)+"/attend";
                unattendForm[0].getElementsByTagName("button")[0].disabled = true;
                unattendForm[0].style.cssText = "display:none"
            } else {
                unattendForm[0].action = currentUrl+"/sessions/"+String(sessionID)+"/unattend";
                attendForm[0].getElementsByTagName("button")[0].disabled = true;
                attendForm[0].style.cssText = "display:none"
            }
            
        }
        //Edit session button
        
        if (["Owner","Admin"].includes(CurrentGroupData["UserRole"])) {
            let editSessionButton = newSessionElement.getElementsByClassName("edittabbutton");
            let cancelEditSessionButton = document.getElementById("canceleditsessionbutton");
            let editSessionMenu = document.getElementById("editsessionmenu");

            editSessionButton[0].onclick = (event) => {
                if (curtain.hidden === true){
                    //changing form fields
                    let editForm = document.forms["editsessionform"];
                    editForm.action = currentUrl+"/sessions/"+String(sessionID);
                    let editFormFields = editForm.elements;
                    for (elements of editFormFields){
                        
                    }
                    editFormFields["Name"].value = sessionData["Name"];
                    editFormFields["Date"].value = sessionDateField.split("/")[2]+"-"+sessionDateField.split("/")[1]+"-"+sessionDateField.split("/")[0];
                    editFormFields["EndTime"].value = sessionEndTimeField;
                    editFormFields["StartTime"].value = sessionStartTimeField;
                    editFormFields["Location"].value = sessionData["Location"];
                    editFormFields["Description"].value = sessionData["Description"];

                    editSessionMenu.hidden = false;
                    curtain.hidden = false;
                }
            }
            cancelEditSessionButton.onclick = (event) => {
            editSessionMenu.hidden = true;
            curtain.hidden = true;
            }
        }
        
        upcommingSessionRef.parentNode.append(newSessionElement);
    }
}  


//loading Tasks
let taskDict= {}
let deleteTaskMenu =  document.getElementById("deletetaskmenu");
let cancelDeleteTaskButton = document.getElementById("canceldeletetaskbutton");
let deleteTaskForm = document.forms["deletetaskform"];

let cancelEditTaskButton = document.getElementById("canceledittaskbutton");
let editTaskMenu = document.getElementById("edittaskmenu");

let taskElementRef = document.getElementById("taskelementref");

let pendingTaskContainer =document.getElementById("pendingtasks");
let completedTaskContainer =document.getElementById("completedtasks");
let inProgressTaskContainer =document.getElementById("inprogresstasks");

let editTaskAssigneeList = document.getElementById("edittaskassigneelist");



for (let index = 0; index < CurrentGroupData["Tasks"].length; index++) {

    let taskData = CurrentGroupData["Tasks"][index];
    let taskID = taskData["TaskID"];
    let taskDueDateTime = new Date(taskData["DueDateTime"]);

    let taskDueDateField = String(taskDueDateTime.getDate()).padStart(2,"0")+"/"+(String(taskDueDateTime.getMonth()+1)).padStart(2,"0")+"/"+String(taskDueDateTime.getFullYear());
    let taskDueTimeField = String(taskDueDateTime.getHours()).padStart(2,"0")+":"+String(taskDueDateTime.getMinutes()).padStart(2,"0");

    let newTaskElement = taskElementRef.cloneNode(true);
    newTaskElement.style.cssText = "";
    newTaskElement.id = "taskelement"+String(taskID);

    newTaskElement.getElementsByClassName("taskduedate")[0].innerText = taskDueDateField;
    newTaskElement.getElementsByClassName("taskduetime")[0].innerText = taskDueTimeField;
    newTaskElement.getElementsByClassName("taskassignees")[0].innerText ="Assigned To: "+taskData["AssigneesString"];
    newTaskElement.getElementsByClassName("taskassignees")[0].title =taskData["AssigneesString"];
    newTaskElement.getElementsByClassName("taskdesc")[0].innerText = taskData["Description"];
    newTaskElement.getElementsByClassName("tasktitle")[0].innerText = taskData["Name"];
    
    //adding task assignees list to overall list
    taskDict[taskID] = {};
    taskDict[taskID] = taskData["AssigneesDict"];
    
    //handling buttons
    //task status
    if (CurrentGroupData["Username"] in taskDict[taskID]){
        let statusPendingButton = newTaskElement.getElementsByClassName("pendingbutton")[0];
        let statusInProgressButton = newTaskElement.getElementsByClassName("inprogressbutton")[0];
        let statusCompletedButton = newTaskElement.getElementsByClassName("completedbutton")[0];
        
        let statusUrl = currentUrl+"/tasks/"+String(taskID)+"/status";
        statusCompletedButton.formAction = statusUrl;
        statusPendingButton.formAction = statusUrl;
        statusInProgressButton.formAction = statusUrl;

        newTaskElement.getElementsByClassName("taskstatus")[0].hidden = false;
        newTaskElement.getElementsByClassName(taskDict[taskID][CurrentGroupData["Username"]].toLowerCase()+"button")[0].className = taskDict[taskID][CurrentGroupData["Username"]].toLowerCase()+"button selectedstatus";
        newTaskElement.getElementsByClassName(taskDict[taskID][CurrentGroupData["Username"]].toLowerCase()+"button")[0].disabled = true;
        
    }

    if (["Owner","Admin"].includes(CurrentGroupData["UserRole"]) ) {
    //remove task button
        let deleteTaskButton = newTaskElement.getElementsByClassName("redbutton");
        deleteTaskButton[0].onclick = (ev) => {
            if (curtain.hidden === true){
                deletetaskform.action = currentUrl+"/tasks/"+String(taskID)+"/delete";
                curtain.hidden = false;
                deleteTaskMenu.hidden = false;
            }
        }
        cancelDeleteTaskButton.onclick = (ev) => {
            if (curtain.hidden === false){
                curtain.hidden = true;
                deleteTaskMenu.hidden = true;
            }
        }
    //Edit task button
        let editTaskButton = newTaskElement.getElementsByClassName("edittabbutton");
        editTaskButton[0].onclick = (event) => {
            if (curtain.hidden === true){
                //changing form fields
                let editForm = document.forms["edittaskform"];
                editForm.action = currentUrl+"/tasks/"+String(taskID);
                let editFormFields = editForm.elements;

                editFormFields["Name"].value = taskData["Name"];
                editFormFields["DueDate"].value = taskDueDateField.split("/")[2]+"-"+taskDueDateField.split("/")[1]+"-"+taskDueDateField.split("/")[0]
                editFormFields["DueTime"].value = taskDueTimeField;
                editFormFields["Description"].value = taskData["Description"];

                editTaskMenu.hidden = false;
                curtain.hidden = false;

                //setting checked assignee fields 
                for (input of editTaskAssigneeList.getElementsByTagName("input")){
                    if (input.value in taskDict[taskID]){
                        input.checked = true;
                    }
                }
            }
        }
        cancelEditTaskButton.onclick = (event) => {
            editTaskMenu.hidden = true;
            curtain.hidden = true;
        }
    }

    if (CurrentGroupData["Username"] in taskDict[taskID]){
        document.getElementById(taskDict[taskID][CurrentGroupData["Username"]].toLowerCase()+"tasks").append(newTaskElement);
    } else{
        pendingTaskContainer.append(newTaskElement);
    }                
}
 
// hiding task status titles:

let inProgressTaskTitle = document.getElementById("inprogresstaskstitle");
let completedTaskTitle = document.getElementById("completedtaskstitle");

if ((["Admin","Owner","Member"].includes(CurrentGroupData["UserRole"]))) {
    inProgressTaskTitle.style.cssText= "";
    completedTaskTitle.style.cssText= "";
}

if (["Owner","Admin"].includes(CurrentGroupData["UserRole"])) {
// tick-all button
    for (listElement of taskAssigneeList){
        let tickAllButton = listElement.parentElement.getElementsByClassName("tickallbutton")[0];
        let taskForm = tickAllButton.form;

        tickAllButton.onclick = (ev) => {
            let ticked = ! (taskForm.getElementsByClassName("membercheckbox")[1].checked);

            for ( element of taskForm.elements){
                if ( element.className ==="membercheckbox" && element.checked !== ticked ){
                    element.checked = ticked;
                }
            }
        }
    }

// createtask button
    let newTaskButton = document.getElementById("newtaskbutton");
    let createTaskMenu = document.getElementById("createtaskmenu");
    let cancelCreateTaskButton = document.getElementById("cancelecreatetaskbutton");
    newTaskButton.onclick = (event) => {
        if (curtain.hidden === true){
            createTaskMenu.hidden = false;
            curtain.hidden = false;
        }
    }
    cancelCreateTaskButton.onclick = (event) => {
        
        createTaskMenu.hidden = true;
        curtain.hidden = true;
    }

//Create session button

    let newSessionButton = document.getElementById("newsessionbutton");
    let createSessionMenu = document.getElementById("createsessionmenu");
    let cancelNewSessionButton = document.getElementById("cancelecreatesessionbutton");
    newSessionButton.onclick = (event) => {
        if (newSessionButton.className === ""){
            if (curtain.hidden === false) {
                return;
            }
            newSessionButton.className = "clickedv2";
            createSessionMenu.hidden = false;
            curtain.hidden = false;
        }
    }
    cancelNewSessionButton.onclick = (event) => {
        newSessionButton.className = "";
        createSessionMenu.hidden = true;
        curtain.hidden = true;
    }
}

//edit group button

if (CurrentGroupData["UserRole"] === "Owner") {
    let editGroupButton = document.getElementById("editgroupbutton");
    let cancelEditGroupButton = document.getElementById("canceleditgroupbutton");
    let editGroupMenu = document.getElementById("editgroupmenu");

    editGroupButton.onclick = (event) => {
        if (editGroupButton.className === ""){
            if (curtain.hidden === false) {
                return;
            }
            editGroupButton.className = "clickedv2";
            editGroupMenu.hidden = false;
            curtain.hidden = false;
        }
    }
    cancelEditGroupButton.onclick = (event) => {
        editGroupButton.className = "";
        editGroupMenu.hidden = true;
        curtain.hidden = true;
    }

// DeleteGroup button
    let deleteGroupButton = document.getElementById("deletegroupbutton");
    let deleteGroupMenu =  document.getElementById("deletegroupmenu");
    let cancelDeleteGroupButton = document.getElementById("canceldeletegroupbutton");
    
    deleteGroupButton.onclick = (event) => {
        if (curtain.hidden === true){
            deleteGroupButton.className = "clickedv2"
            deleteGroupMenu.hidden = false;
            curtain.hidden = false;
        }
    }
    cancelDeleteGroupButton.onclick = (event) => {
        deleteGroupButton.className = ""
        deleteGroupMenu.hidden = true;
        curtain.hidden = true;
    }
}


//Study level selection system
let bachelorButton = document.getElementById("bachelorbutton");
let masterButton = document.getElementById("masterbutton");
let highSchoolButton = document.getElementById("highschoolbutton");
let studyLevelField = document.getElementById("studylevelfield");

bachelorButton.onclick = (event) => {
    if (studyLevelField.value  !== "Bachelor") {
        studyLevelField.value  = "Bachelor";
        masterButton.className = "";
        highSchoolButton.className = "";
        bachelorButton.className = "selected";
    } 
}
masterButton.onclick = (event) => {
    if (studyLevelField.value  !== "Master") {
        studyLevelField.value  = "Master";
        masterButton.className = "selected";
        highSchoolButton.className = "";
        bachelorButton.className = "";
    } 
}
highSchoolButton.onclick = (event) => {
    if (studyLevelField.value  !== "High School") {
        studyLevelField.value  = "High School";
        masterButton.className = "";
        highSchoolButton.className = "selected";
        bachelorButton.className = "";
    } 
}
//Edit group type

if ( ["Owner","Admin"].includes(CurrentGroupData["UserRole"]) ) {
    let publicButton = document.getElementById("publicbutton");
    let privateButton = document.getElementById("privatebutton");
    let isPrivateField = document.getElementById("isprivatefield");
    
    publicButton.onclick = (event) => {
    if (isPrivateField.value  === "1") {
        isPrivateField.value  = 0;
        publicButton.className = "selectedtype";
        privateButton.className = "unselectedtype";
    } 
    }
    privateButton.onclick = (event) => {
        if (isPrivateField.value  === "0") {
            isPrivateField.value = 1;
            privateButton.className = "selectedtype";
            publicButton.className = "unselectedtype";
        }
    }

// Color selection system
    let styleColorInput = document.getElementById("stylecolor");
    let colorListDiv = document.getElementById("colorlist");
    let selectedButton = document.getElementById("control"+styleColorInput.value);

    let buttonList = colorListDiv.children;

    for (let index = 0; index < buttonList.length; index++) {
        const button = buttonList[index]
        button;
        button.onclick = function(){
            selectedButton.className = "";
            styleColorInput.value = button.value;
            button.className = "selectedcolor";
            selectedButton = button;
        }
    }
}

//tab selection system
let selectedTabId = sessionStorage.getItem("selectedTab");
if (selectedTabId === null){
    sessionStorage.setItem("selectedTab","sessiontab"); 
}
let selectedTab = document.getElementById(sessionStorage.getItem("selectedTab"));
selectedTab.className = "selectedtab";
document.getElementById(selectedTab.id.slice(0,selectedTab.id.length - 3)+"tabcontent").hidden = false;

const tabsContainer = document.getElementById("tabs");
let tabList = tabsContainer.children;

for (let index = 0; index < tabList.length; index ++){
    const tabElement = tabList[index]
    tabElement.onclick = function(ev){
        if ( ! selectedTab.isEqualNode(tabElement) && curtain.hidden === true){
            selectedTab.className = "";
            tabElement.className = "selectedtab";
            const newtabType = tabElement.id.slice(0,tabElement.id.length - 3);
            const previousTabType = selectedTab.id.slice(0,selectedTab.id.length - 3);
            sessionStorage.setItem("selectedTab",tabElement.id);

            let previousTabContent = document.getElementById(previousTabType+"tabcontent");
            previousTabContent.hidden = true;
            let newTabContent = document.getElementById(newtabType+"tabcontent");
            newTabContent.hidden = false;
            
            selectedTab = tabElement;
        }
    }
}
//setting timezones on time fileds

const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
let tzOffsetFields = document.getElementsByClassName("timezone");
for (elements of tzOffsetFields){
    elements.value = timezone;
}
