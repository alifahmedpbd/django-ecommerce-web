from django.http import HttpResponse

def stripe_webhook(request):

    return HttpResponse(status=200)