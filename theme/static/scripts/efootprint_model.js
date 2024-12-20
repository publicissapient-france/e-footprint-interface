// ------------------------------------------------------------
// LEADERLINE

const dict_leaderline_option = {
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

let one_rem_value = parseFloat(getComputedStyle(document.documentElement).fontSize);
let start_element_width = 1
let start_element_height = 1


function updateLines() {
    Object.values(allLines).forEach(lineArray => {
        lineArray.forEach(line => {
            line.position();
        });
    });
}

const scrollContainer = document.querySelector('#model-canva');
scrollContainer.addEventListener('scroll', updateLines);

function removeAllLinesDepartingFromElement(elementId) {
    if (allLines[elementId]) {
        allLines[elementId].forEach( line => line.remove());
        delete allLines[elementId];
    }
}

function removeAllLinesArrivingAtElement(elementId) {
    Object.values(allLines).forEach(lineArray => {
        lineArray.forEach(line => {
            if (line.end.id === elementId) {
                line.remove();
            }
            delete allLines[elementId];
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
                    let opt_line = fromElement.getAttribute('data-line-opt');
                    let line = null
                    if(opt_line ==='object-to-object-inside-card'){
                        start_element_width = fromElement.offsetWidth;
                        start_element_height = fromElement.offsetHeight;
                        line = new LeaderLine(
                            LeaderLine.pointAnchor(
                                fromElement, {x: (start_element_width +one_rem_value), y: (start_element_height/2)}),
                            toElement, dict_leaderline_option[opt_line]
                        );
                    } else if (opt_line ==='step-dot-line'){
                        start_element_width = toElement.offsetWidth;
                        start_element_height = toElement.offsetHeight;
                        line = new LeaderLine(
                            fromElement,
                            LeaderLine.pointAnchor(
                                toElement, {x: (start_element_width/2), y: (-one_rem_value/2)}
                            ),
                            dict_leaderline_option[opt_line]
                        );
                    }
                    else{
                        line = new LeaderLine(fromElement, toElement, dict_leaderline_option[opt_line]);
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
    let accordion_collapse = document.getElementById("flush-" + elementId);
    if (accordion_collapse) {
        let isOpen = accordion_collapse.classList.contains('show');
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
}

document.querySelectorAll('.accordion').forEach(accordion => {
    addAccordionListener(accordion);
});

// ------------------------------------------------------------
// HTMX AFTER SWAP

document.body.addEventListener('removeLinesAndEditDataLinkTo', function (event) {
    event.detail['listOfElementsToDeleteTheirAssociatedLines'].forEach(idToRemove => {
        removeAllLinesDepartingFromElement(idToRemove);
        removeAllLinesArrivingAtElement(idToRemove);
        let start_icon_element = document.getElementById('icon-'+idToRemove)
        if(start_icon_element){
            removeAllLinesDepartingFromElement(start_icon_element.id)
            removeAllLinesArrivingAtElement(idToRemove);
        }
    });
    event.detail['listOfElementsToUpdateDataLinkToAttribute'].forEach(idDataLinkToChange => {
        if (idDataLinkToChange && idDataLinkToChange['data-link-to']) {
            let element = document.getElementById(idDataLinkToChange['id']);
            if (element) {
                element.setAttribute('data-link-to', idDataLinkToChange['data-link-to']);
                if (idDataLinkToChange['data-line-opt'] !== '') {
                    element.setAttribute('data-line-opt', idDataLinkToChange['data-line-opt']);
                }
                removeAllLinesDepartingFromElement(idDataLinkToChange['id']);
            }
        }
    });
});

document.body.addEventListener('createOrUpdateLines', function (event) {
    event.detail['listOftopParents'].forEach(topParent => {
        updateOrCreateLines(document.getElementById(topParent));
    });
    updateLines();
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

function reverse_icon_accordion(object_id){
    let icon = document.getElementById('icon_accordion_'+object_id);
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
