/* CobSin Tema - Ana JavaScript Dosyası */

document.addEventListener('DOMContentLoaded', function() {
    // Mobil Menü Kontrolü
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', function() {
            mainNav.classList.toggle('show');
            document.body.classList.toggle('menu-open');
        });
    }
    
    // Dropdown Menü Kontrolü (Mobil)
    const dropdownItems = document.querySelectorAll('.has-dropdown');
    
    dropdownItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        
        if (link && window.innerWidth <= 992) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const dropdown = this.nextElementSibling;
                if (dropdown && dropdown.classList.contains('dropdown')) {
                    dropdown.classList.toggle('show');
                }
            });
        }
    });
    
    // Slider Kontrolü
    const slider = document.querySelector('.slider');
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.querySelector('.slider-prev');
    const nextBtn = document.querySelector('.slider-next');
    const dots = document.querySelectorAll('.dot');
    
    if (slider && slides.length > 0) {
        let currentSlide = 0;
        const slideCount = slides.length;
        
        // Slider'ı başlat
        function initSlider() {
            if (slideCount > 1) {
                // Otomatik geçiş için interval
                const slideInterval = setInterval(() => {
                    goToSlide(currentSlide + 1);
                }, 5000);
                
                // Kontrol butonları
                if (prevBtn && nextBtn) {
                    prevBtn.addEventListener('click', () => {
                        goToSlide(currentSlide - 1);
                        clearInterval(slideInterval);
                    });
                    
                    nextBtn.addEventListener('click', () => {
                        goToSlide(currentSlide + 1);
                        clearInterval(slideInterval);
                    });
                }
                
                // Nokta navigasyonu
                if (dots.length > 0) {
                    dots.forEach((dot, index) => {
                        dot.addEventListener('click', () => {
                            goToSlide(index);
                            clearInterval(slideInterval);
                        });
                    });
                }
            }
        }
        
        // Belirli bir slide'a git
        function goToSlide(n) {
            currentSlide = (n + slideCount) % slideCount;
            
            slider.style.transform = `translateX(-${currentSlide * 100}%)`;
            
            // Aktif noktayı güncelle
            if (dots.length > 0) {
                dots.forEach(dot => dot.classList.remove('active'));
                dots[currentSlide].classList.add('active');
            }
        }
        
        // Slider'ı başlat
        initSlider();
    }
    
    // Scroll Animasyonu
    const scrollElements = document.querySelectorAll('.scroll-animation');
    
    const elementInView = (el, dividend = 1) => {
        const elementTop = el.getBoundingClientRect().top;
        return (
            elementTop <= (window.innerHeight || document.documentElement.clientHeight) / dividend
        );
    };
    
    const displayScrollElement = (element) => {
        element.classList.add('scrolled');
    };
    
    const hideScrollElement = (element) => {
        element.classList.remove('scrolled');
    };
    
    const handleScrollAnimation = () => {
        scrollElements.forEach((el) => {
            if (elementInView(el, 1.25)) {
                displayScrollElement(el);
            } else {
                hideScrollElement(el);
            }
        });
    };
    
    // Scroll olayını dinle
    window.addEventListener('scroll', () => {
        handleScrollAnimation();
    });
    
    // Sayfa yüklendiğinde görünür elemanları kontrol et
    handleScrollAnimation();
    
    // Yukarı Çık Butonu
    const scrollTopBtn = document.querySelector('.scroll-top');
    
    if (scrollTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add('show');
            } else {
                scrollTopBtn.classList.remove('show');
            }
        });
        
        scrollTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Form Doğrulama
    const contactForm = document.querySelector('.contact-form form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            let isValid = true;
            const inputs = this.querySelectorAll('input, textarea');
            
            inputs.forEach(input => {
                if (input.hasAttribute('required') && !input.value.trim()) {
                    isValid = false;
                    input.classList.add('error');
                } else if (input.type === 'email' && input.value.trim()) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(input.value.trim())) {
                        isValid = false;
                        input.classList.add('error');
                    } else {
                        input.classList.remove('error');
                    }
                } else {
                    input.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Lütfen tüm alanları doğru şekilde doldurunuz.');
            }
        });
        
        // Hata sınıfını kaldır
        const formInputs = contactForm.querySelectorAll('input, textarea');
        formInputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.classList.remove('error');
            });
        });
    }
}); 