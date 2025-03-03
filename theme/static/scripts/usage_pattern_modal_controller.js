function copyTimeSeriesValueAndDisplayIcon() {
    let modalElement = document.getElementById('usage-pattern-attributes-modal-timeseries');
    let modalInstance = bootstrap.Modal.getInstance(modalElement);
    let backdrop = document.querySelector('.modal-backdrop');
    window.chart.destroy();
    window.charts = null;
    document.getElementById('timeSeriesChart').innerHTML = '';
    if (modalInstance) {
        modalInstance.hide();
        backdrop.remove();
    }
    let btnAddTimeSeries = document.getElementById('add-time-series-btn');
    btnAddTimeSeries.innerHTML =`
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
             className="bi bi-check-circle" viewBox="0 0 16 16">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
            <path
                d="m10.97 4.97-.02.022-3.473 4.425-2.093-2.094a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05"/>
        </svg>
        Add Time Series
    `;
    cleanModal();
}

function cleanModal() {
    let modalElement = document.getElementById('usage-pattern-attributes-modal-timeseries');
    let modalInstance = bootstrap.Modal.getInstance(modalElement);
    let backdrop = document.querySelector('.modal-backdrop');
    if (modalInstance) {
        modalInstance.hide();
    }
    if(backdrop) {
        backdrop.remove();
    }
    modalElement.remove();
}
