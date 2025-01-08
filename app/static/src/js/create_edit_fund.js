function toggleWelshFields() {
    const welshAvailable = document.querySelector('input[name="welsh_available"]:checked').value;
    const welshFields = document.querySelectorAll('.welsh-field');

    welshFields.forEach(field => {
        const fieldContainer = field.closest('.govuk-form-group');
        if (welshAvailable === 'true') {
            fieldContainer.style.display = 'block';
        } else {
            fieldContainer.style.display = 'none';
        }
    });
}

// Run on page load
document.addEventListener('DOMContentLoaded', function() {
    toggleWelshFields();

    // Add change event listeners to radio buttons
    const radios = document.querySelectorAll('input[name="welsh_available"]');
    radios.forEach(radio => {
        radio.addEventListener('change', toggleWelshFields);
    });
});

// Add click event listener to save and return to home link
document.getElementById('save-return-home').addEventListener('click', function(e) {
    e.preventDefault();
    const form = document.querySelector('form');
    const dashboardUrl = document.getElementById('fund-config').dataset.dashboardUrl;
    const url = new URL(form.action);
    url.searchParams.set('save_dest', dashboardUrl);
    form.action = url.toString();
    form.submit();
});
