import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http.response import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Post, User
from .util import paginate

def index(request):
    response = paginate("index", request.GET.get('page'))
    
    # Ensure page validation was successful
    if "url_redirect" in response:
        return redirect(response["url_redirect"])
    elif "error" in response:
        raise Http404("Page does not exist")
    
    return render(request, "network/index.html", {
        "posts": response["posts"],
        "page_number": response["page_number"],
        "paginator": response["paginator"],
        "page": response["page"],
        "route_name": "index"
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def create(request):
    if request.method == "POST":

        # Ensure submitted form is valid
        content = request.POST.get("content")
        if (not content or len(content) > 512):
            return HttpResponseRedirect(reverse("index"))

        # Create post
        post = Post(creator=request.user, content=content)
        post.save()

        return HttpResponseRedirect(reverse("index"))

    # This branch is for creating posts only. Do not let user try to access it
    raise Http404("Page does not exist")


def profile(request, username):
    
    # Ensure that username exists
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    
    # Get user's followers/following data
    followers_count = user.count_followers()
    following_count = user.count_following()

    # See if who requested the page follow the user
    follow_btn_html = "Follow"
    if request.user in user.followers.all():
        follow_btn_html = "Unfollow"
    
    # Paginate posts
    response = paginate("profile", request.GET.get('page'), user=user)

    # Ensure page validation was successful
    if "url_redirect" in response:
        return redirect(response["url_redirect"])
    elif "error" in response:
        raise Http404("Page does not exist")

    return render(request, "network/profile.html", {
        "posts": response["posts"],
        "page_number": response["page_number"],
        "paginator": response["paginator"],
        "page": response["page"],
        "followers_count": followers_count,
        "following_count": following_count,
        "follow_btn_html": follow_btn_html,
        "profile_user": user,
        "route_name": "profile"
    })


@login_required
def follow(request, user_id):

    try:
        profile_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({
            "error": f"User with id {user_id} does not exist."
        }, status=400)
    
    # Don't allow user to follow himself
    if request.user.id == profile_user.id:
        return JsonResponse({
            "error": f"You cannot follow yourself."
        }, status=400)
    
    # Follow/unfollow
    if request.user in profile_user.followers.all():
        # Unfollow
        profile_user.followers.remove(request.user)
        following = False
    else:
        # Follow
        profile_user.followers.add(request.user)
        following = True
    
    followers_count = profile_user.count_followers()

    return JsonResponse({
        "success": "Action completed successfully.",
        "following": following,
        "followers_count": followers_count
        }, status=201)


@login_required
def following(request):
    response = paginate("following", request.GET.get('page'), request.user)
    
    # Ensure page validation was successful
    if "url_redirect" in response:
        return redirect(response["url_redirect"])
    elif "error" in response:
        raise Http404("Page does not exist")
    
    return render(request, "network/following.html", {
        "posts": response["posts"],
        "page_number": response["page_number"],
        "paginator": response["paginator"],
        "page": response["page"],
        "route_name": "following"
    })


@login_required
def edit(request, post_id):
    # Editing a post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Ensure post with given id exists
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post with that id does not exist"}, status=404)

    # Ensure user trying to edit the post is its creator
    if request.user != post.creator:
        return JsonResponse({"error": "Only the post's creator may edit it."}, status=400)

    # Ensure post's new content is valid
    data = json.loads(request.body)
    content = data.get("content")
    if (not content or len(content) > 512):
        return JsonResponse({"error": "Post must be 1-512 characters long."}, status=400)
    
    # Edit post
    post.content = content
    post.save()

    return JsonResponse({
        "message": "Post edited successfully.",
        "content": content
        }, status=201)


@login_required
def like(request, post_id):
    
    # Liking a post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # Ensure post with given id exists
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post with that id does not exist"}, status=404)

    # Like/unlike post
    if request.user in post.likers.all():
        post.likers.remove(request.user)
        likes = False
    else:
        post.likers.add(request.user)
        likes = True

    return JsonResponse({
        "message": "Action completed successfully.",
        "like_count": post.likers.all().count(),
        "likes": likes
    }, status=201)

