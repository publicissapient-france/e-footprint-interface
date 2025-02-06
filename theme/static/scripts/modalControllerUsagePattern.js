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
                            <button type="button" class="btn btn-primary rounded-pill w-100" id="save_time_series_btn" data-bs-dismiss="modal" onclick="checkAttributes('`+ attributeName +`')">
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
    if (usagePatternAttribute === 'timeseries') {
        document.getElementById('date_hourly_usage_journey_starts').value = document.getElementById('timeframe_start_date').value;
        document.getElementById('list_hourly_usage_journey_starts').value = window.timeseriesToSave['hourlyvariationsValues'].toString();
    } else {
        document.getElementById(usagePatternAttribute).value = document.getElementById('form-select-' + usagePatternAttribute).value;
    }
    if (document.getElementById(usagePatternAttribute + '-icon-check').classList.contains('d-none')) {
        document.getElementById(usagePatternAttribute + '-icon-check').classList.remove('d-none');
    }
}
