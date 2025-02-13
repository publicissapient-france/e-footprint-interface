// LEADERLINE

window.dictLeaderLineOption = {
    'object-to-object': {
        color: "#9CA3AF",
        size: 1,
        startPlug: 'disc',
        endPlug: 'disc',
        startPlugColor: "#E5E7EB",
        endPlugColor: "#E5E7EB",
        startPlugSize: 5,
        endPlugSize: 5,
        startSocket: "right",
        endSocket: "left",
        showEffectName: 'fade'
    },
    'object-to-object-inside-card': {
        color: "#9CA3AF",
        size: 1,
        startPlug: 'disc',
        endPlug: 'disc',
        startPlugColor: "#E5E7EB",
        endPlugColor: "#E5E7EB",
        startPlugSize: 5,
        endPlugSize: 5,
        startSocket: "right",
        endSocket: "left",
        showEffectName: 'fade'
    },
    'vertical-step-swimlane': {
        path: 'straight',
        color: "#003235",
        size: 3,
        startPlug: 'behind',
        endPlug: 'behind',
        startSocket: "bottom",
        endSocket: "top",
        showEffectName: 'fade'
    },
    "step-dot-line": {
        path: 'straight',
        color: "#003235",
        size: 3,
        startPlug: 'behind',
        endPlug: 'behind',
        startSocket: "bottom",
        endSocket: "top",
        showEffectName: 'fade',
        dash: true
    }
};

window.allLines=[];

window.oneRemValue = parseFloat(getComputedStyle(document.documentElement).fontSize);
window.startElementWidth = 1
window.startElementHeight = 1


function updateLines() {
    Object.values(window.allLines).forEach(lineArray => {
        lineArray.forEach(line => {
            line.position();
        });
    });
}

function removeAllLinesDepartingFromElement(elementId) {
    if (window.allLines[elementId]) {
        window.allLines[elementId].forEach( line => line.remove());
        delete window.allLines[elementId];
    }
}

function removeAllLinesArrivingAtElement(elementId) {
    Object.keys(window.allLines).forEach(key => {
        window.allLines[key] = window.allLines[key].filter(line => {
            if (line.end.id === elementId) {
                line.remove();
                return false; // Remove this line from the array
            }
            return true; // Keep this line in the array
        });
    });
}

function removeAllLines() {
    Object.values(window.allLines).forEach(lineArray => {
        lineArray.forEach(line => line.remove());
    });
    window.allLines = [];
}

function updateOrCreateLines(element) {

    function drawLines(fromElement) {
        const linkedIds = fromElement.dataset.linkTo?.split('|') || [];
        linkedIds.forEach(toElementId => {
            if (!window.allLines[fromElement.id]) {
                window.allLines[fromElement.id] = [];
            }
            const existingLine = window.allLines[fromElement.id].find(line => line.end.id === toElementId);
            if (!existingLine) {
                const toElement = document.getElementById(toElementId);
                if (toElement) {
                    let optLine = fromElement.getAttribute('data-line-opt');
                    let line = null
                    if(optLine ==='object-to-object-inside-card'){
                        window.startElementWidth = fromElement.offsetWidth;
                        window.startElementHeight = fromElement.offsetHeight;
                        line = new LeaderLine(
                            LeaderLine.pointAnchor(
                                fromElement, {x: (window.startElementWidth + window.oneRemValue), y: (window.startElementHeight/2)}),
                            toElement, window.dictLeaderLineOption[optLine]
                        );
                    } else if (optLine ==='step-dot-line'){
                        window.startElementWidth = toElement.offsetWidth;
                        window.startElementHeight = toElement.offsetHeight;
                        line = new LeaderLine(
                            fromElement,
                            LeaderLine.pointAnchor(
                                toElement, {x: (window.startElementWidth/2), y: (-window.oneRemValue/2)}
                            ),
                            window.dictLeaderLineOption[optLine]
                        );
                    }
                    else{
                        line = new LeaderLine(fromElement, toElement, window.dictLeaderLineOption[optLine]);
                    }
                    window.allLines[fromElement.id].push(line);
                }
            }
        });
    }

    function getDirectLeaderLineChildren(parent) {
        return Array.from(parent.querySelectorAll('.leader-line-object'))
            .filter(child => child.parentElement.closest('.leader-line-object') === parent);
    }

    const elementId = element.id;
    let accordionCollapse = document.getElementById("flush-" + elementId);
    if (accordionCollapse) {
        let isOpen = accordionCollapse.classList.contains('show');
        if (isOpen) {
            const childElements = getDirectLeaderLineChildren(element);
            if (childElements.length > 0) {
                removeAllLinesDepartingFromElement(elementId);
                childElements.forEach(child => updateOrCreateLines(child));
            } else {
                drawLines(element);
            }
            // Handle usage journey step circles
            const imgLeaderLineChildren = element.querySelectorAll('img.leader-line-object');
            imgLeaderLineChildren.forEach(child => drawLines(child));
        }
        else {
            drawLines(element);
            const childElements = element.querySelectorAll('.leader-line-object');
            childElements.forEach(child => removeAllLinesDepartingFromElement(child.id));
        }
    } else {
        drawLines(element);
    }
}

