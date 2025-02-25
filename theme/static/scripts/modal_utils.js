// MODAL
document.body.addEventListener("openModalDialog", function(event) {
    let modalElement = document.getElementById("model-builder-modal");
    let modal = new bootstrap.Modal(modalElement);
    modal.show();
});

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
