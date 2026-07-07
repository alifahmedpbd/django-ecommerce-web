from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'core/home.html')

def about(request):

    return render(request, "core/about.html")

def contact(request):

    return render(request, "core/contact.html")

def faq(request):

    return render(request, "core/faq.html")

def privacy(request):

    return render(request, "core/privacy.html")

def terms(request):

    return render(request, "core/terms.html")