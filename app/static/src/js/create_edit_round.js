function toggleWelshFields() {
    // Get the welsh availability from the data attribute
    const isWelshAvailable = document.getElementById('round-config').dataset.welshAvailable === 'true';

    const welshFields = document.querySelectorAll('.welsh-field');
    welshFields.forEach(field => {
        const fieldContainer = field.closest('.govuk-form-group');
        if (isWelshAvailable) {
            fieldContainer.style.display = 'block';
        } else {
            fieldContainer.style.display = 'none';
        }
    });
}

// Run on page load
document.addEventListener('DOMContentLoaded', function() {
    toggleWelshFields();
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
