document.addEventListener('DOMContentLoaded', function() {
    const userMenuButton = document.getElementById('user-menu-button');
    const dropdownMenu = userMenuButton.parentElement.nextElementSibling;


    dropdownMenu.classList.add('hidden');
    userMenuButton.setAttribute('aria-expanded', 'false');

    userMenuButton.addEventListener('click', function(e) {
        e.stopPropagation(); // don’t let the document-click closer fire immediately
        const isOpen = userMenuButton.getAttribute('aria-expanded') === 'true';
        dropdownMenu.classList.toggle('hidden');
        userMenuButton.setAttribute('aria-expanded', String(!isOpen));
    });

    document.addEventListener('click', function() {
        if (userMenuButton.getAttribute('aria-expanded') === 'true') {
            dropdownMenu.classList.add('hidden');
            userMenuButton.setAttribute('aria-expanded', 'false');
        }
    });

    const mobileButton = document.querySelector('button[aria-controls="mobile-menu"]');
    const mobileMenu = document.getElementById('mobile-menu');

    mobileMenu.classList.add('hidden');
    mobileButton.setAttribute('aria-expanded', 'false');

    mobileButton.addEventListener('click', function(e) {
        e.stopPropagation();
        const isOpen = mobileButton.getAttribute('aria-expanded') === 'true';
        mobileMenu.classList.toggle('hidden');
        mobileButton.setAttribute('aria-expanded', String(!isOpen));
    });

    document.addEventListener('click', function() {
        if (mobileButton.getAttribute('aria-expanded') === 'true') {
            mobileMenu.classList.add('hidden');
            mobileButton.setAttribute('aria-expanded', 'false');
        }
    });
});