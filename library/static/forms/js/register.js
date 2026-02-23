// Profile image preview
document.getElementById('id_profile_image').addEventListener('change', function (e) {
    const file = e.target.files[0];
    const preview = document.getElementById('imagePreview');

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.innerHTML = `<img src="${e.target.result}" class="profile-preview" alt="Profile preview">`;
        };
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '';
    }
});

// Form validation
document.getElementById('registrationForm').addEventListener('submit', function (e) {
    const termsCheck = document.getElementById('termsCheck');
    if (!termsCheck.checked) {
        e.preventDefault();
        alert('Please accept the Terms and Conditions to register.');
        return false;
    }
});

// Password strength indicator
const password1 = document.getElementById('id_password1');
const password2 = document.getElementById('id_password2');

password1.addEventListener('input', function () {
    const password = this.value;
    let strength = 0;

    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;

    // You can add visual feedback here if needed
});

// Real-time validation
password2.addEventListener('input', function () {
    if (this.value !== password1.value) {
        this.setCustomValidity('Passwords do not match');
    } else {
        this.setCustomValidity('');
    }
});
