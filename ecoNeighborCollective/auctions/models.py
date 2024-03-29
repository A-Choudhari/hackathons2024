from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    notification = models.CharField(max_length =1024, null=True)
    listing_id = models.IntegerField(null=True)


class Bids(models.Model):
    price = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bid")

    def __str__(self):
        return f"{self.user}:Bid:{self.price}"


class Listings(models.Model):
    description = models.CharField(max_length=150)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="user")
    title = models.CharField(max_length=30)
    price = models.ForeignKey(Bids, on_delete=models.CASCADE, blank=True, related_name="auction_price")
    times_visited = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image_url = models.ImageField(upload_to='images/')  # models.CharField(max_length=1000)
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="user_watchlist")

    def __str__(self):
        return f"{self.title}"


class Auctions(models.Model):
    highest_bid = models.FloatField()
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_auction")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_auction")

    def __str__(self):
        return f"{self.user}:{self.item} Winning Bid:{self.highest_bid}"


class Comments(models.Model):
    comment = models.CharField(max_length=1024)
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing_comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment")
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}:{self.item}.Comment:{self.comment}"

    def serialize(self):
        return {
            "comment": self.comment,
            "item": self.item,
            "user": self.user,
            "reply_to": self.reply_to
        }


class Trash(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name="user_trash")
    image = models.ImageField(upload_to='images/')
    description = models.CharField(max_length=1024)
    location = models.CharField(max_length=1024)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user}:{self.location}"
