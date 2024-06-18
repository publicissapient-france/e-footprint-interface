let editor;
let baseUrl;
let csrfToken;


function removeNode(nodeId) {
    editor.removeNodeId(`node-${nodeId}`);
}

/**
 * Fonction récursive qui prend en compte un nodeId, récupère le noeud associé ainsi que ses connexions (déscendants)
 * et les organise de façon plus visible sur le graphe en les espaçant.
 * La profondeur est augmentée et prise en compte à chaque appel de la fonction.
 * @FIXME Actuellement certaines cartes sont placées par dessus d'autres, il faudrait éviter les collisions.
 */
function organizeChildren(nodeId, depth, xStart) {
    if (editor.getNodeFromId(nodeId).outputs.output_1) {
        const connections = editor.getNodeFromId(nodeId).outputs.output_1.connections;

        connections.forEach((connection, index) => {
            const nodeId = connection["node"];
            const x = xStart + 100 * (index * 5);
            const y = 300 * depth;
            moveNode(nodeId, x, y);
            organizeChildren(nodeId, depth + 1, xStart);
        });
    }
}

/**
 * Réorganisation des noeuds en partant des UsagePattern en haut du graphe,
 * puis en descendant de manière récursive dans l'arborescence.
 */
function rearrangeNodes() {
    editor.getNodesFromName("UsagePattern").forEach((nodeId, index) => {
        const x = 300 * (index + 1);
        const y = 5;
        moveNode(nodeId, x, y);
        organizeChildren(nodeId, 1, x);
    });
}

/**
 * Déplace un noeud à partir de nouvelles positions x et y et de son nodeId.
 */
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

document.body.addEventListener("InsertNewNode", function(evt){
    let drawflowData = evt.detail["drawflowData"];
    console.log(drawflowData);
    editor.addNode(
        drawflowData["name"], 1, 1, 100, 100, drawflowData["class"], drawflowData["data"], drawflowData["html"]);
    htmx.process(document.getElementById(drawflowData["html_block_id"]));
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

    rearrangeNodes();
    editor.zoom = 0.5;
    editor.zoom_refresh();

    Array.prototype.forEach.call(document.getElementsByClassName("output"), (output) => {
        output.addEventListener("mousedown", () => displayAvailableConnections(output));
    });

    function displayAvailableConnections(output) {
        // Tous les inputs sont rouges par défaut, puis on va chercher les connexions possibles
        Array.prototype.forEach.call(document.getElementsByClassName("input"), (input) => {
            input.style.background = "red";
        });
        // Récupération du type d'objet associé à l'output sur lequel on a cliqué
        const classlist = output.parentElement.parentElement.classList;
        const objectTypeList = Array.prototype.filter.call(classlist, (objectTypeClass) =>
            Object.keys(object_inputs_and_default_values_json).includes(objectTypeClass)
        );

        if (objectTypeList.length) {
            const typeData = object_inputs_and_default_values_json[objectTypeList[0]];
            const modObjs = typeData["modeling_obj_attributes"].map((type) => type.object_type);
            const listAttributes = typeData["list_attributes"].map((type) => type.object_type);

            const targetObjectTypes = [...modObjs, ...listAttributes];
            const selectors = targetObjectTypes.map((target) => `.${target} .input`).join(",");
            Array.prototype.forEach.call(document.querySelectorAll(selectors), (input) => {
                input.style.background = "green";
            });
        }

        document.addEventListener("mouseup", () => {
            Array.prototype.forEach.call(document.getElementsByClassName("input"), (input) => {
                input.style.background = "white";
            });
        });
    }

    editor.on("nodeCreated", function (id) {
        // Lorsqu'une nouvelle carte est créée, il faut rajouter l'eventListener pour afficher les liens possibles.
        Array.prototype.forEach.call(document.querySelectorAll(`#node-${id} > .outputs > .output`), (output) => {
            output.addEventListener("mousedown", () => displayAvailableConnections(output));
        });
    });

    editor.on("connectionCreated", function (connection) {
        // L'utilisateur vient de créer un lien, mais on va s'assurer qu'il soit valide avant de l'enregistrer.
        const originNode = editor.getNodeFromId(connection.output_id);
        const destinationNode = editor.getNodeFromId(connection.input_id);

        const typeData = object_inputs_and_default_values_json[originNode.name];
        const modObjs = typeData["modeling_obj_attributes"].map((type) => type.object_type);
        const listAttributes = typeData["list_attributes"].map((type) => type.object_type);

        // Si le type d'objet de départ a le type d'objet d'arrivée dans ses attributs, on peut valider.
        if (modObjs.includes(destinationNode.name) || listAttributes.includes(destinationNode.name)) {
            const formData = new URLSearchParams();
            formData.append("parentObjectType", originNode.name);
            formData.append("childObjectType", destinationNode.name);
            formData.append("parentObjectId", originNode["data"]["id"]);
            formData.append("childObjectId", destinationNode["data"]["id"]);

            fetch(`${baseUrl}/model_builder/add-object-connection`, {
                method: "post",
                body: formData,
                credentials: "same-origin",
                headers: { "X-CSRFToken": csrfToken },
            })
                .then((response) => response.text())
                .then((responseTemplate) => {
                    // Si c'est un lien simple et qu'un lien précédant existait, on l'écrase et le remplace par le nouveau.
                    const connections = originNode.outputs["output_1"].connections;
                    const nodes = connections
                        .map((nodeData) => editor.getNodeFromId(nodeData.node))
                        .filter((node) => node.name === destinationNode.name && node.id !== destinationNode.id);

                    if (modObjs.includes(destinationNode.name)) {
                        const connections = originNode.outputs["output_1"].connections;
                        const nodes = connections
                            .map((nodeData) => editor.getNodeFromId(nodeData.node))
                            .filter((node) => node.name === destinationNode.name && node.id !== destinationNode.id)
                            .map((node) => node.id);
                        connections
                            .filter((connec) => nodes.includes(Number.parseInt(connec.node)))
                            .forEach((connec) => {
                                editor.removeSingleConnection(
                                    originNode.id,
                                    Number.parseInt(connec.node),
                                    "output_1",
                                    "input_1"
                                );
                            });
                    }
                    rearrangeNodes();
                    document.getElementById("refresh-graph-button").click();
                });
        } else {
            const connections = destinationNode.inputs[connection.input_class].connections;
            const removeConnectionInfo = connections[connections.length - 1];
            editor.removeSingleConnection(
                removeConnectionInfo.node,
                connection.input_id,
                removeConnectionInfo.input,
                connection.input_class
            );
        }
    });

    editor.on("connectionRemoved", function (connection) {
        const nodeIdA = editor.getNodeFromId(connection.output_id).data.id;
        const nodeIdB = editor.getNodeFromId(connection.input_id).data.id;
        const formData = new URLSearchParams();
        formData.append("object_id", nodeIdA);
        formData.append("objet_linked_to_remove", nodeIdB);

        fetch(`${baseUrl}/model_builder/remove-connection`, {
            method: "post",
            body: formData,
            credentials: "same-origin",
            headers: { "X-CSRFToken": csrfToken },
        })
            .then((response) => response.json())
            .then((response) => {
                console.log(response);
            });
    });
}
