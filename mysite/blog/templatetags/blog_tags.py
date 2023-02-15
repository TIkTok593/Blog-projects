from django import template
from ..models import Post

register = template.library()
@register.simple_tag
def total_post():
    return Post.published.count()