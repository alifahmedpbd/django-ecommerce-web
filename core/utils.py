from django.utils.text import slugify
from decimal import Decimal
from django.utils import timezone

def generate_unique_slug(instance, title):

    model = instance.__class__

    slug = slugify(title)

    unique_slug = slug

    counter = 1

    while model.objects.filter(slug=unique_slug).exclude(pk=instance.pk).exists():

        unique_slug = f"{slug}-{counter}"

        counter += 1
    
    return unique_slug

def format_currency(amount):

    return f"${Decimal(amount):,.2f}"

def today():

    return timezone.now().date()

