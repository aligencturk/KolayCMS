/**
 * Cobsin Theme - Main JavaScript
 * KolayCMS
 */

// Document Ready Function
document.addEventListener('DOMContentLoaded', function() {
    // Animasyon efektleri
    initAnimations();
    
    // Mobil menü
    initMobileMenu();
    
    // Smooth scroll
    initSmoothScroll();
    
    // Testimonial carousel
    initTestimonialCarousel();
});

/**
 * Animasyon efektlerini başlat
 */
function initAnimations() {
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animateElements.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    animateElements.forEach(element => {
        observer.observe(element);
    });
}

/**
 * Mobil menü işlevselliğini başlat
 */
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    
    if (!navbarToggler) return;
    
    navbarToggler.addEventListener('click', function() {
        document.body.classList.toggle('mobile-menu-open');
    });
    
    // Dropdown menüler için
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth < 992) {
                e.preventDefault();
                e.stopPropagation();
                
                const parent = this.parentElement;
                const dropdown = parent.querySelector('.dropdown-menu');
                
                if (dropdown) {
                    dropdown.classList.toggle('show');
                }
            }
        });
    });
}

/**
 * Smooth scroll işlevselliğini başlat
 */
function initSmoothScroll() {
    const scrollLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                
                // URL'yi güncelle
                history.pushState(null, null, targetId);
            }
        });
    });
}

/**
 * Testimonial carousel işlevselliğini başlat
 */
function initTestimonialCarousel() {
    const carousel = document.querySelector('.testimonial-carousel');
    
    if (!carousel) return;
    
    const prevBtn = carousel.querySelector('.carousel-prev');
    const nextBtn = carousel.querySelector('.carousel-next');
    const items = carousel.querySelectorAll('.testimonial-item');
    
    if (items.length <= 3) return;
    
    let currentIndex = 0;
    const itemsPerSlide = window.innerWidth < 768 ? 1 : 3;
    const maxIndex = Math.ceil(items.length / itemsPerSlide) - 1;
    
    // İlk durumu ayarla
    updateCarousel();
    
    // Önceki slide'a git
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            currentIndex = Math.max(0, currentIndex - 1);
            updateCarousel();
        });
    }
    
    // Sonraki slide'a git
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            currentIndex = Math.min(maxIndex, currentIndex + 1);
            updateCarousel();
        });
    }
    
    // Carousel'i güncelle
    function updateCarousel() {
        const offset = currentIndex * itemsPerSlide;
        
        items.forEach((item, index) => {
            if (index >= offset && index < offset + itemsPerSlide) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        // Butonları güncelle
        if (prevBtn) {
            prevBtn.disabled = currentIndex === 0;
        }
        
        if (nextBtn) {
            nextBtn.disabled = currentIndex === maxIndex;
        }
    }
    
    // Pencere boyutu değiştiğinde güncelle
    window.addEventListener('resize', function() {
        const newItemsPerSlide = window.innerWidth < 768 ? 1 : 3;
        
        if (newItemsPerSlide !== itemsPerSlide) {
            itemsPerSlide = newItemsPerSlide;
            currentIndex = 0;
            updateCarousel();
        }
    });
}

/**
 * Tema bilgisi
 */
const themeInfo = {
    name: 'Cobsin',
    version: '1.0.0',
    author: 'KolayCMS',
    description: 'Modern ve kullanıcı dostu bir tema'
}; 