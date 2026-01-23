document.addEventListener('DOMContentLoaded', function() {

    const minus = document.getElementById("count-minus");
    const add = document.getElementById("count-add");
    const countSpan = document.getElementById("num-count");
    const formQuantityInput = document.getElementById("form-quantity");

    function updateQuantity(val) {
        if (val < 1) val = 1;

        if (countSpan) countSpan.textContent = val;
        
        if (formQuantityInput) formQuantityInput.value = val;
    }

    if (minus && add && countSpan) {
        minus.addEventListener("click", () => {
            let current = parseInt(countSpan.textContent) || 1;
            updateQuantity(current - 1);
        });
        
        add.addEventListener("click", () => {
            let current = parseInt(countSpan.textContent) || 1;
            updateQuantity(current + 1);
        });
    }


    const toggleBtn = document.getElementById('readMoreBtn');
    const content = document.getElementById('contentToCollapse');
    const container = document.getElementById('productDescription');
    
    if (toggleBtn && content && container) {
        toggleBtn.addEventListener('click', function() {
            container.classList.toggle('is-expanded');
            
            if (container.classList.contains('is-expanded')) {
                // Mở rộng
                content.style.maxHeight = content.scrollHeight + 'px';
                this.innerHTML = 'Thu gọn <span class="arrow"></span>';
            } else {
                // Thu gọn
                content.style.maxHeight = null;
                this.innerHTML = 'Xem thêm <span class="arrow"></span>';
            }
        });
    }
});