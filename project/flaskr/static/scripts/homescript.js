//user profile button
let profilebutton = document.getElementById("profilebutton");
let profilemenu = document.getElementById("menucontainer");
let cancelEditProfileButton = document.getElementById("canceleditprofilebutton");
let curtain = document.getElementById("curtain");

profilebutton.onclick = (event) => {
    if (profilebutton.className === "unclickedimage"){
        if (curtain.hidden === false) {
            return;
        }
        profilebutton.className = "clickedimage";
        profilemenu.hidden = false;
        curtain.hidden = false;
    } else if (profilebutton.className === "clickedimage") {
        profilebutton.className = "unclickedimage";
        profilemenu.hidden = true;
        curtain.hidden = true;
    }
}
cancelEditProfileButton.onclick = (event) => {
    profilebutton.className = "unclickedimage";
    profilemenu.hidden = true;
    curtain.hidden = true;
}

//create group button
let groupbutton = document.getElementById("createbutton");
let cancelCreateGroupButton = document.getElementById("cancelcreategroupbutton");
let groupmenu = document.getElementById("creategroupmenu");

groupbutton.onclick = (event) => {
    if (curtain.hidden === true){
        groupbutton.className = "topbuttons clickedgroupbutton"
        groupmenu.hidden = false;
        curtain.hidden = false;
    }
}
cancelCreateGroupButton.onclick = (event) => {
    groupbutton.className = "topbuttons"
    groupmenu.hidden = true;
    curtain.hidden = true;
}
//create group type button
let privateButton = document.getElementById("privatebutton");
let publicButton = document.getElementById("publicbutton");
let isPrivateField = document.getElementById("isprivatefield");

