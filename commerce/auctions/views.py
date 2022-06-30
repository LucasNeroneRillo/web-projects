from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from .util import get_listing_by_id

def index(request):
    listings = Listings.objects.filter(closed=False)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "page": "active"
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":

        # Ensure submitted form is valid
        try:
            title = str(request.POST["title"])
            description = str(request.POST["description"])
            starting_bid = round(float(request.POST["starting_bid"]), 2)
            image_url = str(request.POST.get("image_url"))
            category = request.POST.get("category")
            creator = request.user
            current_bid = starting_bid

        # Display error message to user (if form is invalid)
        except KeyError:
            return HttpResponseRedirect(reverse("create"))
        except ValueError:
            return HttpResponseRedirect(reverse("create"))
        if (    len(title) > 128 or 
                len(description) > 256 or
                len(category) > 32 or
                len(image_url) > 8192 or
                starting_bid >= pow(10, 15) or
                starting_bid <= 0):
            return HttpResponseRedirect(reverse("create"))

        # Save form to database
        form = Listings(title=title, description=description, starting_bid=starting_bid,
            image_url=image_url, category=category, creator=creator, current_bid=current_bid)
        form.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create.html")


def listings(request, primary_key):

    listing = get_listing_by_id(primary_key)
    
    try:
        bids = Bids.objects.filter(listing=listing)
        biggest_bid = bids.get(bid=listing.current_bid)
        bidder = biggest_bid.bidder
        bids_count = bids.count
    except:
        bids = 0
        bidder = None
        bids_count = 0
    try:
        comments = Comments.objects.filter(listing=listing)
    except:
        comments = None
    
    # If listing specified does not exist, redirect user to home page
    if not listing:
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/listings.html", {
            "listing": listing,
            "bids": bids,
            "bidder": bidder,
            "bids_count": bids_count,
            "comments": comments
        })


@login_required
def watchlist(request):
    if request.method == "POST":
        
        listing = get_listing_by_id(request.POST["listing_id"])

        # If listing specified does not exist, redirect user to home page
        if not listing:
            return HttpResponseRedirect(reverse("index"))

        # If listing in watchlist, remove it. Otherwise, add it.
        if request.user in listing.users_watching.all():
            listing.users_watching.remove(request.user)
        else:
            listing.users_watching.add(request.user)
        
        return HttpResponseRedirect(reverse("listings", kwargs={"primary_key": request.POST["listing_id"]}))

    return render(request, "auctions/index.html", {
        "listings": request.user.watchlisted.all(),
        "page": "watchlist"
    })


@login_required
def bid(request):
    if request.method == "POST":

        listing = get_listing_by_id(request.POST["listing_id"])
        
        # If listing specified does not exist, redirect user to home page
        if not listing:
            return HttpResponseRedirect(reverse("index"))
        
        # Check if bid is indeed a float
        try:
            bid = float(request.POST["bid"])
        except ValueError:
            return HttpResponseRedirect(reverse("listings",
                kwargs={"primary_key": request.POST["listing_id"]}))

        # Check if bid is greater than current one (and at least as large as starting bid)
        if (    (not listing.bids_made and bid < listing.current_bid) or
                (listing.bids_made and bid <= listing.current_bid)):
                return HttpResponseRedirect(reverse("listings",
                    kwargs={"primary_key": request.POST["listing_id"]}))

        # Add bid to database and update current bid
        listing.current_bid = bid
        listing.bids_made = True
        listing.save()
        bid_object = Bids(listing=listing, bid=bid, bidder=request.user)
        bid_object.save()
        
        return HttpResponseRedirect(reverse("listings", kwargs={"primary_key": request.POST["listing_id"]}))

    # This branch is for updating bids only. Do not let user try to access it
    raise Http404("Page does not exist")


@login_required
def comment(request):
    if request.method == "POST":

        listing = get_listing_by_id(request.POST["listing_id"])
        
        # If listing does not exist, redirect user to home page
        if not listing:
            return HttpResponseRedirect(reverse("index"))
        # Check if comment is indeed a string
        try:
            text = str(request.POST["text"])
        except ValueError:
            return HttpResponseRedirect(reverse("listings",
                kwargs={"primary_key": request.POST["listing_id"]}))

        # Check if comment's length match criteria
        if len(text) > 1024:
            return HttpResponseRedirect(reverse("listings",
                kwargs={"primary_key": request.POST["listing_id"]}))

        # Add comment to database
        comment = Comments(text=text, creator=request.user, listing=listing)
        comment.save()

        return HttpResponseRedirect(reverse("listings", kwargs={"primary_key": request.POST["listing_id"]}))
    
    # This branch is for creating comments only. Do not let user try to access it
    raise Http404("Page does not exist")


@login_required
def close(request):
    if request.method == "POST":

        listing = get_listing_by_id(request.POST["listing_id"])
        
        # If listing not exists or user doesn't own it, redirect them to home page
        if not listing or not listing.creator == request.user:
            return HttpResponseRedirect(reverse("index"))
        
        # Close listing
        listing.closed = True
        listing.save()

        return HttpResponseRedirect(reverse("listings", kwargs={"primary_key": request.POST["listing_id"]}))
    
    # This branch is for closing listings only. Do not let user try to access it
    raise Http404("Page does not exist")


def categories(request):
    categories = Listings.objects.exclude(category__exact='').values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html", {
            "categories": categories
        })


def category(request, title):
    listings = Listings.objects.filter(closed=False, category=title)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "page": "categories",
        "category": title
    })
    