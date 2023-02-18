from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, \
    SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity

from taggit.models import Tag

# from django.http import Http404


from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'  # Used for passing parameters to the model
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)  # Notice that slug will convert the word to lower case
        post_list = post_list.filter(tag__in=[tag])  # here we put the tag in brackets because it's an array

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
                             publish__day=day,
                             status=Post.Status.PUBLISHED)

    comments = post.comments.filter(
        active=True)  # we can use comments, because we defined the related_name in Comments's Model
    form = CommentForm()

    post_tags = post.tag.values_list('id', flat=True)  # This will return you a list of tags' ids and flat to return
    # it in a list of ids not list of characters
    similar_posts = Post.published.filter(tag__in=post_tags).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tag')) \
                        .order_by('-same_tags', '-publish')[:4]  # this will generate a field called same_tags
    # This field will be in each on of the similar posts, we will order them by this field firstly.

    return render(request,
                  'blog/post/detail.html',
                  {
                      'post': post,
                      'comments': comments,
                      'form': form,
                      'similar_posts': similar_posts
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
            print(post.get_absolute_url())
            print(request.build_absolute_uri(post.get_absolute_url()))
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
    # If it exists, we will assign this post to a field on that comment's object
    post = get_object_or_404(Post, id=post_id,
                             status=Post.Status.PUBLISHED)  # you have to assure that this is a published post not a
    # draft one.
    comment = None
    print(request.POST)
    form = CommentForm(
        request.POST)  # by using request.POST, we get the form object that has been submitted, and we pass it to
    # comment form to check it's validated
    print(form)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        print(comment)
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    print('request.GET \n', request.GET)
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        print('request.GET \n', form)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body', config='english', weight='A') + \
                            SearchVector('body', weight='B')
            search_query = SearchQuery(query, config='english')
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
            ).filter(rank__gte=0.3).order_by('-rank')
            # results = Post.published.annotate(
            #     similarity=TrigramSimilarity('title', query),
            # ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'results': results
        }
    )
