let editor;
let baseUrl;
let csrfToken;
let nbObjectsAtDepth = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0};
let movedNodes = [];


function removeNode(nodeId) {
    editor.removeNodeId(`node-${nodeId}`);
}

function organizeChildren(nodeId, depth) {
    if (editor.getNodeFromId(nodeId).outputs.output_1) {
        const connections = editor.getNodeFromId(nodeId).outputs.output_1.connections;

        connections.forEach((connection, index) => {
            const nodeId = connection["node"];
            if (!movedNodes.includes(nodeId)){
                const x = 500 * (nbObjectsAtDepth[depth]);
                const y = 300 * depth;
                moveNode(nodeId, x, y);
                movedNodes.push(nodeId);
                nbObjectsAtDepth[depth] += 1;
            }
            organizeChildren(nodeId, depth + 1);
        });
    }
}

function rearrangeNodes() {
    movedNodes = [];
    editor.getNodesFromName("UsagePattern").forEach((nodeId, index) => {
        const x = 300 * (index + 1);
        const y = 5;
        moveNode(nodeId, x, y);
        organizeChildren(nodeId, 1);
        nbObjectsAtDepth[0] += 1;
    });
}

function moveNode(nodeId, x, y) {
    editor.drawflow.drawflow.Home.data[nodeId].pos_x = x;
    editor.drawflow.drawflow.Home.data[nodeId].pos_y = y;

    document.getElementById(`node-${nodeId}`).style.left = `${x}px`;
    document.getElementById(`node-${nodeId}`).style.top = `${y}px`;
    editor.updateConnectionNodes(`node-${nodeId}`);
}

function getObjectInputsAndDefaultValues() {
    return fetch("/static/object_inputs_and_default_values.json").then((data) => data.json());
}

document.body.addEventListener("insertNewNode", function(evt){
    editor.last_event_origin = "server";
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
    editor.last_event_origin = "server";
    removeNode(evt.detail["nodeId"]);
})

document.body.addEventListener("editConnections", function(evt){
    editor.last_event_origin = "server";
    evt.detail["connectionsToAdd"].forEach(function(connectionToAdd){
        editor.addConnection(evt.detail["editedNode"], connectionToAdd, "output_1", "input_1");
    });
    evt.detail["connectionsToRemove"].forEach(function(connectionToRemove){
        editor.removeSingleConnection(evt.detail["editedNode"], connectionToRemove, "output_1", "input_1");
    });
})

document.body.addEventListener("mouseup", function (e) {
        editor.last_event_origin = "drawflow";
    });

async function init(baseUrlParam, csrfTokenParam) {
    baseUrl = baseUrlParam;
    csrfToken = csrfTokenParam;
    const jsonContainer = document.getElementById("json-data");
    const jsonContextData = JSON.parse(jsonContainer.textContent);
    const id = document.getElementById("drawflow");
    const object_inputs_and_default_values_json = await getObjectInputsAndDefaultValues();

    editor = new Drawflow(id);
    editor.curvature = 0;
    editor.zoom_value = 0.05;
    editor.start();
    editor.import(jsonContextData);
    htmx.process(id);
    _hyperscript.processNode(id);

    rearrangeNodes();
    editor.zoom = 0.6;
    editor.zoom_refresh();
    editor.precanvas.style.transform = "translate(0px, -150px) scale("+editor.zoom+")"
    editor.last_event_origin = "drawflow";

    editor.on("connectionCreated", function (e){
       if (editor.last_event_origin == "drawflow"){
           editor.removeSingleConnection(e["output_id"], e["input_id"], "output_1", "input_1");
           alert("The connection you just drew is going to be deleted. Please use edit buttons to create connections.");
       }
    });
}
