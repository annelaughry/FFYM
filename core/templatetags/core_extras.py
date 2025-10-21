from django import template
register = template.Library()


@register.filter
def index(sequence, idx):
    return sequence[idx].prompt