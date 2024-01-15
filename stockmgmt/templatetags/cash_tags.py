from django import template
from stockmgmt.models import AddCash
from django.db import models 


register = template.Library()

@register.simple_tag(takes_context=True)
def get_total_cash(context):
    return AddCash.objects.aggregate(models.Sum('cash'))['cash__sum'] or 0
