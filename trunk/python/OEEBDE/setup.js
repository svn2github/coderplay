
var settingsTemplate

function readBdeSettings() {

    
    //settingsTemplate = new ActiveXObject("Msxml2.DOMDocument.3.0")
    settingsTemplate = new ActiveXObject("Microsoft.XMLDOM")
    settingsTemplate.async = false
    settingsTemplate.load("bdesettings.xml")


    nodeBdeSettings = settingsTemplate.documentElement

    nodeHeader = nodeBdeSettings.getElementsByTagName("Header")[0]
    nodeClient = nodeHeader.getElementsByTagName("Client")[0]
    nodeAnalyst = nodeHeader.getElementsByTagName("Analyst")[0]

    thisNode = nodeClient.firstChild
    clientName.innerHTML = thisNode.firstChild.nodeValue
    

    thisNode = nodeAnalyst.firstChild
    analystName.innerHTML = thisNode.firstChild.nodeValue

    now = new Date()
    dateString = now.getFullYear() + '-' + (now.getMonth() + 1) + '-' + now.getDate()
    date.innerHTML = dateString
    // Update the XML DOM
    thisNode = thisNode.nextSibling
    thisNode.firstChild.nodeValue = dateString

   










    

    // settingsTemplate.save("new.xml")




}

function getinput(obj) {
    oldValue = obj.innerHTML;
    displayText = "<input type=\"text\" class=\"textinput\" name=\"" + obj.id+"_input" + "\" size=\"15\" value=\"" + oldValue + "\" />";
    obj.innerHTML = displayText;
}


function test() {
    alert(arguments.callee.caller.toString());
}