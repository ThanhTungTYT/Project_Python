document.addEventListener('DOMContentLoaded', function() {
    // --- Tăng / giảm số lượng ---
    const minus = document.getElementById("count-minus");
    const add = document.getElementById("count-add");
    const count  = document.getElementById("num-count");
    if(minus && add && count){
        minus.addEventListener("click", () => {
            let current = parseInt(count.textContent);
            if(current > 1) count.textContent = current - 1;
        });
        add.addEventListener("click", () => {
            let current = parseInt(count.textContent);
            count.textContent = current + 1;
        });
    }

    // --- Xem thêm / Thu gọn ---
    const toggleBtn = document.getElementById('readMoreBtn');
    const content = document.getElementById('contentToCollapse');
    const container = document.getElementById('productDescription');
    if(toggleBtn && content && container){
        toggleBtn.addEventListener('click', function(){
            container.classList.toggle('is-expanded');
            if(container.classList.contains('is-expanded')){
                content.style.maxHeight = content.scrollHeight + 'px';
                this.innerHTML = 'Thu gọn <span class="arrow"></span>';
            } else {
                content.style.maxHeight = null;
                this.innerHTML = 'Xem thêm <span class="arrow"></span>';
            }
        });
    }

    // --- Thay đổi ảnh thumbnail ---
    const mainProductImage = document.getElementById('img-main');
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    if(mainProductImage && thumbnails.length > 0){
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function(){
                thumbnails.forEach(item => item.classList.remove('active'));
                this.classList.add('active');
                const fullImageUrl = this.getAttribute('data-full-image');
                if(fullImageUrl) mainProductImage.src = fullImageUrl;
            });
        });
    }

    // --- Thêm vào giỏ hàng ---
    function addToCart(productId){
        var csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        var csrfToken = csrfTokenInput ? csrfTokenInput.value : '';

        var quantity = parseInt(document.getElementById('num-count').textContent) || 1;

        fetch('/add_to_cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `product_id=${productId}&quantity=${quantity}&csrfmiddlewaretoken=${csrfToken}`
        }).then(res => res.json())
        .then(response => {
            if(response.status === 'success'){
                alert("Đã thêm sản phẩm vào giỏ hàng!");
                const cartLabel = document.getElementById('num-cart-label');
                if(cartLabel) cartLabel.textContent = response.total_quantity;
            } else if(response.status === 'error'){
                if(confirm(response.message + " Bạn có muốn đến trang đăng nhập không?")){
                    window.location.href = "/login/";
                }
            }
        }).catch(err => {
            console.error("AJAX lỗi:", err);
            alert("Có lỗi khi kết nối server!");
        });
    }

    const addCartBtn = document.querySelector('.add-cart-btn');
    if(addCartBtn){
        addCartBtn.addEventListener('click', function(){
            const productId = this.dataset.id;
            addToCart(productId);
        });
    }
});
