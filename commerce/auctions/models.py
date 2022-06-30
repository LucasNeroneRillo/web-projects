from django.contrib.auth.models import AbstractUser
from django.db import models


class Listings(models.Model):
    creator = models.ForeignKey('User', on_delete=models.CASCADE, related_name="user_listings")
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    starting_bid = models.DecimalField(max_digits=19, decimal_places=4)
    current_bid = models.DecimalField(max_digits=19, decimal_places=4)
    image_url = models.URLField(max_length=8192, blank=True)
    category = models.CharField(max_length=32, blank=True)
    bids_made = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    def __str__(self):
        price = "${:,.2f}".format(self.current_bid)
        return f"{self.title}, listed by {self.creator}, bid at {price}"


class User(AbstractUser):
    watchlisted = models.ManyToManyField(Listings, blank=True, related_name="users_watching")

    
class Bids(models.Model):
    bid = models.DecimalField(max_digits=8, decimal_places=2)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidders")

    def __str__(self):
        return f"{self.listing.title}: {self.bid}, made by {self.bidder}"


class Comments(models.Model):
    creator = models.ForeignKey('User', on_delete=models.CASCADE, related_name="user_comments")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=1024)
