from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # --- Trang chủ & Sản phẩm ---
    path('', views.get_index, name='index'),
    path('catalog/', views.get_catalog, name='catalog'),
    path('product/<int:product_id>/', views.get_product, name='product'),
    path('search/', views.get_search, name='search'),

    # --- Tài khoản & Xác thực ---
    path('login/', views.get_login, name='login'),
    path('register/', views.get_register, name='register'), # Giữ 1 dòng này thôi
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout/', views.get_logout, name='logout'),
    path('forgotpassword/', views.get_forgotpassword, name='forgotpassword'),
    path('changepw/', views.get_changepw, name='changepw'),
    path('account/', views.get_account, name='account'),
    path('info/', views.get_info, name='info'),
    path('history/', views.get_history, name='history'),
    path('delete_account/<int:user_id>/', views.delete_account, name='delete_account'),
    path('add_account/', views.add_account, name='add_account'),

    # --- Giỏ hàng (Cart) ---
    path('cart/', views.get_cart, name='cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_cart_item/', views.remove_cart_item, name='remove_cart_item'),
    path('remove_all_cart_items/', views.remove_all_cart_items, name='remove_all_cart_items'),
    
    # --- Thanh toán (Checkout) ---
    path('cart/prepare/', views.prepare_checkout, name='prepare_checkout'),
    path('checkout/', views.checkout_view, name='checkout'),          # Trang hiển thị thanh toán
    path('process/', views.process_checkout, name='process_checkout'), # Xử lý đặt hàng
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),    # Áp mã
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'), # Gỡ mã
    
    path('payment/', views.get_payment, name='payment'), # (Có thể dư thừa nếu đã dùng checkout?)
    path('payment/qr/<int:order_id>/', views.payment_qr, name='payment_qr'),
    
    # --- Đơn hàng ---
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/confirm/<int:order_id>/', views.confirm_order, name='confirm_order'),

    # --- Thông tin phụ ---
    path('about/', views.get_about, name='aboutUs'),
    path('shippingPolicies/', views.get_shippingPolicies, name='shippingPolicies'),
    path('termOfUse/', views.get_termOfUse, name='termOfUse'),
    path('warrantyPolicies/', views.get_warrantyPolicies, name='warrantyPolicies'),
    path('help/', views.get_help, name='help'),

    # --- Admin Pages ---
    path('adminPage1/', views.get_adminPage1, name='adminPage1'),
    path('adminPage2/', views.get_adminPage2, name='adminPage2'),
    path('adminPage3/', views.get_adminPage3, name='adminPage3'),
    path('adminPage4/', views.get_adminPage4, name='adminPage4'),
    path('adminPage5/', views.get_adminPage5, name='adminPage5'),
    path('adminPage6/', views.get_adminPage6, name='adminPage6'),
    path('adminPage7/', views.get_adminPage7, name='adminPage7'),
    path('adminPage8/', views.get_adminPage8, name='adminPage8'),

    # --- Admin Chức năng ---
    path('quan-ly/them-san-pham/', views.add_product, name='add_product'),
    path('quanly/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('quan-ly/sua-san-pham/<int:product_id>/', views.edit_product, name='edit_product'),
    path('quan-ly/xoa-danh-gia/<int:review_id>/', views.delete_review, name='delete_review'),
    
    path('add_discount/', views.add_discount, name='add_discount'),
    path('update_discount/<int:promo_id>/', views.update_discount, name='update_discount'),
    path('delete_discount/<int:promo_id>/', views.delete_discount, name='delete_discount'),
    
    path('add_banner/', views.add_banner, name='add_banner'),
    path('update_banner/', views.update_banner, name='update_banner'),
    path('delete_banner/<int:banner_id>/', views.delete_banner, name='delete_banner'),
]