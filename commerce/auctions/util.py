from .models import Listings

def get_listing_by_id(raw_pk):

    # Ensure key provided is an inetegr
    try:
        primary_key = int(raw_pk)
    except ValueError:
        return None

    # Ensure listing with that key exists
    try:
        listing = Listings.objects.get(pk=primary_key)
        return listing
    except Listings.DoesNotExist:
        return None