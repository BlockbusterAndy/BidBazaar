from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    description = models.CharField(max_length=512)
    starting_value = models.DecimalField(max_digits=10, decimal_places=2)
    auction_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="won", null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/")

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