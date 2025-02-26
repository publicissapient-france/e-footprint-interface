function initSortableObjectCards() {
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
}

function initModelBuilderMain() {
    initLeaderLines();
    initSortableObjectCards();
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
