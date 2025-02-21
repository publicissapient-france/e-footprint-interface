function openModalUsagePattern(attributeName) {
    let modalContainer = document.getElementById('modal-container');
    let optionContent = null;
    window.modalContent[attributeName]['data'].forEach((option) => {
        if(optionContent == null){
            optionContent = `<option value="`+ option['efootprint_id'] +`">`+ option['name'] +`</option>`;
        }else{
            optionContent += `<option value="`+ option['efootprint_id'] +`">`+ option['name'] +`</option>`;
        }
    });
    let htmlContentModal = `
        <div class="modal usage-pattern-modal-attributes fade" id="usage-pattern-attributes-modal-`+ attributeName +`" tabindex="-1" aria-labelledby="usage-pattern-attributes-modal-`+ attributeName +`" aria-hidden="true" data-bs-backdrop="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-body">
                        <div class="form-header text-start">
                            <h5 id="formModalLabel" class="mt-4">
                                <b>Edit `+ window.modalContent[attributeName]['name'] +`</b>
                            </h5>
                        </div>
                        <div class="form-body">
                            <div class="">
                                <label for="form-select-`+ attributeName +`" class="form-label w-100 text-start fz-0-8">User Journey</label>
                                <select class="form-select light-select fz-0-8 h-30"  id="form-select-`+ attributeName +`"  name="form-select-`+ attributeName +`" >
                                    `+ optionContent +`
                                </select>
                            </div>
                        </div>
                        <div class="form-footer mt-5 px-3 d-grid gap-2">
                            <button type="button" class="btn btn-primary rounded-pill w-100" id="save-`+attributeName+`-attributes-btn" data-bs-dismiss="modal" onclick="checkAttributes('`+ attributeName +`')">
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `
    modalContainer.innerHTML = htmlContentModal;
    let modalElement = document.getElementById("usage-pattern-attributes-modal-"+ attributeName);
    let modal = new bootstrap.Modal(modalElement);
    modal.show();
}

function checkAttributes(usagePatternAttribute) {
    let modalElement = document.getElementById('usage-pattern-attributes-modal-' + usagePatternAttribute);
    let modalInstance = bootstrap.Modal.getInstance(modalElement);
    let backdrop = document.querySelector('.modal-backdrop');

    if (usagePatternAttribute === 'timeseries') {
        document.getElementById('date_hourly_usage_journey_starts').value = document.getElementById('modal_timeframe_start_date').value;
        document.getElementById('list_hourly_usage_journey_starts').value = window.variationsValues.toString();
        document.getElementById('timeframe_start_date').value = window.formValues['modal_timeframe_start_date'].value;
        document.getElementById('net_growth_rate_period').value = window.formValues['modal_net_growth_rate_period'].value;
        document.getElementById('net_growth_rate_value').value = window.formValues['modal_net_growth_rate_value'].value;
        document.getElementById('avg_nb_usage_journey_value').value = window.formValues['modal_avg_nb_usage_journey_value'].value;
        document.getElementById('avg_nb_usage_journey_period').value = window.formValues['modal_avg_nb_usage_journey_period'].value;
        document.getElementById('timeframe_value').value = window.formValues['modal_timeframe_value'].value;
        document.getElementById('timeframe_range').value = window.formValues['modal_timeframe_range'].value;
        window.charts['timeSeriesChart'].destroy();
        window.charts['timeSeriesChart'] = null;
        document.getElementById('timeSeriesChart').innerHTML = '';
        if (modalInstance) {
            modalInstance.hide();
            backdrop.remove();
        }
    } else {
        document.getElementById(usagePatternAttribute).value = document.getElementById('form-select-' + usagePatternAttribute).value;
        modalInstance.hide();
        modalElement.remove();
        if (backdrop) {
            backdrop.remove();
        }
    }
    if (document.getElementById(usagePatternAttribute + '-icon-check').classList.contains('d-none')) {
        document.getElementById(usagePatternAttribute + '-icon-check').classList.remove('d-none');
    }
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
