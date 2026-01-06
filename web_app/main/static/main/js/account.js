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

    // --- XỬ LÝ NÚT HỦY ĐƠN (Event Delegation) ---
    $(document).on('click', '.btn-cancel-order', function() {
        var orderId = $(this).data('id');
        if(confirm('Bạn có chắc chắn muốn hủy đơn hàng này không?')) {
            $.ajax({
                url: '/order/cancel/' + orderId + '/',
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val() || '{{ csrf_token }}' 
                },
                headers: {'X-CSRFToken': getCookie('csrftoken')}, 
                success: function(response) {
                    if(response.success) {
                        alert(response.message);
                        $('#content-area').load('/account/history/'); 
                    } else {
                        alert(response.message);
                    }
                },
                error: function() {
                    alert('Có lỗi xảy ra, vui lòng thử lại.');
                }
            });
        }
    });

    // --- XỬ LÝ NÚT ĐÃ NHẬN (Event Delegation) ---
    $(document).on('click', '.btn-confirm-order', function() {
        var orderId = $(this).data('id');
        if(confirm('Bạn xác nhận đã nhận được hàng?')) {
            $.ajax({
                url: '/order/confirm/' + orderId + '/',
                type: 'POST',
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                success: function(response) {
                    if(response.success) {
                        alert(response.message);
                        $('#content-area').load('/account/history/');
                    } else {
                        alert(response.message);
                    }
                }
            });
        }
    });

    // Hàm lấy CSRF Token từ cookie (Django bắt buộc cần cái này khi POST)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    // --- XỬ LÝ FORM ĐỔI MẬT KHẨU (Event Delegation) ---
    $(document).on('click', '#btn-submit-changepw', function(e) {
        e.preventDefault(); 

        var form = $('#form-changepw');
        var url = form.attr('action'); 
        
        var formData = form.serialize(); 

        $.ajax({
            type: "POST",
            url: url,
            data: formData,
            success: function(responseHtml) {
                $('#content-area').html(responseHtml);
            },
            error: function() {
                alert("Có lỗi xảy ra khi kết nối đến server.");
            }
        });
    });
});