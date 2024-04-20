from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='images/', blank=True, null=True)
    

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    starting_value = models.DecimalField(max_digits=10, decimal_places=2)
    auction_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="won", null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    # end_time = models.DateTimeField(default=timezone.now)
    
    def is_active(self):
        return self.auction_active and self.end_time > timezone.now()

class Watch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchList")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchers")
    def __str__(self):
        return f"user {self.user} is watching listing {self.listing}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    value = models.DecimalField(max_digits=10, decimal_places=2)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=512)