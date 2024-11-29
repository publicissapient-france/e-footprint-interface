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

let allLines={};

function createLines(element) {
    let link_to_objets = element.getAttribute('data-link-to');
    let objectLines = [];
    for (let link_to of link_to_objets.split('|')) {
        let opt_line = element.getAttribute('data-line-opt');
        const endElem = document.getElementById(link_to);
        let line = new LeaderLine(element, endElem, dict_leaderline_option[opt_line]);
        objectLines.push(line);
    }
    allLines[element.id] = objectLines;
}

function initLeaderLines() {
    let elements = document.querySelectorAll('.leader-line-object');
    let type_object_to_not_init = ['Job','UserJourney']
    elements.forEach(element => {
        let objectType = element.getAttribute('data-object-type');
        if (!type_object_to_not_init.includes(objectType)) {
            createLines(element);
        }
    });
}

function updateObjectToObjectLinesUJStepAccordionOpening(ujStepAccordion) {
    allLines[ujStepAccordion.id].forEach(line => {line.remove();});
    delete allLines[ujStepAccordion.id];
    let jobs = document.querySelectorAll('#'+ujStepAccordion.id+" .accordion-collapse"+' .leader-line-object');
    jobs.forEach(job => {createLines(job);});
}

function updateObjectToObjectLinesUJStepAccordionClosing(ujStepAccordion) {
    createLines(ujStepAccordion);
    let jobs = document.querySelectorAll('#'+ujStepAccordion.id+" .accordion-collapse"+' .leader-line-object');
    jobs.forEach(job => {
        allLines[job.id].forEach(line => {line.remove();});
        delete allLines[job.id];
    });
}

function updateObjectToObjectLinesUJAccordionOpening(ujAccordion) {
    allLines[ujAccordion.id].forEach(line => line.remove());
    delete allLines[ujAccordion.id];
    let elements = document.querySelectorAll('#' + ujAccordion.id + ' .leader-line-object[data-object-type="UserJourneyStep"]');
    elements.forEach(element => {
        let collapsible = document.querySelector(`#flush-${element.id}`);
        if (collapsible && collapsible.classList.contains('show')) {
           let sub_elements = document.querySelectorAll('#' + element.id + ' .leader-line-object[data-object-type="Job"]');
            sub_elements.forEach(sub_element => {createLines(sub_element);});
        }else{
            createLines(element);
        }
    });
    elements = document.querySelectorAll('#' + ujAccordion.id + ' .leader-line-object[data-object-type="circle"]');
    elements.forEach(element => {createLines(element);});
}

function updateObjectToObjectLinesUJAccordionClosing(ujAccordion) {
    createLines(ujAccordion);
    let uj_steps = document.querySelectorAll('#'+ujAccordion.id+" .accordion-collapse"+' .leader-line-object');
    uj_steps.forEach(uj_step => {
       if (allLines[uj_step.id] !== undefined) {
           allLines[uj_step.id].forEach(line => {
               line.remove();
           });
           delete allLines[uj_step.id];
       }
    });
}

function updateLines() {
    Object.values(allLines).forEach(lineList => {
        lineList.forEach(line => {
            line.position();
        });
    });
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

document.addEventListener("DOMContentLoaded", function () {
    initLeaderLines();
});

document.querySelectorAll('.accordion').forEach((accordion) => {
    let obj = accordion.getAttribute('data-object-type')
    if (obj === "UserJourneyStep") {
        accordion.addEventListener('shown.bs.collapse', function () {
            event.stopPropagation();
            updateObjectToObjectLinesUJStepAccordionOpening(accordion);
            updateLines();
            reverse_icon_accordion(accordion.id);
        });
        accordion.addEventListener('hidden.bs.collapse', function () {
            event.stopPropagation();
            updateObjectToObjectLinesUJStepAccordionClosing(accordion);
            updateLines();
            reverse_icon_accordion(accordion.id);
        });
    } else if ( obj === "UserJourney") {
        accordion.addEventListener('shown.bs.collapse', function () {
            updateObjectToObjectLinesUJAccordionOpening(accordion);
            updateLines();
            reverse_icon_accordion(accordion.id);
        });
        accordion.addEventListener('hidden.bs.collapse', function () {
            updateObjectToObjectLinesUJAccordionClosing(accordion);
            updateLines();
            reverse_icon_accordion(accordion.id);
        });
    } else {
        accordion.addEventListener('shown.bs.collapse', function (){
            updateLines();
            reverse_icon_accordion(accordion.id);
        });
        accordion.addEventListener('hidden.bs.collapse', function (){
            updateLines();
            reverse_icon_accordion(accordion.id);
        });
    }
});

const scrollContainer = document.querySelector('#model-canva');
scrollContainer.addEventListener('scroll', updateLines);

/*
document.querySelectorAll('.right-click-target').forEach((element, index) => {
    element.addEventListener('contextmenu', function (e) {
        let id_objet = element.getAttribute('data-object-id');
        console.log('Right-click detected on:', id_objet);
    e.preventDefault();
    });
});
*/
function closePanel() {
    const formPanel = document.getElementById('formPanel');
    formPanel.innerHTML = '';
}


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
