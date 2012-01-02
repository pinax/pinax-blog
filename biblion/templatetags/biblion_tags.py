from django import template

from biblion.utils.code_hilite import to_html


register = template.Library()


register.filter("to_html", to_html)
