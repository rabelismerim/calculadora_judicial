from django import template

register = template.Library()


@register.filter
def replace(value, arg):
    """
    Substitui todas as ocorrências de um valor por outro.
    """
    what, to = arg.split('|')
    return value.replace(what, to)
