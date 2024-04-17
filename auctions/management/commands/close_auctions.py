from django.core.management.base import BaseCommand
from django.utils import timezone
from auctions.models import Listing

class Command(BaseCommand):
    help = 'Close expired auctions'

    def handle(self, *args, **kwargs):
        expired_auctions = Listing.objects.filter(end_time__lte=timezone.now(), auction_active=True)
        for auction in expired_auctions:
            auction.auction_active = False
            auction.save()
            self.stdout.write(self.style.SUCCESS(f"Auction '{auction.title}' closed successfully."))