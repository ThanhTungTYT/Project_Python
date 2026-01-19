const img_home = document.getElementById('img-home');
const images = Array.isArray(window.BANNERS) ? window.BANNERS.filter(Boolean) : [];

let currentIndex = 0;
let slideInterval; // Biến lưu timer

// Hàm hiển thị ảnh dựa trên currentIndex
function updateBanner() {
    if (images.length > 0) {
        img_home.style.backgroundImage = `url('${images[currentIndex]}')`;
    }
}

function showNextImage() {
    currentIndex++;
    if (currentIndex >= images.length) {
        currentIndex = 0;
    }
    updateBanner();
}

function showPreviousImage() {
    currentIndex--;
    if (currentIndex < 0) {
        currentIndex = images.length - 1;
    }
    updateBanner();
}

// Hàm Wrapper để xử lý khi click nút (Reset timer)
function handleNextClick() {
    showNextImage();
    resetTimer();
}

function handlePreviousClick() {
    showPreviousImage();
    resetTimer();
}

// Hàm reset lại đồng hồ đếm ngược khi người dùng tương tác
function resetTimer() {
    clearInterval(slideInterval);
    slideInterval = setInterval(showNextImage, 3000);
}

// KHỞI CHẠY
if (images.length > 0) {
    // 1. Hiển thị ảnh đầu tiên ngay lập tức (không đợi 3s)
    updateBanner(); 
    
    // 2. Bắt đầu timer
    slideInterval = setInterval(showNextImage, 3000);
}

document.querySelector('.left').onclick = handlePreviousClick;
document.querySelector('.right').onclick = handleNextClick;

window.addEventListener("scroll", () => {
    const elements = document.querySelectorAll(".fade-in, .slide-up");
    elements.forEach((el) => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
            el.classList.add("visible");
        }
    });
});