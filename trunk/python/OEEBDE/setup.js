
function Hash() {
    this.length = 0;
    this.items = new Array();
    for (var i = 0; i < arguments.length; i += 2) {
        if (typeof (arguments[i + 1]) != 'undefined') {
            this.items[arguments[i]] = arguments[i + 1];
            this.length++;
        }
    }

    this.removeItem = function (in_key) {
        var tmp_previous;
        if (typeof (this.items[in_key]) != 'undefined') {
            this.length--;
            var tmp_previous = this.items[in_key];
            delete this.items[in_key];
        }

        return tmp_previous;
    }

    this.getItem = function (in_key) {
        return this.items[in_key];
    }

    this.setItem = function (in_key, in_value) {
        var tmp_previous;
        if (typeof (in_value) != 'undefined') {
            if (typeof (this.items[in_key]) == 'undefined') {
                this.length++;
            }
            else {
                tmp_previous = this.items[in_key];
            }

            this.items[in_key] = in_value;
        }

        return tmp_previous;
    }

    this.hasItem = function (in_key) {
        return typeof (this.items[in_key]) != 'undefined';
    }

    this.clear = function () {
        for (var i in this.items) {
            delete this.items[i];
        }

        this.length = 0;
    }
}

function debugShow(displayText, isCode) {
    if (isCode != null && isCode != false) {
        displayText = displayText.replace(/[&]/g, '&amp;');
        displayText = displayText.replace(/[<]/g, '&lt;');
        displayText = displayText.replace(/[>]/g, '&gt;');
        displayText = displayText.replace(/[\n]/g, '<br>');
    }
    debugarea.innerHTML = displayText;
}

function addTooltip(displayText, tooltipText) {
    displayText = '<a href="#" class="tt">' + displayText;
    displayText += '<span class="tooltip"><span class="top"></span><span class="middle">';
    displayText += tooltipText + '</span><span class="bottom"></span></span></a>';
    return displayText;
}

var rulesXML;
var vruleList = new Array();
var settingsTemplate;
var isEditing;

function readRulesXML() {
    rulesXML = new ActiveXObject("Microsoft.XMLDOM");
    rulesXML.async = false;
    rulesXML.load("bderules.xml");

    var nodeBdeRules = rulesXML.documentElement;
    var nodeValidations = nodeBdeRules.firstChild;
    var ruleList = nodeValidations.firstChild.childNodes;

    for (ii = 0; ii < ruleList.length; ii++) {
        vruleList[ii] = ruleList[ii].getAttribute('Name');
    }

}


function readBdeSettings() {

    isEditing = new Hash();
    var displayText; 

    //settingsTemplate = new ActiveXObject("Msxml2.DOMDocument.3.0");
    settingsTemplate = new ActiveXObject("Microsoft.XMLDOM");
    settingsTemplate.async = false;
    settingsTemplate.load("bdesettings.xml");

    nodeBdeSettings = settingsTemplate.documentElement;

    nodeHeader = nodeBdeSettings.getElementsByTagName("Header")[0];
    nodeClient = nodeHeader.getElementsByTagName("Client")[0];
    nodeAnalyst = nodeHeader.getElementsByTagName("Analyst")[0];
    nodeGeneral = nodeHeader.nextSibling;
    nodeValidations = nodeGeneral.nextSibling;
    nodeSumups = nodeValidations.nextSibling;
    nodeReporting = nodeSumups.nextSibling;

    thisNode = nodeClient.firstChild;
    clientName.innerHTML = thisNode.firstChild.nodeValue;

    thisNode = nodeAnalyst.firstChild;
    analystName.innerHTML = thisNode.firstChild.nodeValue;

    now = new Date();
    dateString = now.getFullYear() + '-' + (now.getMonth() + 1) + '-' + now.getDate();
    date.innerHTML = dateString;
    // Update the XML DOM
    thisNode = thisNode.nextSibling;
    thisNode.firstChild.nodeValue = dateString;


    // Validations
    actionNode = nodeValidations.firstChild;
    ruleNodes = actionNode.childNodes;
    displayText = '<span class="collapseExpand" title="Collapse" onClick="collapseIt(validations)">&#9650;</span>&nbsp;<table class="frame" style="display:inline;">';
    displayText += '<tr><th>No.</th><th>Name</th></tr>';
    for (ii = 0; ii < ruleNodes.length; ii++) {
        thisid = 'vrule_' + ii;
        displayText += '<tr>';
        displayText += '<td style="color:#003A7D;">' + (ii + 1);
        displayText += '</td><td title="Double click to edit" ondblClick="getSelectInput(' + thisid + ',vruleList)" >';
        displayText += '<span class="editable" id="' + thisid + '" >';
        displayText += ruleNodes[ii].getAttribute('Name');
        displayText += '</span>';
        displayText += '</td>';
        displayText += '</tr>';
    }
    displayText += '</table>';
    document.getElementById('validations').innerHTML = displayText;


    // Sumups
    categoriesNode = nodeSumups.firstChild;
    categoryNodes = categoriesNode.childNodes;
    displayText = '<span class="collapseExpand" title="Collapse" onClick="collapseIt(sumups)">&#9650;</span>&nbsp;<table class="frame" style="display:inline;">';
    displayText += '<tr><th>No.</th><th>Name</th></tr>';
    for (ii = 0; ii < categoryNodes.length; ii++) {
        thisid = 'srule_' + ii;
        displayText += '<tr>';
        displayText += '<td style="color:#003A7D;">' + (ii + 1);
        displayText += '</td><td title="Double click to edit" ondblClick="getTextInput(' + thisid + ')" >';
        displayText += '<span class="editable" id="' + thisid + '" >';
        displayText += categoryNodes[ii].getAttribute('Name');
        displayText += '</span>';
        displayText += '</td>';
        displayText += '</tr>';

    }
    displayText += '</table>';
    document.getElementById('sumups').innerHTML = displayText;


    // Reportings
    categoriesNode = nodeReporting.firstChild;
    categoryNodes = categoriesNode.childNodes;
    displayText = '<span class="collapseExpand" title="Collapse" onClick="collapseIt(reporting)">&#9650;</span>&nbsp;<table class="frame" style="display:inline;">';
    displayText += '<tr><th>No.</th><th>Name</th></tr>';
    for (ii = 0; ii < categoryNodes.length; ii++) {
        thisid = 'rrule_' + ii;
        displayText += '<tr>';
        displayText += '<td style="color:#003A7D;">' + (ii + 1);
        displayText += '</td><td title="Double click to edit" ondblClick="getTextInput(' + thisid + ')" >';
        displayText += '<span class="editable" id="' + thisid + '" >';
        displayText += categoryNodes[ii].getAttribute('Name');
        displayText += '</span>';
        displayText += '</td>';
        displayText += '</tr>';

    }
    displayText += '</table>';
    document.getElementById('reporting').innerHTML = displayText;





    //debugShow(displayText, true);
    

    // settingsTemplate.save("new.xml");




}

