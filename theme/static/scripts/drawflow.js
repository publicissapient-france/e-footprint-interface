let editor;
let baseUrl;
let csrfToken;
let nbObjectsAtDepth = {};
let movedNodes = [];


function removeNode(nodeId) {
    editor.removeNodeId(`node-${nodeId}`);
}

function organizeChildren(nodeId, depth, yOffset) {
    if (editor.getNodeFromId(nodeId).outputs.output_1) {
        const connections = editor.getNodeFromId(nodeId).outputs.output_1.connections;

        connections.forEach((connection, index) => {
            const nodeId = connection["node"];
            if (!movedNodes.includes(nodeId)){
                const x = 400 * (nbObjectsAtDepth[depth]);
                const y = 300 * depth;
                moveNode(nodeId, x, y + yOffset);
                movedNodes.push(nodeId);
                nbObjectsAtDepth[depth] += 1;
            }
            organizeChildren(nodeId, depth + 1, yOffset);
        });
    }
}

function rearrangeNodes(yOffset) {
    movedNodes = [];
    nbObjectsAtDepth = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0};
    editor.getNodesFromName("UsagePattern").forEach((nodeId, index) => {
        const x = 300 * (index + 1);
        const y = 5;
        moveNode(nodeId, x, y + yOffset);
        organizeChildren(nodeId, 1, yOffset);
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

    rearrangeNodes(-300);
    editor.zoom = 0.6;
    editor.zoom_refresh();
    editor.lastEventOrigin = "drawflow";

    editor.on("connectionCreated", function (e){
       if (editor.lastEventOrigin == "drawflow"){
           editor.removeSingleConnection(e["output_id"], e["input_id"], "output_1", "input_1");
           alert("The connection you just drew is going to be deleted. Please use edit buttons to create connections.");
       }
    });
}
