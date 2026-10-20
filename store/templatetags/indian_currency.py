from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='inr')
def inr(amount):
    """
    Formats a number into the Indian Rupee system:
    1500 -> ₹1,500
    45999 -> ₹45,999
    149900 -> ₹1,49,900
    1250000 -> ₹12,50,000
    """
    if amount is None or amount == "":
        return "₹0"
    try:
        val = Decimal(str(amount))
        is_negative = val < 0
        val = abs(val)

        # Separate integer part and decimals
        int_part = int(val)
        
        s = str(int_part)
        if len(s) <= 3:
            formatted_int = s
        else:
            last3 = s[-3:]
            rest = s[:-3]
            pairs = []
            while len(rest) > 2:
                pairs.insert(0, rest[-2:])
                rest = rest[:-2]
            if rest:
                pairs.insert(0, rest)
            formatted_int = ",".join(pairs) + "," + last3

        sign = "-" if is_negative else ""
        return f"{sign}₹{formatted_int}"
    except Exception:
        return f"₹{amount}"

@register.filter(name='inr_num')
def inr_num(amount):
    """
    Formats without the ₹ symbol
    """
    res = inr(amount)
    return res.replace("₹", "")

@register.filter(name='split_lines')
def split_lines(value):
    if not value:
        return []
    return [line.strip() for line in value.split('\n') if line.strip()]

@register.filter(name='range_stars')
def range_stars(value):
    try:
        val = int(round(float(value)))
        return range(min(max(val, 1), 5))
    except Exception:
        return range(4)
