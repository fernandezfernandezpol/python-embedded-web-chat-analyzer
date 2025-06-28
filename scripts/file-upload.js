const fileInput = document.getElementById('txtfile');
const fileLabel = document.getElementById('file-upload-label');

fileInput.addEventListener('change', function() {
    if (fileInput.files.length) {
        fileLabel.textContent = fileInput.files[0].name;
    } else {
        fileLabel.textContent = 'No se ha seleccionado ningún archivo';
    }
});