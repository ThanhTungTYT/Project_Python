const img_home = document.getElementById('img-home');
const images = [
    '/static/main/img/img_1.jpg',
    '/static/main/img/img_2.jpg',
    '/static/main/img/img_3.jpg'
];

let currentIndex = 0;

function showNextImage() {
    currentIndex++;
    if (currentIndex >= images.length) {
        currentIndex = 0;
    }
    img_home.style.backgroundImage = `url('${images[currentIndex]}')`;
}

function showPreviousImage() {
    currentIndex--;
    if (currentIndex < 0) {
        currentIndex = images.length - 1;
    }
    img_home.style.backgroundImage = `url('${images[currentIndex]}')`;
}

setInterval(showNextImage, 3000);

window.addEventListener("scroll", () => {
    const elements = document.querySelectorAll(".fade-in, .slide-up");
    elements.forEach((el) => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
            el.classList.add("visible");
        }
    });
});




