// Hiệu ứng xuất hiện khi cuộn xuống
document.addEventListener("scroll", function () {
    const elements = document.querySelectorAll(".fade-in");
    const triggerBottom = window.innerHeight * 0.9;

    elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < triggerBottom) {
            el.classList.add("visible");
        }
    });
});
