// Animation khi cuộn
window.addEventListener("scroll", () => {
    const elements = document.querySelectorAll(".fade-in, .slide-up");
    elements.forEach((el) => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
            el.classList.add("visible");
        }
    });
});
