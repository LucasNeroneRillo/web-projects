from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import markdown2
import re
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):

    entry = util.get_entry(title)
    if entry:
        html = markdown2.markdown(entry)
        return render(request, "encyclopedia/entry.html", {
        "entry": html,
        "title": title
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "This page does not exist!"
            })


def search(request, title):

    # If user submitted form (reached via POST), redirect it to the same page via GET
    if request.method == "POST":
        title = request.POST.get("q")
        return HttpResponseRedirect(reverse("encyclopedia:search", kwargs={"title": title}))
    
    else:
        # If typed text matches an entry, redirect user to that entry
        if util.get_entry(title):
            return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={"title": title}))

        # Else, display entries that contain typed text as a substring
        else:
            entries = list(filter(lambda x: re.search(title, x, re.IGNORECASE), util.list_entries()))
            return render(request, "encyclopedia/search.html", {
            "entries": entries
            })


def create(request):

    # If user submitted creation (POSTed form), create new entry
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # If entry already exists, return error
        if title in util.list_entries():
            return render(request, "encyclopedia/error.html", {
            "message": "This page already exists!"
            })

        # Create new file and update view
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={"title": title}))
        

    # Else, render page for user to create a new entry
    else:
        return render(request, "encyclopedia/create.html")


def edit(request, title):

    # When user submit changes to file, update file and view
    if request.method == "POST":
        content = request.POST.get("content")
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={"title": title}))
    
    # Render file for user
    else:
        content = util.get_entry(title)

        # Ensure page user is trying to edit exists
        if not content:
            return render(request, "encyclopedia/error.html", {
            "message": "This page does not exist!"
            })
        
        # Render file for user
        return render(request, "encyclopedia/edit.html", {
                "title": title,
                "content": content
            })


def random_entry(request):
    entries = util.list_entries()
    title = random.choice(entries)
    return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={"title": title}))