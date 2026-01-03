from django import template

register = template.Library()

@register.filter(name='vn_currency')
def vn_currency(value):
    """
    Chuyển đổi số thành định dạng tiền tệ Việt Nam.
    Ví dụ: 150000 -> 150.000
    """
    try:
        value = int(value)
        # Format số với dấu phẩy ngăn cách (1,000,000)
        formatted = "{:,}".format(value)
        # Đổi dấu phẩy thành dấu chấm cho đúng chuẩn VN (1.000.000)
        return formatted.replace(",", ".")
    except (ValueError, TypeError):
        return value