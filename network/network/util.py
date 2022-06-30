from django.http import request
from django.urls import reverse
from django.core.paginator import EmptyPage, Paginator
from urllib.parse import urlencode

from .models import Post, User

def paginate(route_name, p_nmbr_str, user=None):

    # Get posts associated with that route
    if route_name == "index":
        posts = Post.objects.all().order_by("-timestamp")
    elif route_name == "profile":
        posts = Post.objects.filter(creator=user).order_by("-timestamp")
    elif route_name == "following":
        followed = User.objects.filter(followers=user)
        posts = Post.objects.filter(creator__in=followed).order_by("-timestamp")
    
    # Paginate the posts
    paginator = Paginator(posts, 10)

    # Ensure page number was provided
    if not p_nmbr_str:
        if route_name == "profile":
            base_url = reverse(route_name, kwargs={"username": user.username})
        else:
            base_url = reverse(route_name)
        query_string = urlencode({'page': 1})
        url = "{}?{}".format(base_url, query_string)
        return {"url_redirect": url}
    
    # Ensure page number is valid
    try:
        page_number = int(p_nmbr_str)
        page = paginator.page(page_number)
    except ValueError:
        return {"error": "Page does not exist"}
    except EmptyPage:
        return {"error": "Page does not exist"}
    
    return {
        "paginator": paginator,
        "page_number": page_number,
        "posts": page.object_list,
        "page":page,
    }