function addAccordionListener(accordion){
    accordion.addEventListener('shown.bs.collapse', function () {
        let closestLeaderlineObject = accordion.closest('.leader-line-object');
        if (closestLeaderlineObject) {
            updateOrCreateLines(closestLeaderlineObject);
        }
        updateLines();
    });
    accordion.addEventListener('hidden.bs.collapse', function () {
        let closestLeaderlineObject = accordion.closest('.leader-line-object');
        if (closestLeaderlineObject) {
            updateOrCreateLines(closestLeaderlineObject);
        }
        updateLines();
    });
    accordion.addEventListener('hide.bs.collapse', function (event) {
        event.stopPropagation();
        const childElements = accordion.querySelectorAll('.leader-line-object');
        childElements.forEach(child => removeAllLinesDepartingFromElement(child.id));
    });
}

function initLeaderLines() {
    let leaderLineObjects = document.querySelectorAll('.leader-line-object');
    leaderLineObjects.forEach(leaderLineObject => {
        let leaderLineObjectParent = leaderLineObject.parentElement.closest('.leader-line-object');
        if (leaderLineObjectParent == null) {
            updateOrCreateLines(leaderLineObject);
        }
    });
    document.querySelectorAll('.accordion').forEach(accordion => {
        addAccordionListener(accordion);
    });
    const scrollContainer = document.querySelector('#model-canva');
    scrollContainer.addEventListener('scroll', updateLines);
    updateLines();
}

// ------------------------------------------------------------
// HTMX AFTER SWAP

document.body.addEventListener('removeLinesAndUpdateDataAttributes', function (event) {
    event.detail['elementIdsOfLinesToRemove'].forEach(elementIdWithLinesToRemove => {
        removeAllLinesDepartingFromElement(elementIdWithLinesToRemove);
        removeAllLinesArrivingAtElement(elementIdWithLinesToRemove);
        let leaderlineObjectChildren = document.getElementById(elementIdWithLinesToRemove)
            .querySelectorAll('.leader-line-object');
        leaderlineObjectChildren.forEach(leaderlineObjectChild => {
            removeAllLinesDepartingFromElement(leaderlineObjectChild.id);
            removeAllLinesArrivingAtElement(leaderlineObjectChild.id);
        });
    });
    event.detail['dataAttributeUpdates'].forEach(dataAttributeUpdate => {
        let element = document.getElementById(dataAttributeUpdate['id']);
        if (element) {
            element.setAttribute('data-link-to', dataAttributeUpdate['data-link-to']);
            if (dataAttributeUpdate['data-line-opt'] !== '') {
                element.setAttribute('data-line-opt', dataAttributeUpdate['data-line-opt']);
            }
            removeAllLinesDepartingFromElement(dataAttributeUpdate['id']);
        }
    });
});

document.body.addEventListener('updateTopParentLines', function (event) {
    event.detail['topParentIds'].forEach(topParentId => {
        let card = document.getElementById(topParentId);
        card.addEventListener("mouseover", function () {
            updateLines();
        });
        card.addEventListener("mouseout", function () {
            updateLines();
        });
        updateOrCreateLines(document.getElementById(topParentId));
    });
    updateLines();
});

document.body.addEventListener('setAccordionListeners', function (event) {
    event.detail['accordionIds'].forEach(accordionId => {
        addAccordionListener(document.getElementById(accordionId));
    });
});

document.body.addEventListener('closePanelAfterSwap', function (event) {
    closePanel();
});

window.initLeaderLines = initLeaderLines;


function dropModal(id){
    let modalElement = document.getElementById(id);
    let modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
        modalInstance.hide();
        modalElement.remove();
    }
    let backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
}

function dropModalUnderstand(){
    document.getElementById("open-understand-modal").focus();
}
