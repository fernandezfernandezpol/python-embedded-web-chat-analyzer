document.addEventListener("DOMContentLoaded", function() {
    const scrollLink = document.querySelector('.scroll-top-link');
    if (scrollLink) {
        scrollLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({top:0, behavior:"smooth"});
        });
    }
});