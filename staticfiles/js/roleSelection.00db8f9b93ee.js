function selectOption(optionId) {
    // Get the input elements
    let regularUserInput = document.getElementById('regularUser');
    let adminInput = document.getElementById('admin');

    // Get the option elements
    let regularUserOption = regularUserInput.parentElement;
    let adminOption = adminInput.parentElement;

    // Reset styles
    regularUserOption.classList.remove('selected');
    adminOption.classList.remove('selected');

    // Check and style the selected option
    if (optionId === 'regularUser') {
        regularUserInput.checked = true;
        regularUserOption.classList.add('selected');
    } else {
        adminInput.checked = true;
        adminOption.classList.add('selected');
    }

    // Enable the submit button
    let submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = false;
}