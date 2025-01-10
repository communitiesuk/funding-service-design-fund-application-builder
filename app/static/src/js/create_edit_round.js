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
