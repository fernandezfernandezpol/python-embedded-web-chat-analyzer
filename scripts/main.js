import './pyodide-loader.js';
import './process.js';
import './scroll.js';
import './file-upload.js';
import './output-message.js';

window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 40) {
        header.classList.add('header-small');
    } else {
        header.classList.remove('header-small');
    }
});