publicButton.onclick = (event) => {
    if (isPrivateField.value  === "1") {
        isPrivateField.value  = "0";
        publicButton.className = "selectedtype";
        privateButton.className = "unselectedtype";
    } 
}
privateButton.onclick = (event) => {
    if (isPrivateField.value  === "0") {
        isPrivateField.value = "1";
        privateButton.className = "selectedtype";
        publicButton.className = "unselectedtype";
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

// Color selection system
let profileStyleColorInput = document.getElementById("profilestylecolor");
let profileColorListDiv = document.getElementById("profilecolorlist");
let profileSelectedButton = document.getElementById("profilecontrol"+profileStyleColorInput.value);

let groupStyleColorInput = document.getElementById("groupstylecolor");
let groupColorListDiv = document.getElementById("groupcolorlist");
let groupSelectedButton = document.getElementById("groupcontrol"+groupStyleColorInput.value);

let profileButtonList = profileColorListDiv.children;
for (let index = 0; index < profileButtonList.length; index++) {
    const button = profileButtonList[index]
    button;
    button.onclick = function(){
        profileSelectedButton.className = "";
        profileStyleColorInput.value = button.value;
        button.className = "selectedcolor";
        profileSelectedButton = button;
    }
}
let groupButtonList = groupColorListDiv.children;
for (let index = 0; index < groupButtonList.length; index++) {
    const button = groupButtonList[index];
    button;
    button.onclick = function(){
        groupSelectedButton.className = "";
        groupStyleColorInput.value = button.value;
        button.className = "selectedcolor";
        groupSelectedButton = button;
    }
}


//loading joined groups 

let groupElement = document.getElementById("groupelementref");

for (let index = 0; index < userGroupsData["JoinedGroups"].length; index++) {
    let groupData = userGroupsData["JoinedGroups"][index];
    let groupID = groupData["GroupID"]
    let newGroupElement = groupElement.cloneNode(true);

    newGroupElement.id = "";
    newGroupElement.style.cssText = "";
    newGroupElement.getElementsByTagName("svg")[0].style.cssText = "fill:"+groupData["StyleColor"] ;
    newGroupElement.getElementsByClassName("grouplabel")[0].innerText = groupData["Name"];
    newGroupElement.getElementsByTagName("a")[0].href = "/groups/" + groupID;
    
    groupElement.parentNode.appendChild(newGroupElement);
}  

//loading upcoming sessions 
let sessionElement = document.getElementById("sessionelementref");
for (let index = 0; index < userGroupsData["UpcomingSessions"].length; index++) {
    let sessionData = userGroupsData["UpcomingSessions"][index];
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
    linkElement.href = "/groups/" + sessionData["GroupID"] ;
    //Handling link to session
    imageElement.onclick = (ev) => {
        sessionStorage.setItem("selectedTab","sessiontab");
        sessionStorage.setItem("targetListID","sessionelement"+String(sessionData["SessionID"]));
    }
    
    sessionElement.parentElement.append(newSessionElement);
}
//loading due tasks
let taskElement = document.getElementById("taskelementref");
for (let index = 0; index < userGroupsData["DueTasks"].length; index++) {
    let taskData = userGroupsData["DueTasks"][index];
    let taskID = taskData["TaskID"];
    let newTaskElement = taskElement.cloneNode(true);
    let linkElement = newTaskElement.getElementsByTagName("a")[0];
    let imageElement = linkElement.getElementsByTagName("img")[0];

    let dueDateTime = new Date(taskData["DueDateTime"]);
    let dueDateField = String(dueDateTime.getDate())+"/"+String(dueDateTime.getMonth() + 1)+"/"+String(dueDateTime.getFullYear());
    let timeField =  String(dueDateTime.getHours()).padStart(2,"0")+":"+String(dueDateTime.getMinutes()).padStart(2,"0");
    //Handling link to session
    linkElement.href = "/groups/" + taskData["GroupID"];
    imageElement.onclick = (ev) => {
        sessionStorage.setItem("selectedTab","tasktab");
        sessionStorage.setItem("targetListID","taskelement"+String(taskData["TaskID"]));
    }
    
    newTaskElement.id = "";
    newTaskElement.style.cssText = "";
    newTaskElement.getElementsByClassName("tasktitle")[0].innerText = taskData["Name"];
    newTaskElement.getElementsByClassName("taskduedate")[0].innerText = "Due "+dueDateField+" at : "+timeField;


    taskElement.parentElement.append(newTaskElement);
}

//Group search system

let searchForm = document.forms["searchform"];
let searchElementRef = document.getElementById("searchelementref");
let canFetch = true;

searchForm.addEventListener("submit",(ev)=>{
    ev.preventDefault();
    if (canFetch === false){
        return;
    }
    canFetch = false;
    let searchUrl = "/search?query="+encodeURIComponent(searchForm.elements["query"].value)+"&level="+encodeURIComponent(searchForm.elements["StudyLevel"].value)+"&privacy="+searchForm.elements["Privacy"].value;
    
    fetch(searchUrl).then( response => response.json(), reason => { console.log(reason); return null;}).then(data => {
        if (data === null){
            return
        }
        //data received
        //clearing search group list
        for (child of searchElementRef.parentElement.children){
            if (! searchElementRef.isEqualNode(child)){
                child.remove();
            }
        }
        for (let index = 0; index < data.length; index++){
            let groupData = data[index];
            let groupID = groupData["GroupID"];
            
            let newGroupElement = searchElementRef.cloneNode(true);

            newGroupElement.id = "";
            newGroupElement.style.cssText = "";
            newGroupElement.getElementsByTagName("svg")[0].style.cssText = "fill:"+groupData["StyleColor"] ;

            newGroupElement.getElementsByClassName("groupid")[0].innerText = "ID: "+groupData["GroupID"];
            newGroupElement.getElementsByClassName("membercount")[0].innerText = groupData["MemberCount"];
            newGroupElement.getElementsByClassName("searchdesc")[0].innerText = groupData["Description"];
            newGroupElement.getElementsByClassName("searchsubject")[0].innerText = groupData["Subject"];
            newGroupElement.getElementsByClassName("searchtitle")[0].innerText = groupData["Name"];
            newGroupElement.getElementsByTagName("a")[0].href = "/groups/" + groupID;
            newGroupElement.getElementsByClassName("StudyLevel")[0].className += " "+groupData["StudyLevel"].replace(/ /g,"");
            newGroupElement.getElementsByClassName("StudyLevel")[0].innerText = groupData["StudyLevel"];

            if (groupData["IsPrivate"] == "0") {
                newGroupElement.getElementsByClassName("isprivate")[0].innerText = "public";
                newGroupElement.getElementsByClassName("isprivate")[0].className = "ispublic";
            }

            searchElementRef.parentElement.append(newGroupElement);
        }
    })
    setTimeout(()=> {
        canFetch = true;
    }, 500)
})

// handling overview tab selection

for (button of document.getElementsByClassName("viewallbutton")) {
    const viewAllButton = button;
    viewAllButton.onclick = (ev) => {
        sessionStorage.setItem("overviewSelectedTab",viewAllButton.dataset.overviewtab);
        
    }

}