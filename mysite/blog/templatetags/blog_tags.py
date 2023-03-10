from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments') # comments is the a name for foreign key between Post and Comments Models named in the related field
    ).order_by('-total_comments')[:count]


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}
# @register.simple_tag
# def show_latest_posts(count=5):
#     latest_posts = Post.published.order_by('-publish')[:count]
#     return latest_posts


#this is a filter
@register.filter(name='markdown')  # this name will be used in the templates for filtering
def markdown_format(text):
    return mark_safe(markdown.markdown(text))