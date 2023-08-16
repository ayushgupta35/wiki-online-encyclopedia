from django.shortcuts import render
from django.http import HttpResponseRedirect
import markdown2
import secrets
from django import forms
from django.urls import reverse
from . import util
from markdown2 import Markdown

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Entry title", widget=forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-8', 'rows' : 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry):
    markdown = Markdown()
    page = util.get_entry(entry)
    if page == None:
        return render(request, "encyclopedia/error.html", {
            "title": entry    
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown.convert(page),
            "title": entry
        })

def new(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) == None or form.cleaned_data["edit"] == True):
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))
            else:
                return render(request, "encyclopedia/new.html", {
                "form": form,
                "existing": True,
                "entry": title
                })
        else:
            return render(request, "encyclopedia/new.html", {
            "form": form,
            "existing": False
            })
    else:
        return render(request,"encyclopedia/new.html", {
            "form": NewEntryForm(),
            "existing": False
        })    

def edit(request, entry):
    page = util.get_entry(entry)
    if page == None:
        return render(request, "encyclopedia/error.html", {
            "title": entry    
        })
    else:
        form = NewEntryForm()
        form.fields["title"].initial = entry     
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = page
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/new.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "title": form.fields["title"].initial
        })        

def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': randomEntry}))

def search(request):
    search_word = request.GET.get('q','')
    if(util.get_entry(search_word) != None):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': search_word }))
    else:
        results = []
        for entry in util.list_entries():
            if search_word.upper() in entry.upper():
                results.append(entry)

        return render(request, "encyclopedia/index.html", {
        "entries": results,
        "search": True,
        "search_word": search_word
    })