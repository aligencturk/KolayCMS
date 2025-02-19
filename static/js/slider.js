document.addEventListener('DOMContentLoaded', function() {
    var myCarousel = document.getElementById('myCarousel');
    if (myCarousel) {
        // Slider ayarlarını data attribute'larından al
        var transitionSpeed = myCarousel.dataset.transitionSpeed === 'false' ? false : parseInt(myCarousel.dataset.transitionSpeed);
        
        var sliderConfig = {
            interval: transitionSpeed,
            pause: 'hover'
        };

        var carousel = new bootstrap.Carousel(myCarousel, sliderConfig);
    }
}); 