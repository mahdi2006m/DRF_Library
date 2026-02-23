// File Upload Display
function updateFileName(input) {
    const fileNameText = document.getElementById('file-name-text');
    if (input.files && input.files.length > 0) {
        fileNameText.textContent = input.files[0].name;
    } else {
        fileNameText.textContent = 'Click or drag to upload cover image';
    }
}