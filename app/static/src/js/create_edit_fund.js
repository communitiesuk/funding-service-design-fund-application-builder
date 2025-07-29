function toggleWelshFields() {
    const checked = document.querySelector('input[name="welsh_available"]:checked');
    const welshAvailable = (checked && checked.value) ? checked.value : false;
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
