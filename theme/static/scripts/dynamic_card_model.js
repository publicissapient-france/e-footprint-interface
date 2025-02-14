
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

window.resizeTimeout = null;

window.addEventListener('resize', () => {
    clearTimeout(window.resizeTimeout);
    window.resizeTimeout = setTimeout(() => {
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


