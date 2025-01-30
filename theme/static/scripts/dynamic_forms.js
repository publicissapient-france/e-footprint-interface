document.addEventListener("initAddPanel", function () {
    const structureDict = JSON.parse(document.getElementById('dynamic-form-data').textContent);
  /**
   * 1) SWITCH ELEMENT LOGIC
   */
  if (structureDict.switch_item) {
    const switchElementId = "form_add_" + structureDict.switch_item;
    const switchElement = document.getElementById(switchElementId);
    let previousSwitchValue = switchElement.value;

    switchElement.addEventListener("change", function() {
      // Hide the previous group
      const itemToHide = document.getElementById("item-" + previousSwitchValue);
      itemToHide.classList.add('d-none');
      itemToHide.querySelectorAll('input, select').forEach(function(input) {
        input.required = false;
      });

      // Show the newly selected group
      const itemToShow = document.getElementById("item-" + switchElement.value);
      itemToShow.classList.remove('d-none');
      itemToShow.querySelectorAll('input, select').forEach(function(input) {
        input.required = true;
      });

      previousSwitchValue = switchElement.value;
    });
  }

  /**
   * 2) DYNAMIC LISTS LOGIC
   */

  // Define the reusable function *once*, outside the loop
  // This function populates the datalist based on the provided arguments
  function fillDataList(listValue, filterId, listId) {
    const filterElement = document.getElementById(filterId);
    const dataList = document.getElementById(listId);

    // Safety check if the elements exist
    if (!filterElement || !dataList) return;

    // Which key do we filter by?
    const filterKey = filterElement.value;

    // Clear old options
    dataList.innerHTML = '';

    // Create & append new options
    // If you'd like a default "select a configuration", you can add an <option> here
    if (listValue[filterKey]) {
      listValue[filterKey].forEach(function(item) {
        const option = document.createElement('option');
        option.value = item;
        dataList.appendChild(option);
      });
    }
  }

  // If dynamic_lists is present, iterate through them
  if (structureDict.dynamic_lists) {
    structureDict.dynamic_lists.forEach(dynamicList => {
      // Build the relevant IDs
      const filterId = "form_add_" + dynamicList.filter_by;
      const listId   = "list_" + dynamicList.input;

      // 1) Fill once on page load
      fillDataList(dynamicList.list_value, filterId, listId);

      // 2) Re-fill on change
      const filterElement = document.getElementById(filterId);
      if (filterElement) {
        filterElement.addEventListener("change", function() {
          fillDataList(dynamicList.list_value, filterId, listId);
        });
      }
    });
  }
});
