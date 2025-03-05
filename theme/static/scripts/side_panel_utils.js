function openSidePanel() {
    let modelCanva = document.getElementById("model-canva");
    let formPanel = document.getElementById("formPanel");
    modelCanva.classList.replace("col-12", "col-9");
    formPanel.classList.replace("d-none", "col-3");
    updateLines();
}

function closeAndEmptySidePanel() {
    let modelCanva = document.getElementById("model-canva");
    let formPanel = document.getElementById("formPanel");
    modelCanva.classList.replace("col-9", "col-12");
    formPanel.classList.replace("col-3", "d-none");
    formPanel.innerHTML = "";
    closeTimeseriesChart();
    updateLines();
}

document.addEventListener('click', function(event) {
    if(event.target.closest('[hx-target="#formPanel"]')){
        openSidePanel();
    }
});
