

function readBdeSettings() {

    var settingsTemplate
    //settingsTemplate = new ActiveXObject("Msxml2.DOMDocument.3.0")
    settingsTemplate = new ActiveXObject("Microsoft.XMLDOM")
    settingsTemplate.async = false
    settingsTemplate.load("bdesettings.xml")


    nodeBdeSettings = settingsTemplate.documentElement

    nodeHeader = nodeBdeSettings.getElementsByTagName("Header")[0]

   

    displayText = nodeBdeSettings.firstChild.firstChild.firstChild.firstChild.nodeValue

    other = nodeHeader.nodeName


    nodeClientName = nodeBdeSettings.firstChild.firstChild.firstChild.firstChild
    nodeClientName.nodeValue = "Changed"

    settingsTemplate.save("new.xml")

    clientName.innerHTML = displayText + other

}