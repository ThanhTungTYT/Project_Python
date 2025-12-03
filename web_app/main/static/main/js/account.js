$(document).ready(function() {
    // 1. Xác định khung chứa nội dung
    const contentArea = $('#content-area');

    // 2. Hàm load nội dung (dùng lại nhiều lần)
    function loadContent(url) {
        contentArea.html('<p style="text-align:center; padding: 20px;">Đang tải...</p>');
        
        // Dùng hàm .load() của jQuery để lấy HTML từ URL bỏ vào khung
        contentArea.load(url, function(response, status, xhr) {
            if (status == "error") {
                contentArea.html("<p>Lỗi tải trang: " + xhr.status + " " + xhr.statusText + "</p>");
            }
        });
    }

    // 3. Tự động load tab nào đang có class 'active' khi vừa vào trang
    const activeLink = $('.sidebar-link.active');
    if (activeLink.length > 0) {
        loadContent(activeLink.attr('href'));
    }

    // 4. Bắt sự kiện click vào menu bên trái
    $('.sidebar-link').on('click', function(e) {
        e.preventDefault(); // <--- QUAN TRỌNG: Chặn không cho load lại trang

        // Lấy đường dẫn từ href của thẻ a
        var url = $(this).attr('href');

        // Xử lý giao diện (chuyển class active)
        $('.sidebar-link').removeClass('active');
        $(this).addClass('active');

        // Gọi hàm load
        loadContent(url);
    });
});