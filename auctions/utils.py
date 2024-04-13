from django.db.models import Max

from .models import User, Listing, Watch, Bid

def get_current_bid_value(listing_id):
    """
    returns the highest current bid for a listing as an integer
    """
    bids = Bid.objects.filter(listing_id=listing_id)
    if bids.exists():
        return bids.aggregate(Max('value'))['value__max']
    else:
        return Listing.objects.filter(id=listing_id)[0].starting_value