// LEADERLINE

const dictLeaderLineOption = {
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

let allLines=[];

let oneRemValue = parseFloat(getComputedStyle(document.documentElement).fontSize);
let startElementWidth = 1
let startElementHeight = 1


function updateLines() {
    Object.values(allLines).forEach(lineArray => {
        lineArray.forEach(line => {
            line.position();
        });
    });
}

function removeAllLinesDepartingFromElement(elementId) {
    if (allLines[elementId]) {
        allLines[elementId].forEach( line => line.remove());
        delete allLines[elementId];
    }
}

function removeAllLinesArrivingAtElement(elementId) {
    Object.keys(allLines).forEach(key => {
        allLines[key] = allLines[key].filter(line => {
            if (line.end.id === elementId) {
                line.remove();
                return false; // Remove this line from the array
            }
            return true; // Keep this line in the array
        });
    });
}

function removeAllLines() {
    Object.values(allLines).forEach(lineArray => {
        lineArray.forEach(line => line.remove());
    });
    allLines = [];
}

function updateOrCreateLines(element) {

    function drawLines(fromElement) {
        const linkedIds = fromElement.dataset.linkTo?.split('|') || [];
        linkedIds.forEach(toElementId => {
            if (!allLines[fromElement.id]) {
                allLines[fromElement.id] = [];
            }
            const existingLine = allLines[fromElement.id].find(line => line.end.id === toElementId);
            if (!existingLine) {
                const toElement = document.getElementById(toElementId);
                if (toElement) {
                    let optLine = fromElement.getAttribute('data-line-opt');
                    let line = null
                    if(optLine ==='object-to-object-inside-card'){
                        startElementWidth = fromElement.offsetWidth;
                        startElementHeight = fromElement.offsetHeight;
                        line = new LeaderLine(
                            LeaderLine.pointAnchor(
                                fromElement, {x: (startElementWidth + oneRemValue), y: (startElementHeight/2)}),
                            toElement, dictLeaderLineOption[optLine]
                        );
                    } else if (optLine ==='step-dot-line'){
                        startElementWidth = toElement.offsetWidth;
                        startElementHeight = toElement.offsetHeight;
                        line = new LeaderLine(
                            fromElement,
                            LeaderLine.pointAnchor(
                                toElement, {x: (startElementWidth/2), y: (-oneRemValue/2)}
                            ),
                            dictLeaderLineOption[optLine]
                        );
                    }
                    else{
                        line = new LeaderLine(fromElement, toElement, dictLeaderLineOption[optLine]);
                    }
                    allLines[fromElement.id].push(line);
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
            // Handle user journey step circles
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
        updateOrCreateLines(document.getElementById(topParentId));
    });
    updateLines();
});

document.body.addEventListener('setAccordionListeners', function (event) {
    event.detail['accordionIds'].forEach(accordionId => {
        addAccordionListener(document.getElementById(accordionId));
    });
});

document.body.addEventListener('initLeaderLines', function (event) {
    initLeaderLines();
});

// ------------------------------------------------------------
// SORTABLE
document.addEventListener("DOMContentLoaded", function () {
    const upList = new Sortable(document.getElementById("up-list"), {
        animation: 150,
        onEnd: updateLines
    });

    const ujList = new Sortable(document.getElementById("uj-list"), {
        animation: 150,
        onEnd: updateLines
    });

    const serverList = new Sortable(document.getElementById("server-list"), {
        animation: 150,
        onEnd: updateLines
    });
});

// ------------------------------------------------------------
// User interaction

function closePanel() {
    const formPanel = document.getElementById('formPanel');
    formPanel.innerHTML = '';
}

function reverseIconAccordion(objectId){
    let icon = document.getElementById('icon_accordion_'+objectId);
    if (icon.classList.contains('chevron-rotate')) {
        icon.classList.remove('chevron-rotate');
    }
    else {
        icon.classList.add('chevron-rotate');
    }
    updateLines();
}

let resizeTimeout;

window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        removeAllLines();
        initLeaderLines();
    }, 100);
});

document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(".card")
    cards.forEach(card => {
        card.addEventListener("mouseover", function () {
            updateLines();
        });
        card.addEventListener("mouseout", function () {
            updateLines();
        });
    });
});

window.addEventListener("load", function () {
    setTimeout(() => {
        initLeaderLines();
    }, 100);
});