function getTextInput(obj) {

    if (isEditing.getItem(obj.id) ) {
        return;
    }
    isEditing.setItem(obj.id, true)
    obj.oldValue = obj.innerHTML;
    obj.parentElement.title = "";
    displayText = '<input type="text" class="textinput" id="' + obj.id + '_input" size="15" onKeyPress="keyInTextInput(event,'+obj.id+')" onFocus="focusCellbgcolor()" onBlur="blurCellbgcolor()" value="' + obj.oldValue + '" />';
    displayText += '<img class="yes" onClick="yesTextInput(' + obj.id +')" src="resources/img_trans.gif" width="1" height="1" />';
    displayText += '<img class="no" onClick="noTextInput(' + obj.id + ')" src="resources/img_trans.gif" width="1" height="1" />';

    obj.innerHTML = displayText;
    document.getElementById(obj.id + '_input').focus();

}

function yesTextInput(obj) {
    var newValue = document.getElementById(obj.id + '_input').value;
    obj.innerHTML = newValue;
    isEditing.setItem(obj.id, false);
    obj.parentElement.title = 'Double click to edit';
}

function noTextInput(obj) {
    obj.innerHTML = obj.oldValue;
    isEditing.setItem(obj.id, false);
    obj.parentElement.title = 'Double click to edit';
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


function focusCellbgcolor() {
    document.getElementById(event.srcElement.id).style.background = 'yellow';
}

function blurCellbgcolor() {
    document.getElementById(event.srcElement.id).style.background = 'white';
}


function collapseIt(obj) {
    obj.hiddenValue = obj.innerHTML;
    var displayText = '<span class="collapseExpand" title="Expand" onClick="expandIt(' + obj.id + ')">&#9660;</span>&nbsp;...';
    obj.innerHTML = displayText;
}

function expandIt(obj) {
    obj.innerHTML = obj.hiddenValue;
}

function getSelectInput(obj, list) {

    if (isEditing.getItem(obj.id)) {
        return;
    }
    isEditing.setItem(obj.id, true);
    obj.oldValue = obj.innerHTML;
    obj.parentElement.title = "";

    var displayText = '<select id="' + obj.id + '_select" >';
    for (ii = 0; ii < list.length; ii++) {
        if (obj.oldValue == list[ii])
            displayText += '<option selected="yes">' + list[ii] + '</option>';
        else
            displayText += '<option>' + list[ii] + '</option>';
    }
    displayText += '<select>';

    displayText += '<img class="yes" onClick="yesSelectInput(' + obj.id + ')" src="resources/img_trans.gif" width="1" height="1" />';
    displayText += '<img class="no" onClick="noSelectInput(' + obj.id + ')" src="resources/img_trans.gif" width="1" height="1" />';

    obj.innerHTML = displayText;
    document.getElementById(obj.id + '_select').focus();
}


function yesSelectInput(obj) {
    theSelector = document.getElementById(obj.id + '_select');
    var newValue = theSelector.options[theSelector.selectedIndex].text;
    obj.innerHTML = newValue;
    isEditing.setItem(obj.id, false);
    obj.parentElement.title = "Double click to edit";
}

function noSelectInput(obj) {
    obj.innerHTML = obj.oldValue;
    isEditing.setItem(obj.id, false);
    obj.parentElement.title = "Double click to edit";
}






function fade() {
    mainEditArea.hiddenValue = mainEditArea.innerHTML;
    
    $fx('#mainEditArea').fxAdd({type: 'opacity', from: 100, to:1, step: -5, delay:10}).fxRun(null,1);
}






/*
RUN Program on Local client machine
<script> 
function go()
{
w = new ActiveXObject("WScript.Shell");
w.run('notepad.exe');
return true;
} 
</script>


<form>
Run Notepad (Window with explorer only)
<input type="button" value="Go" onClick="return go()">
</form>


*/