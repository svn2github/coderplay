
var settingsTemplate;
var isEditing;
var toXMLField;

function readBdeSettings() {

    isEditing = new Array();
    toXMLField = new Array();

    //settingsTemplate = new ActiveXObject("Msxml2.DOMDocument.3.0");
    settingsTemplate = new ActiveXObject("Microsoft.XMLDOM");
    settingsTemplate.async = false;
    settingsTemplate.load("bdesettings.xml");


    nodeBdeSettings = settingsTemplate.documentElement;

    nodeHeader = nodeBdeSettings.getElementsByTagName("Header")[0];
    nodeClient = nodeHeader.getElementsByTagName("Client")[0];
    nodeAnalyst = nodeHeader.getElementsByTagName("Analyst")[0];

    thisNode = nodeClient.firstChild;
    clientName.innerHTML = thisNode.firstChild.nodeValue;
    toXMLField[clientName] = thisNode;


    thisNode = nodeAnalyst.firstChild;
    analystName.innerHTML = thisNode.firstChild.nodeValue;

    now = new Date();
    dateString = now.getFullYear() + '-' + (now.getMonth() + 1) + '-' + now.getDate();
    date.innerHTML = dateString;
    // Update the XML DOM
    thisNode = thisNode.nextSibling;
    thisNode.firstChild.nodeValue = dateString;

    

    // settingsTemplate.save("new.xml");




}

function getinput(obj) {

    if (isEditing[obj]) {
        return;
    }
    isEditing[obj] = true;
    obj.oldValue = obj.innerHTML;
    displayText = '<input type="text" class="textinput" id="' + obj.id + '_input" size="15" onKeyPress="keyInTextInput(event,'+obj.id+')" value="' + obj.oldValue + '" />';

    displayText += '<img class="yes" onClick="yesTextInput(' + obj.id +')" src="resources/img_trans.gif" width="1" height="1" />';

    displayText += '<img class="no" onClick="noTextInput(' + obj.id + ')" src="resources/img_trans.gif" width="1" height="1" />';

    obj.innerHTML = displayText;
    document.getElementById(obj.id + '_input').focus();

    /*
    displayText = displayText.replace(/[&]/g, '&amp;');
    displayText = displayText.replace(/[<]/g, '&lt;');
    displayText = displayText.replace(/[>]/g, '&gt;');
    displayText = displayText.replace(/[\n]/g, '<br>');
    debugarea.innerHTML = displayText;
    */
}

function yesTextInput(obj) {
    var newValue = document.getElementById(obj.id + '_input').value;
    obj.innerHTML = newValue;
    isEditing[obj] = false;
}

function noTextInput(obj) {
    obj.innerHTML = obj.oldValue;
    isEditing[obj] = false;
}

function keyInTextInput(e, obj) {
    // return is 13
    // esc is 27
    if (e.keyCode == 13) {
        yesTextInput(obj);
    }
    if (e.keyCode == 27) {
        noTextInput(obj);
    }
} 
