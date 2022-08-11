from cgi import print_exception
from unicodedata import name
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# listings, bids, comments

class Listing(models.Model):
    title = models.CharField(max_length=32)
    # creator of the listing:
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing')
    starting_bid = models.FloatField(max_length=16)
    description = models.CharField(max_length=128)
    creation_date = models.DateTimeField()
    category = models.CharField(max_length=16)
    image_url = models.CharField(max_length=128)
    watchlist = models.ManyToManyField(User, blank=True, related_name='watchlist')
    winner = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, default='', null=True, related_name='won_listing')
    highest_bid = models.FloatField(max_length=16, blank=True, default=-1 , null=True)

    class Meta:
        ordering = ['creation_date']

    def __str__(self):
        return f"Title: {self.title} User: {self.user} Price: {self.starting_bid}"

class Bid(models.Model):
    title = models.ForeignKey(Listing, on_delete=models.CASCADE,  related_name='bid')
    # user that is bidding:
    user = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='bid')
    bid = models.FloatField(max_length=16)

class Comment(models.Model):
    title = models.ForeignKey(Listing, on_delete=models.CASCADE,  related_name='comment')
    # user that created comment:
    user = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='comment')
    comment = models.CharField(max_length=32)
    creation_date = models.DateTimeField()

    class Meta:
        ordering = ['creation_date']

    def __str__(self):
        return 'Comment {} by {}'.format(self.comment, self.user)
