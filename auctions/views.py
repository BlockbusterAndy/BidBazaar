from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import connections
from .models import User, Listing, Watch, Bid, Comment
from .forms import ListingForm
from .utils import *
from django.utils import timezone
from datetime import timedelta

def index(request):
    listings = Listing.objects.filter(auction_active=True)
    for listing in listings:
        listing.starting_value = get_current_bid_value(listing.id)
        # listing.remaining_time = max(listing.end_time - timezone.now(), timedelta(seconds=0))
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

@login_required(redirect_field_name='index')
def create_listing(request):
    if not(request.user.is_authenticated):
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = Listing(user=request.user, title=form.cleaned_data["title"], category=form.cleaned_data["category"], description=form.cleaned_data["description"], starting_value=form.cleaned_data["starting_value"], image=form.cleaned_data["image"])
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/createListing.html", {
                'form': form
            })
        

    return render(request, "auctions/createListing.html", {
        'form': ListingForm
    })

def view_listing(request, listing_id, error_message=False):
    listing = Listing.objects.get(pk=listing_id)
    isActive = listing.auction_active
    current_bid = get_current_bid_value(listing_id)
    highest_bidder = get_current_bidder(listing_id)
    # listing.remaining_time = max(listing.end_time - timezone.now(), timedelta(seconds=0))

    user_authenticated = request.user.is_authenticated
    if (user_authenticated):    
        watchExists = Watch.objects.filter(user=request.user, listing=listing_id).exists()
        isOwner = listing.user == request.user
    else:
        watchExists=False
        isOwner = False

    if not(error_message):
        return render(request, "auctions/listingView.html", {
            'user_authenticated': user_authenticated,
            'listing': listing,
            'watch': watchExists,
            'current_bid': current_bid,
            'owner': isOwner,
            'active': isActive,
            'comments': Comment.objects.filter(listing=listing),
            'highest_bidder': highest_bidder,
            # 'remaining_time': listing.remaining_time,
        })
    else:
        return render(request, "auctions/listingView.html", {
            'user_authenticated': user_authenticated,
            'listing': listing,
            'watch': watchExists,
            'current_bid': current_bid,
            'owner': isOwner,
            'active': isActive,
            'comments': Comment.objects.filter(listing=listing),
            'highest_bidder': highest_bidder,
            # 'remaining_time': listing.remaining_time,
            'error_message': 'Your bid was too Low',
        })

@login_required(redirect_field_name='index')
def watch(request, listing_id):
    # if the user is not watching the item it will add a watch to the item. If the user is already watching the item it will delete the watch from the item.
    watch = Watch.objects.filter(user=request.user, listing_id=listing_id)
    if watch.exists():
        watch.delete()
    else:
        watch = Watch(user=request.user, listing_id=listing_id)
        watch.save()
    
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(redirect_field_name='index')
def bid(request, listing_id):
    current_bid = get_current_bid_value(listing_id)

    if float(request.POST["value"]) > current_bid:
        newBid = Bid(user=request.user, listing_id=listing_id, value=request.POST["value"])
        newBid.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

    else:
        return view_listing(request, listing_id, error_message=True)

@login_required(redirect_field_name='index')
def close_auction(request, listing_id):
    # TODO if no one has bid
    listing = Listing.objects.get(id=listing_id)
    listing.auction_active = False

    # set the highest bid to the winner of the bid
    bids = Bid.objects.filter(listing_id=listing_id)
    if bids.exists():
        highest_bid = bids.order_by('value')[0]
        listing.winner = highest_bid.user
    else:
        listing.winner = None

    listing.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(redirect_field_name='index')
def comment(request, listing_id):
    comment = request.POST['comment']
    comment = Comment(user=request.user, listing_id = listing_id, comment=comment)
    comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required(redirect_field_name='index')
def your_listings(request):
    return render(request, "auctions/yourListings.html", {
        'listings': Listing.objects.filter(user=request.user)
    })

@login_required(redirect_field_name='index')
def won_listings(request):
    return render(request, "auctions/wonListings.html", {
        'listings': Listing.objects.filter(winner=request.user)
    })

@login_required(redirect_field_name='index')
def watch_list(request):
    listings = Listing.objects.raw(f'SELECT * FROM auctions_listing, auctions_watch WHERE auctions_listing.id = auctions_watch.listing_id AND auctions_watch.user_id=%s', [request.user.id])
    return render(request, "auctions/watchList.html", {
        'listings': listings
    })

def categories(request):
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT DISTINCT category FROM auctions_listing ORDER BY category")
        cats = cursor.fetchall() #list of tuples returned

    # converting the list of tuples to just a list
    categories = []
    for category in cats:
        categories.append(category[0])

    return render(request, "auctions/categories.html", {
        'categories': categories
    }
    )

def category(request, category):
    return render(request, "auctions/category.html",{
        'category': category,
        'active_listings': Listing.objects.filter(category=category, auction_active=True),
        'inactive_listings': Listing.objects.filter(category=category, auction_active=False)
    })