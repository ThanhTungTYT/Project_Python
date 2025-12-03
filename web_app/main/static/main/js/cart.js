document.addEventListener("DOMContentLoaded", function () {
    const cartList = document.getElementById("cart-list");
    const totalDisplay = document.getElementById("cart-total");
    const clearAllBtn = document.querySelector(".clear-all-cart");
    const selectAllBtn = document.querySelector(".select-all-cart");

    // Gắn sự kiện ban đầu
    initCartEvents();
    updateCartTotal();

    // GẮN SỰ KIỆN CHO TOÀN BỘ ITEM
    function initCartEvents() {
        document.querySelectorAll(".cart-item").forEach(item => attachItemEvents(item));
    }


    // SỰ KIỆN TRONG MỖI CART-ITEM
    function attachItemEvents(item) {
        const btnMinus = item.querySelector(".btn-decrease");
        const btnPlus = item.querySelector(".btn-increase");
        const qtyInput = item.querySelector("input[type='number']");
        const checkbox = item.querySelector(".product-select");
        const removeBtn = item.querySelector(".product-remove");

        btnMinus.addEventListener("click", () => { changeQuantity(qtyInput, -1); });
        btnPlus.addEventListener("click", () => { changeQuantity(qtyInput, +1); });

        qtyInput.addEventListener("change", () => {
            qtyInput.value = Math.max(1, parseInt(qtyInput.value) || 1);
            updateCartTotal();
        });

        checkbox.addEventListener("change", updateCartTotal);

        removeBtn.addEventListener("click", () => {
            item.remove();
            updateCartTotal();
        });
    }

    // THAY ĐỔI SỐ LƯỢNG
    function changeQuantity(input, amount) {
        let val = parseInt(input.value) || 1;
        val = Math.max(1, val + amount);
        input.value = val;
        updateCartTotal();
    }

    // CẬP NHẬT TỔNG TIỀN
    function updateCartTotal() {
        let total = 0;

        document.querySelectorAll(".cart-item").forEach(item => {
            const checkbox = item.querySelector(".product-select");
            const qty = parseInt(item.querySelector("input[type='number']").value);
            const price = parseInt(item.dataset.price);
            const subtotal = qty * price;

            item.querySelector(".product-subtotal").textContent = formatPrice(subtotal);

            if (checkbox.checked) total += subtotal;
        });

        totalDisplay.textContent = formatPrice(total);
    }

    // NÚT XÓA TẤT CẢ
    clearAllBtn.addEventListener("click", e => {
        e.preventDefault();
        cartList.innerHTML = "";
        updateCartTotal();
    });

    // NÚT CHỌN TẤT CẢ
    selectAllBtn.addEventListener("click", e => {
        e.preventDefault();

        const checkboxes = document.querySelectorAll(".product-select");

        // Nếu tất cả đã chọn → chuyển thành bỏ chọn
        const shouldSelectAll = [...checkboxes].some(cb => !cb.checked);

        checkboxes.forEach(cb => cb.checked = shouldSelectAll);

        updateCartTotal();
    });

    // ĐỊNH DẠNG GIÁ
    function formatPrice(value) {
        return value.toLocaleString("vi-VN") + "đ";
    }
});
