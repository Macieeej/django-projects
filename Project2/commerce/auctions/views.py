from datetime import datetime
from turtle import title
from xmlrpc.client import boolean
from django import forms

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import DateTimeField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.db.models import Max

from .models import Bid, Comment, Listing, User


class NewBidForm(forms.Form):
    bid = forms.FloatField(label="", widget=forms.TextInput(attrs={
        'placeholder': 'Enter Your Offer',
        'class': 'myFormClass'
        }))

class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)
        widgets = {
            'comment': forms.TextInput(attrs={
                'class': "myFormClass",
                'style': 'max-width: 300px;',
                'placeholder': 'Place a Comment here'
                }),
        }
        labels = {
            "comment": "",
        }


def index(request):
    # Display listings from newest to oldest
    listings = []
    for listing in reversed(list(Listing.objects.all())):
        if not listing.winner:
            listings.append(listing)

    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        user = request.user
        starting_bid = float(request.POST["starting_bid"])
        description = request.POST["description"]
        creation_date = datetime.now()
        category = request.POST["category"]
        image_url = request.POST["image_url"]

        listing = Listing.objects.create(title=title, user=user, starting_bid=starting_bid, description=description, creation_date=creation_date, category=category, image_url=image_url)

        listing.save()
        
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create_listing.html")


def listing_page(request, TITLE):
    createOrError = True
    isAuctionOwner = False
    isAuctionWinner = False
    isAuctionClosed = False
    isOnWatchlist = False
    listing = Listing.objects.get(title=TITLE)
    bids = Listing.objects.get(title=TITLE).bid.all()
    bidForm = NewBidForm(request.POST)
    commentForm = NewCommentForm(request.POST)

    # Form for adding comments
    if commentForm.is_valid():
        comment = commentForm.cleaned_data['comment']
        new_comment = Comment.objects.create(title=listing, user=request.user, comment=comment, creation_date=datetime.now())
        new_comment.save()
    
    # Get all comments
    comments = Listing.objects.get(title=TITLE).comment.all()

    # Form for adding a bid
    if bidForm.is_valid():
        bid_offer = bidForm.cleaned_data["bid"]
        if bid_offer <= listing.starting_bid:
            createOrError = False
            messages.error(request, 'You must place an offer that is bigger than the starting price.')
        elif createOrError:
            for bid in bids:
                if bid_offer <= bid.bid:
                    createOrError = False
                    messages.error(request, 'You must place an offer that is bigger than a previous offer.')
                    break
        if createOrError:
            # Place a bid and add the item to a user's watchlist
            new_bid = Bid.objects.create(title=listing, user=request.user, bid=bid_offer)
            new_bid.save()
            user = request.user
            user.watchlist.add(listing)
            user.save()

    # Get the highest bid
    bids = Listing.objects.get(title=TITLE).bid.all()
    bids.aggregate(Max('bid'))
    if bids:
        highestBid = bids.order_by('-bid')[0]
        listing.highest_bid = highestBid.bid
        listing.save()
    else:
        highestBid = -1
    sizeOfBids = len(bids)

    # Check if the item is on the current user's watchlist
    if request.user.is_authenticated and listing in request.user.watchlist.all():
        isOnWatchlist = True
    else:
        isOnWatchlist = False

    # Add to watchlist button
    if request.method == "POST":
        data = request.POST
        action = data.get("watchlistAction")
        if action == "add":
            user = request.user
            user.watchlist.add(listing)
            user.save()
        elif action == "unadd":
            user = request.user
            user.watchlist.remove(listing)
            user.save()

    # Close listing button
    if request.method == "POST":
        data = request.POST
        action = data.get("closeListingAction")
        if action == "close":
            user = highestBid.user
            user.won_listing.add(listing)
            user.save() 

    # Check if a current user is auction owner, current winner or if the auctionis closed
    if request.user == Listing.objects.get(title=TITLE).user:
        isAuctionOwner = True
    if highestBid != -1 and request.user == highestBid.user:
        isAuctionWinner = True
    if listing.winner:
        isAuctionClosed = True

    return render(request, "auctions/listing_page.html", {
        "title": TITLE,
        "listing": listing,
        "sizeOfBids": sizeOfBids,
        "highestBid": highestBid,
        "comments": comments,
        "isOnWatchlist": isOnWatchlist,
        "isAuctionOwner": isAuctionOwner,
        "isAuctionWinner": isAuctionWinner,
        "isAuctionClosed": isAuctionClosed,
        "bidForm": NewBidForm(),
        "commentForm": NewCommentForm()
    })


@login_required
def watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


def categories(request):
    categories_list = []
    for listing in Listing.objects.all():
        if listing.category:
            categories_list.append(listing.category)
    categories_set = [*set(categories_list)]
    return render(request, "auctions/categories.html", {
        "categories": categories_set
    })


def category(request, CATEGORY):
    listings = []
    for listing in Listing.objects.all():
        if listing.category and listing.category==CATEGORY:
            listings.append(listing)

    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": CATEGORY
    })