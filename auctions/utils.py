from django.db.models import Max
from django.core.management.base import BaseCommand
from django.utils import timezone
from .models import User, Listing, Watch, Bid
from django.core.mail import send_mail
from django.conf import settings

def get_current_bid_value(listing_id):
    """
    returns the highest current bid for a listing as an integer
    """
    bids = Bid.objects.filter(listing_id=listing_id)
    if bids.exists():
        return bids.aggregate(Max('value'))['value__max']
    else:
        return Listing.objects.filter(id=listing_id)[0].starting_value

import logging

logger = logging.getLogger(__name__)

def get_current_bidder(listing_id):
    """
    returns the highest current bidder for a listing as a User object
    """
    bids = Bid.objects.filter(listing_id=listing_id)
    logger.info("Bids for listing %d: %s", listing_id, bids)
    
    if bids.exists():
        highest_bid = bids.order_by('-value')[0]
        highest_bidder = highest_bid.user
        logger.info("Highest bidder for listing %d: %s", listing_id, highest_bidder)
        return highest_bidder
    else:
        logger.info("No bids found for listing %d", listing_id)
        return None