from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

import random
import re

from . import util


# Home page
def index(request):
    # Activate Search
    searchQuery = request.GET.get('q', '')
    if searchQuery != "":
        searchQueryTest = util.get_entry(searchQuery)
        if searchQueryTest is not None:
            return HttpResponseRedirect("wiki/" + searchQuery)
        else:
            return HttpResponseRedirect("wiki/search/" + searchQuery)

    # Random Button
    entries = util.list_entries()
    randomArticle = random.choice(entries)

    return render(request, "encyclopedia/index.html", {
        # Lists all article entries
        "entries": entries,
        "randomArticle": randomArticle
    })


# Article Pages
def article(request, title):
    # Activate Search
    searchQuery = request.GET.get('q', '')
    if searchQuery != "":
        searchQueryTest = util.get_entry(searchQuery)
        if searchQueryTest is not None:
            return HttpResponseRedirect("/" + "wiki/" + searchQuery)
        else:
            return HttpResponseRedirect("search/" + searchQuery)

    # Random Button
    entries = util.list_entries()
    randomArticle = random.choice(entries)

    # Uses Util function to get the article info based on the URL title
    get_entry = util.get_entry(title)
    # If the function can find the article go through the
    # text and change the markdown to HTML to display on the page
    if get_entry is not None:
        # Regex for h1
        entryFormat = re.sub(r"## +(\w+)", r"<h2>\1</h2>", get_entry)
        # Regex for h2
        entryFormat = re.sub(r"# +(\w+)", r"<h1>\1</h1>", entryFormat)
        # Regex for p tag
        entryFormat = re.sub(r"\n(\w.*)", r"<p>\1</p>", entryFormat)
        # Regex for a tag
        entryFormat = re.sub(r"\[(\w*)\]\((.[^)]+)\)", r"<a href=\2>\1</a>", entryFormat)
        # Regex for bolding
        entryFormat = re.sub(r"\*\*(.[^*]+)\*\*", r"<b>\1</b>", entryFormat)
        # Regex for lists and unordered lists
        entryFormat = re.sub(r"\* (.*)", r"<li>\1</li>", entryFormat)
        entryFormat = re.sub(r"(<li>.*</li>)\n", r"\1", entryFormat)
        entryFormat = re.sub(r"(<li>.*</li>)", r"<ul>\1</ul>", entryFormat)

        return render(request, "encyclopedia/article.html", {
            "title": title,
            "get_entry": entryFormat,
            "randomArticle": randomArticle
        })

    # If the title returns edit display edit page
    elif title == "edit":
        return render(request, "encyclopedia/edit.html")

    # If the title is new_article display the new article page
    elif title == "new_article":
        # If form is POST then add in the inputs
        if request.method == "POST":
            form = newArticleForm(request.POST)
            # If the form is valid get the title and content
            if form.is_valid():
                titleInput = form.cleaned_data["titleInput"]
                contentInput = form.cleaned_data["contentInput"]
                # If there are no existing articles with the same name save the entry using the
                # save_entry function and go to the new entries page
                if util.get_entry(titleInput) is None:
                    util.save_entry(titleInput, contentInput)
                    return HttpResponseRedirect(titleInput)
                # If a article with that name already exists reload the page with an error message
                else:
                    error = "<div class='alert alert-danger col-md-5'>There is already an article named " + titleInput + "</div>"
                    return render(request, "encyclopedia/newArticle.html", {
                        "form": form,
                        "error": error,
                        "randomArticle": randomArticle
                    })
            # If form is not POST load the page normally
            else:
                return render(request, "encyclopedia/newArticle.html", {
                    "form": form,
                    "randomArticle": randomArticle
                })
        # Load the page with the form
        return render(request, "encyclopedia/newArticle.html", {
            "form": newArticleForm(),
            "randomArticle": randomArticle
        })
    # If the title is anything else just load the page
    else:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "randomArticle": randomArticle
        })


# Form for creating new article, includes title and content input fields
class newArticleForm(forms.Form):
    titleInput = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': "col-md-12", 'style': 'width:98%; border-width:1px; border-style:solid;'}),)
    contentInput = forms.CharField(widget=forms.Textarea(attrs={'class': "col-md-12", 'style': 'height:500px; width:98%'}), label="Content")


# New Article Page
def newArticle(request):
    return render(request, "encyclopedia/newArticle.html")


# Edit Page
def edit(request, editTitle):
    # Activate Search
    searchQuery = request.GET.get('q', '')
    if searchQuery != "":
        searchQueryTest = util.get_entry(searchQuery)
        if searchQueryTest is not None:
            return HttpResponseRedirect("/" + "wiki/" + searchQuery)
        else:
            return HttpResponseRedirect("/" + "wiki/search/" + searchQuery)

    # Random Button
    entries = util.list_entries()
    randomArticle = random.choice(entries)

    # Get title from URL and search for the article markdown info
    articleInfo = util.get_entry(editTitle)
    # Create the html text area field with the articles markdown filled out
    textArea = "<textarea name='editedContent' value= '' style='height:500px; width:98%'>" + articleInfo + "</textarea>"

    # If form is POST get 'editedContent' from the form submits querylist and save the entry then redirect to the page you were editing
    if request.method == "POST":
        editForm = request.POST
        editedContent = editForm.get('editedContent')
        print(editedContent)
        util.save_entry(editTitle, editedContent)
        return HttpResponseRedirect("/wiki/" + editTitle)

    # Render the title, article info and textArea
    return render(request, "encyclopedia/edit.html", {
        "editTitle": editTitle,
        "articleInfo": articleInfo,
        "textArea": textArea,
        "randomArticle": randomArticle
    })


# Search Page
def search(request, searchQuery):
    # Activate Search
    searchQ = request.GET.get('q', '')
    if searchQ != "":
        searchQueryTest = util.get_entry(searchQ)
        if searchQueryTest is not None:
            return HttpResponseRedirect("/" + "wiki/" + searchQ)
        else:
            return HttpResponseRedirect(searchQ)

    # Random Button
    entries = util.list_entries()
    randomArticle = random.choice(entries)

    # Get list of search results if there are any
    entries = util.list_entries()
    matchingQueries = []
    matchesTF = []
    for entry in entries:
        # casefold makes comparing the query with the name listings non case sensitive
        queryMatchTest = searchQuery.casefold() in entry.casefold()
        matchesTF.append(queryMatchTest)
        if queryMatchTest is True:
            matchingQueries.append(entry)

    # Check if there are no matches in the search
    noMatches = True in matchesTF
    if noMatches is False:
        noMatchResponse = "No Matches"
    else:
        noMatchResponse = ""

    return render(request, "encyclopedia/search.html", {
        "searchQuery": searchQuery,
        "matchingQueries": matchingQueries,
        "noMatchResponse": noMatchResponse,
        "randomArticle": randomArticle
    })
