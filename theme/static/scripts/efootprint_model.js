// ------------------------------------------------------------
// LEADERLINE

const object_type_to_exclude = ["UsagePattern","Server"];
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
        endSocket: "left",
        showEffectName: 'fade',
        dash: true
    }
};

let allLines=[];

function updateLines() {
    Object.values(allLines).forEach(lineArray => {
        lineArray.forEach(line => {
            line.position();
        });
    });
}

const scrollContainer = document.querySelector('#model-canva');
scrollContainer.addEventListener('scroll', updateLines);

function removeLines(elementId) {
    if (allLines[elementId]) {
        allLines[elementId].forEach( line => line.remove());
        delete allLines[elementId];
    }
}

function updateOrCreateLines(element) {
    const elementId = element.id;

    function drawLines(fromElement) {
        const linkedIds = element.dataset.linkTo?.split('|') || [];
        linkedIds.forEach(toElementId => {
            if (!allLines[fromElement.id]) {
                allLines[fromElement.id] = [];
            }
            const existingLine = allLines[fromElement.id].find(line => line.end.id === toElementId);
            if (!existingLine) {
                const toElement = document.getElementById(toElementId);
                if (toElement) {
                    let opt_line = fromElement.getAttribute('data-line-opt');
                    const line = new LeaderLine(fromElement, toElement, dict_leaderline_option[opt_line]);
                    allLines[fromElement.id].push(line);
                }
            }
        });
    }

    function getDirectLeaderLineChildren(parent) {
        return Array.from(parent.querySelectorAll('.leader-line-object'))
            .filter(child => child.parentElement.closest('.leader-line-object') === parent);
    }

    if (element.classList.contains('accordion')) {
        const accordion_collapse = document.getElementById("flush-" + elementId);
        let isOpen =  accordion_collapse.classList.contains('show');
        if (!isOpen) {
            drawLines(element);
            const childElements = element.querySelectorAll('.leader-line-object');
            childElements.forEach(child => removeLines(child.id));
        } else {
            const childElements = getDirectLeaderLineChildren(element);
            if (childElements.length > 0) {
                removeLines(elementId);
                childElements.forEach(child => updateOrCreateLines(child));
            } else {
                drawLines(element);
            }
        }
    } else {
        drawLines(element);
    }
}

document.addEventListener("htmx:oobAfterSwap", function (event) {
    updateOrCreateLines(event.target);
    updateLines();
    addAccordionListener(event.target);
});

function addAccordionListener(accordion){
    accordion.addEventListener('shown.bs.collapse', function () {
        updateOrCreateLines(accordion);
        updateLines();
    });
    accordion.addEventListener('hidden.bs.collapse', function () {
        updateOrCreateLines(accordion);
        updateLines();
    });
    accordion.addEventListener('hide.bs.collapse', function (event) {
        event.stopPropagation();
        const childElements = accordion.querySelectorAll('.leader-line-object');
        childElements.forEach(child => removeLines(child.id));
    });
}

function initLeaderLines() {
    let accordions = document.querySelectorAll('.accordion');
    accordions.forEach(accordion => {
        let accordionParent = accordion.parentElement.closest('.accordion');
        if (accordionParent == null) {
            updateOrCreateLines(accordion);
        }
    });
}

document.querySelectorAll('.accordion').forEach(accordion => {
    addAccordionListener(accordion);
});

document.addEventListener("DOMContentLoaded", function () {
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
}
