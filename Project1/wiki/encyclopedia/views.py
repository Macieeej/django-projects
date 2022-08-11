from cProfile import label
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import secrets
import markdown2
from . import util


class NewSearchForm(forms.Form):
    task = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'}))

class NewCreatorForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Enter Title Here'}))
    content = forms.CharField(label="Enter New Page\'s Content Below", widget=forms.Textarea)

class NewEditorForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput)
    content = forms.CharField(label="Edit Page\'s Content Below", widget=forms.Textarea)


def index(request):
    search_list = []
    if request.method == "POST":
        form = NewSearchForm(request.POST)
        if form.is_valid():
            task = form.cleaned_data["task"]
            for entry in util.list_entries():
                if task == entry:
                    return render(request, "encyclopedia/wiki_page.html", {
                        "page": markdown2.markdown(util.get_entry(entry)),
                        "form": NewSearchForm(),
                        "title": entry
                    })
                if task in entry:
                    search_list.append(entry)
            return render(request, "encyclopedia/index.html", {
                "entries": search_list,
                "form": NewSearchForm()
            })

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": NewSearchForm()
    })


def wiki_page(request, TITLE):
    for entry in util.list_entries():
        if TITLE == entry:
            return render(request, "encyclopedia/wiki_page.html", {
                "page": markdown2.markdown(util.get_entry(TITLE)),
                "form": NewSearchForm(),
                "title": TITLE
            })
    return HttpResponse("Error! Page does not exist.")


def creator(request):
    if request.method == "POST":
        form = NewCreatorForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            for entry in util.list_entries():
                if title == entry:
                    return HttpResponse("Error! Page already exists.")
            util.save_entry(title, content)
            return render(request, "encyclopedia/wiki_page.html", {
                "page": markdown2.markdown(util.get_entry(title)),
                "form": NewSearchForm(),
                "title": title
            })
    return render(request, "encyclopedia/creator.html", {
        "form": NewSearchForm(),
        "creatorForm": NewCreatorForm()
    })


def editor(request, TITLE):
    initial_data = {
        'title': TITLE,
        'content': util.get_entry(TITLE)
    }
    form = NewEditorForm(request.POST or None, initial=initial_data)
    if form.is_valid():
        content = form.cleaned_data["content"]
        util.save_entry(TITLE, content)
        return render(request, "encyclopedia/wiki_page.html", {
            "page": markdown2.markdown(util.get_entry(TITLE)),
            "form": NewSearchForm(),
            "title": TITLE
        })
    return render(request, "encyclopedia/editor.html", {
        "form": NewSearchForm(),
        "editorForm": form,
        "title": TITLE
    })


def random(request):
    random_title = secrets.choice(util.list_entries())
    return wiki_page(request, TITLE=random_title)