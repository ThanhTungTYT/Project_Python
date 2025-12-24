document.addEventListener('DOMContentLoaded', () => {

    // --- Lấy các phần tử CỐ ĐỊNH ---
    const menu = document.getElementById("left-menu");
    const content = document.getElementById("right-content");
    const menuContainer = document.querySelector(".menu");
    const btn_slider_top = document.getElementById("slide-top");
    if (btn_slider_top) {
        window.addEventListener("scroll", () => {
            btn_slider_top.style.display = window.scrollY > 20 ? "block" : "none";
        });
        btn_slider_top.addEventListener("click", () => {
            window.scrollTo({top: 0, behavior: "smooth"});
        });
    }

    // 3. XỬ LÝ SỰ KIỆN TOÀN TRANG
    // Lắng nghe trên `document.body`
    document.body.addEventListener('click', e => {
        // Tìm pop-up MỖI KHI CLICK, vì chúng được tạo động
        const form_add = document.getElementById("form-add");
        const form_remake = document.getElementById("form-remake");
        const detail = document.getElementById("detail-p");

        // a) Xử lý nút ẨN/HIỆN MENU
        const sliderMenu = e.target.closest('#slider-menu');
        if (sliderMenu) {
            if (getComputedStyle(menu).display !== "none") {
                menu.style.display = "none";
                content.style.width = "100%";
                form_add.style.left = "50%";
                form_remake.style.left = "50%";
                detail.style.left = "50%";
            } else {
                menu.style.display = "";
                content.style.width = "80%";
                form_add.style.left = "60%";
                form_remake.style.left = "60%";
                detail.style.left = "60%";
            }
        }

        // b) Xử lý nút MỞ form "Thêm"
        if (e.target.id === 'add') {
            if (form_add && getComputedStyle(form_add).display === 'none') {
                form_add.style.display = 'block';
                content.style.filter = 'blur(5px)';
            }
        }

        // c) Xử lý nút TẮT form "Thêm"
        if (e.target.id === 'take-off') {
            if (form_add && getComputedStyle(form_add).display === 'block') {
                form_add.style.display = 'none';
                content.style.filter = 'blur(0)';
            }
        }

        if (e.target.closest('.remake')) {
            if (form_remake && getComputedStyle(form_remake).display === 'none') {
                form_remake.style.display = 'block';
                content.style.filter = 'blur(5px)';
            }
        }
        if (e.target.id === 'close') {
            if (form_remake && getComputedStyle(form_remake).display === 'block') {
                form_remake.style.display = 'none';
                content.style.filter = 'blur(0)';
            }
        }

        // d) Xử lý nút MỞ "Chi tiết"
        if (e.target.closest('.detail')) {
            if (detail && getComputedStyle(detail).display === 'none') {
                detail.style.display = 'flex';
                content.style.filter = 'blur(5px)';
            }
        }

        // e) Xử lý nút ĐÓNG "Chi tiết"
        if (e.target.id === 'close') {
            if (detail && getComputedStyle(detail).display === 'flex') {
                detail.style.display = 'none';
                content.style.filter = 'blur(0)';
            }
        }
    });

    function openEditModal(id, name, catId, price, weight, stock, desc) {
    const editForm = document.getElementById('form-remake');
    const formTag = document.getElementById('edit-product-form'); // Form trong popup sửa
    const content = document.getElementById('right-content');

    if (formTag && editForm) {
        // QUAN TRỌNG: Cập nhật đường dẫn action để Django biết là SỬA ID nào
        formTag.action = `/quan-ly/sua-san-pham/${id}/`;

        // Đổ dữ liệu vào input
        document.getElementById('edit-id-display').value = id;
        document.getElementById('edit-name').value = name;
        document.getElementById('edit-category').value = catId;
        document.getElementById('edit-price').value = price;
        document.getElementById('edit-weight').value = weight;
        document.getElementById('edit-quantity').value = stock;
        document.getElementById('edit-description').value = desc;

        editForm.style.display = 'flex'; // Hoặc 'block' tùy CSS
        if (content) content.style.filter = 'blur(5px)';
    } else {
        alert("Lỗi: Không tìm thấy Form có id='edit-product-form'");
    }
}

})

