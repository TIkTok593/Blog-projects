from typing import Any
from django.forms.models import BaseModelForm
from django.shortcuts import render, get_object_or_404, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, CreateView 
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.utils.text import slugify

from taggit.models import Tag
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, PostForm, UserRegistrationForm

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, tag=tag_slug)
        post_list = post_list.filter(tag__in=[tag]) # here we put the tag in brackets because it's an array

    paginator = Paginator(post_list, 3)  # This post_list is for the variable That get the value from the model
    page_number = request.GET.get('page', 1)  # Get the value of the page if it has one, if not return 1
    try:
        posts = paginator.page(page_number)

    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 
    'blog/post/list.html', 
    {
        'posts': posts,
        'tag': tag                
    })


@login_required
def post_create(request):
    pass


@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    form_class = PostForm
    template_name = 'blog/post/post_create.html'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        title = form.cleaned_data['title']
        slug = slugify(title)
        form.instance.slug = slug
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('blog:post_list')



@login_required
def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404('No Post found.')
    # return render(request, 'blog/post/detail.html', {'post': post})
    post = get_object_or_404(Post, 
                            slug=post,
                            publish__year=year,
                            publish__month=month,
                            publish__day = day,
                            status=Post.Status.PUBLISHED)
    
    comments = post.comments.filter(active=True) # we can use comments, because we defined the related_name in Comments's Model
    form = CommentForm()
    return render(request,
     'blog/post/detail.html',
      {'post': post,
       'comments': comments,
       'form': form
       }
    )

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'abuyahyadiab@gmail.com',
                      [cd['to']])
            sent = True


    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form, 'sent': sent})

@require_POST
def post_comment(request, post_id):
    # here the user has been posted a comment to a specific post
    # I'll try to fetch this post, if not exist, an error will be generated
    # If it exist, we will assign this post to a field on that comment's object
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED) # you have to assure that this is a published post not a draft one.
    comment = None
    print(request.POST)
    form = CommentForm(request.POST) # by using request.POST, we get the form object that has been submitted, and we pass it to comment form to check it's validation
    print(form)
    if form.is_valid():
        comment = form.save(commit=False)
        print(comment)
        comment.post = post
        print(comment)
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


def user_register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)  # don't save the user now, because we want to add on it.
            new_user.set_password(  # this method is for hashing passwords rather than put it in a plain text.
                user_form.cleaned_data['password1']
            )
            new_user.save()
            return render(request, 'blog/register_done.html', {'user_form': user_form})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'blog/register.html',
                  {'user_form': user_form}
                  )
