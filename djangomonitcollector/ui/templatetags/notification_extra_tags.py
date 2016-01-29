import time

from django import template
from django.utils import timezone

register = template.Library()



@register.filter
def from_array_to_ul(myarray):
    output = "<ul>"
    print type(myarray)
    for item in myarray.split(","):
        output = "{0}<li>{1}</li>".format(output,item)
    return "{0}</ul>".format(output)
