$(document).ready(function() {
    // Carousel ayarları
    var $carousel = $('#myCarousel');
    
    // Carousel'ı başlat
    $carousel.carousel({
        interval: parseInt($carousel.data('transition-speed')) || 5000,
        pause: 'hover'
    });
    
    // Carousel kontrolleri için hover efekti
    $('.banner_section').hover(
        function() {
            $('.carousel-control-prev, .carousel-control-next').css('opacity', '1');
        },
        function() {
            $('.carousel-control-prev, .carousel-control-next').css('opacity', '0');
        }
    );
    
    // Carousel indikatörleri için animasyon
    $('.carousel-indicators [data-bs-target]').hover(
        function() {
            $(this).css('transform', 'scale(1.2)');
        },
        function() {
            if (!$(this).hasClass('active')) {
                $(this).css('transform', 'scale(1)');
            }
        }
    );
    
    // Carousel slide değiştiğinde
    $carousel.on('slide.bs.carousel', function () {
        $('.banner_taital, .banner_text, .btn_main').css('opacity', '0');
    });
    
    // Carousel slide değiştikten sonra
    $carousel.on('slid.bs.carousel', function () {
        $('.banner_taital, .banner_text, .btn_main').css('opacity', '1');
    });
    
    // Responsive video popup
    $('.video-popup').magnificPopup({
        type: 'iframe',
        mainClass: 'mfp-fade',
        removalDelay: 160,
        preloader: false,
        fixedContentPos: false,
        iframe: {
            patterns: {
                youtube: {
                    index: 'youtube.com/',
                    id: 'v=',
                    src: '//www.youtube.com/embed/%id%?autoplay=1'
                },
                vimeo: {
                    index: 'vimeo.com/',
                    id: '/',
                    src: '//player.vimeo.com/video/%id%?autoplay=1'
                }
            }
        }
    });
}); 