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
        formatted = "{:,}".format(value)
        return formatted.replace(",", ".")
    except (ValueError, TypeError):
        return value