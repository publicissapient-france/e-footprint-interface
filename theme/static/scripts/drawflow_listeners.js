document.body.addEventListener("insertNewNode", function(evt){
    editor.lastEventOrigin = "server";
    let drawflowData = evt.detail["drawflowData"];
    editor.addNode(
        drawflowData["name"], 1, 1, 100, 100, drawflowData["class"], drawflowData["data"], drawflowData["html"]);
    let addedHtmlElement = document.getElementById(drawflowData['html_block_id']);
    htmx.process(addedHtmlElement);
    _hyperscript.processNode(addedHtmlElement);
    if (Object.keys(drawflowData.outputs).length > 0) {
        drawflowData.outputs.output_1.connections.forEach(connection => {
            editor.addConnection(drawflowData["id"], connection.node, "output_1", "input_1");
        });
    }
    if (Object.keys(drawflowData.inputs).length > 0) {
        drawflowData.inputs.input_1.connections.forEach(connection => {
            editor.addConnection(connection.node, drawflowData["id"], "output_1", "input_1");
        });
    }
})

document.body.addEventListener("deleteNode", function(evt){
    editor.lastEventOrigin = "server";
    removeNode(evt.detail["nodeId"]);
})

document.body.addEventListener("editConnections", function(evt){
    editor.lastEventOrigin = "server";
    evt.detail["connectionsToAdd"].forEach(function(connectionToAdd){
        editor.addConnection(evt.detail["editedNode"], connectionToAdd, "output_1", "input_1");
    });
    evt.detail["connectionsToRemove"].forEach(function(connectionToRemove){
        editor.removeSingleConnection(evt.detail["editedNode"], connectionToRemove, "output_1", "input_1");
    });
})

document.body.addEventListener("mouseup", function (e) {
        editor.lastEventOrigin = "drawflow";
    });
