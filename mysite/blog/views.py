from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
# from django.http import Http404


from .models import Post, Comment
from .forms import EmailPostForm, CommentForm

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)  # This post_list is for the variable That get the value from the model
    page_number = request.GET.get('page', 1)  # Get the value of the page if it has one, if not return 1
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts})

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
        comment.post = post
        print(comment)
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})