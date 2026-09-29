/**
 * Leaf Letang Enterprises — Main JavaScript
 */
(function () {
    'use strict';

    // Mobile menu
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.nav');
    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            const open = nav.classList.toggle('open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            document.body.style.overflow = open ? 'hidden' : '';
        });
        // Close on link click
        nav.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                nav.classList.remove('open');
                toggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            });
        });
    }

    // Sticky header shadow
    const header = document.querySelector('.site-header');
    if (header) {
        const onScroll = function () {
            if (window.scrollY > 20) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    // Active nav link
    const path = window.location.pathname.replace(/\/$/, '') || '/';
    document.querySelectorAll('.nav-list a').forEach(function (a) {
        const href = a.getAttribute('href');
        if (!href) return;
        const clean = href.replace(/\/$/, '') || '/';
        if (clean === path) {
            a.classList.add('active');
            a.setAttribute('aria-current', 'page');
        }
    });

    // Auto-dismiss flash messages
    document.querySelectorAll('.flash').forEach(function (el) {
        setTimeout(function () {
            el.style.opacity = '0';
            el.style.transform = 'translateX(20px)';
            setTimeout(function () { el.remove(); }, 300);
        }, 5000);
    });

    // Gallery filter (client-side)
    const filterBtns = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    if (filterBtns.length && galleryItems.length) {
        filterBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                filterBtns.forEach(function (b) { b.classList.remove('active'); });
                btn.classList.add('active');
                const cat = btn.dataset.category;
                galleryItems.forEach(function (item) {
                    if (cat === 'All' || item.dataset.category === cat) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    // Lightbox
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = lightbox ? lightbox.querySelector('img') : null;
    const lightboxClose = lightbox ? lightbox.querySelector('.lightbox-close') : null;

    if (lightbox && lightboxImg) {
        document.querySelectorAll('.gallery-item[data-full]').forEach(function (item) {
            item.addEventListener('click', function () {
                lightboxImg.src = item.dataset.full;
                lightboxImg.alt = item.dataset.title || '';
                lightbox.classList.add('active');
                lightbox.setAttribute('aria-hidden', 'false');
                document.body.style.overflow = 'hidden';
            });
            item.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    item.click();
                }
            });
        });

        function closeLightbox() {
            lightbox.classList.remove('active');
            lightbox.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }

        if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', function (e) {
            if (e.target === lightbox) closeLightbox();
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && lightbox.classList.contains('active')) closeLightbox();
        });
    }
})();
