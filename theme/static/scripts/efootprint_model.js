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

function reverse_icon_accordion(object_id){
    let icon = document.getElementById('icon_accordion_'+object_id);
    if (icon.classList.contains('chevron-rotate')) {
        icon.classList.remove('chevron-rotate');
    }
    else {
        icon.classList.add('chevron-rotate');
    }
}


function createLines(element) {
    let link_to_objets = element.getAttribute('data-link-to');
    for (let link_to of link_to_objets.split('|')) {
        let opt_line = element.getAttribute('data-line-opt');
        const endElem = document.getElementById(link_to);
        let line = new LeaderLine(element, endElem, dict_leaderline_option[opt_line]);
        allLines.push(line);
    }
}

function removeLiveLines(element) {
    Object.keys(allLines).forEach(key => {
        let line = allLines[key];
        if (line.start.id === element.id ) {
            line.remove();
            delete allLines[key];
        }
    });
}

function updateLines() {
    Object.values(allLines).forEach(line => {
        line.position();
    });
}

const scrollContainer = document.querySelector('#model-canva');
scrollContainer.addEventListener('scroll', updateLines);

function closePanel() {
    const formPanel = document.getElementById('formPanel');
    formPanel.innerHTML = '';
}

document.addEventListener("htmx:oobAfterSwap", function (event) {
    Object.keys(allLines).forEach(key => {
        allLines[key].remove();
        delete allLines[key];
    });
    initLeaderLines();
    updateLines();
    addAccordionListener(event.target);
});

function showLinesAccordionOpening(accordion) {
    removeLiveLines(accordion);
    let allLeaderLineChildren = document.querySelectorAll('#'+accordion.id+" .leader-line-object");
    allLeaderLineChildren.forEach(leaderLineChild => {
        let parent_accordion = leaderLineChild.closest('.accordion-collapse');
        if(parent_accordion.classList.contains('show')){
            if(leaderLineChild.querySelectorAll(".leader-line-object").length > 0){
                if(leaderLineChild.querySelectorAll('#'+leaderLineChild.id+" .leader-line-object").length > 0) {
                    if (
                        document.getElementById('flush-' + leaderLineChild.id) !== null
                        && document.getElementById('flush-' + leaderLineChild.id).classList.contains('show')
                    ){
                        showLinesAccordionOpening(leaderLineChild);
                    } else {
                        createLines(leaderLineChild);
                    }
                }
            }else{
                createLines(leaderLineChild);
            }
        }
    });
    updateLines();
}

function showLinesAccordionClosed(accordion , init_accordion) {
    let allLeaderLineChildren = document.querySelectorAll('#'+accordion.id+" .leader-line-object");
    allLeaderLineChildren.forEach(leaderLineChild => {
        removeLiveLines(leaderLineChild);
        if(leaderLineChild.querySelectorAll('#'+leaderLineChild.id+" .leader-line-object").length > 0){
           showLinesAccordionClosed(leaderLineChild, init_accordion);
        }
    });
    if(accordion === init_accordion){
        createLines(accordion);
    }
    updateLines()
}

function addAccordionListener(accordion){
    accordion.addEventListener('shown.bs.collapse', function (event) {
        event.stopPropagation();
        let obj_type = accordion.getAttribute('data-object-type')
        if (!object_type_to_exclude.includes(obj_type)) {
            showLinesAccordionOpening(accordion);
        }
        updateLines();
    });
    accordion.addEventListener('hidden.bs.collapse', function (event) {
        event.stopPropagation();
        let obj_type = accordion.getAttribute('data-object-type')
        if (!object_type_to_exclude.includes(obj_type)) {
            showLinesAccordionClosed(accordion, accordion);
        }
        updateLines();
});
}

document.querySelectorAll('.accordion').forEach((accordion) => {
    addAccordionListener(accordion);
});

function getLeaderLineObjects() {
    let elements = document.querySelectorAll('.leader-line-object');
    elements.forEach(element => {
        let object_type = element.getAttribute('data-object-type');
        if (!object_type_to_exclude.includes(object_type)) {
            let accordionParent = element.closest('.accordion-collapse');
            if (accordionParent) {
                if (accordionParent.classList.contains('show')) {
                    createLines(element);
                }
            }
        }else{
             createLines(element);
        }
    });
}

function initLeaderLines() {
    getLeaderLineObjects();
}

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
