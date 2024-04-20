from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connections
from .models import User, Listing, Watch, Bid, Comment
from .forms import ListingForm
from .utils import *
# from django.utils import timezone
# from datetime import timedelta
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import time
from django.template.loader import render_to_string


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
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmation = request.POST.get('confirmation')

        # Basic validation
        if password == confirmation:
            # Generate OTP
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['username'] = username
            request.session['email'] = email
            request.session['password'] = password
            
            html_content = render_to_string('auctions/otp_mail.html', {'username': username, 'otp': otp})

            # Send OTP via email
            send_mail(
                'Your Account Verification OTP',
                'Use the following OTP to verify your account:',
                'bidbazaar2024@gmail.com',  # Change this to your actual sender email address
                [email],  # Add the recipient's email address to the recipient_list
                html_message=html_content,  # Use HTML content for the email body
                fail_silently=False,
            )

            # Redirect to OTP verification page
            return redirect('otp_verification')
        else:
            return render(request, 'auctions/register.html', {'message': 'Passwords do not match'})

    return render(request, 'auctions/register.html')

def otp_verification(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        if int(user_otp) == request.session.get('otp', 0):
            # Create user if OTP verification succeeds
            user = User.objects.create(
                username=request.session['username'],
                email=request.session['email'],
                password=make_password(request.session['password'])
            )
            user.save()
            # Set a session variable to indicate OTP verification success
            request.session['otp_verified'] = True
            return redirect('otp_success')  # Redirect to the success page
        else:
            return render(request, 'auctions/otp_authentication.html', {'error': 'Invalid OTP'})
    return render(request, 'auctions/otp_authentication.html')



def otp_success(request):
    # Redirect to login page after 5 seconds
    time.sleep(5)
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        # Check if user exists
        user = User.objects.get(username=username, email=email)
        
        if user is not None:
            # Generate OTP
            otp = random.randint(100000, 999999)
            
            request.session['otp'] = otp
            request.session['username'] = username
            request.session['email'] = email
            
            html_content = render_to_string('auctions/forgot_password_mail.html', {'username': username, 'otp': otp})
            # Send OTP via email
            try:
                send_mail(
                    'Your Account Verification OTP',
                    'Use the following OTP to verify your account:',
                    'bidbazaar2024@gmail.com',
                    [email],
                    html_message=html_content,
                    fail_silently=False,
                )
            except Exception as e:
                return render(request, 'auctions/forgot_password.html', {'message': 'Failed to send email. Please try again later.'})
            
            return redirect('password_otp')
        else:
            return render(request, 'auctions/forgot_password.html', {'message': 'Invalid username and/or email.'})
        
    return render(request, 'auctions/forgot_password.html')

def password_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        
        # Check if OTP is provided
        if user_otp is None:
            return render(request, 'auctions/otp_authentication.html', {'error': 'OTP is required'})
        
        # Check if OTP is a valid integer
        try:
            otp = int(user_otp)
        except ValueError:
            return render(request, 'auctions/otp_authentication.html', {'error': 'Invalid OTP format'})
        
        # Check OTP against session OTP
        if otp == request.session.get('otp', 0):
            # Set a session variable to indicate OTP verification success
            request.session['otp_verified'] = True
            
            username = request.session['username']
            email = request.session['email']
            
            # Generate a new password
            password = User.objects.make_random_password()
            user = User.objects.get(username=username, email=email)
            user.set_password(password)
            user.save()
            
            html_content = render_to_string('auctions/new_password_mail.html', {'username': username, 'password': password})
            
            send_mail(
                'Your Account Verification OTP',
                'Use the following OTP to verify your account:',
                'bidbazaar2024@gmail.com',
                [email],
                html_message=html_content,
                fail_silently=False,
            )
            
            return redirect('otp_success')  # Redirect to the success page
        else:
            return render(request, 'auctions/otp_authentication.html', {'error': 'Invalid OTP'})
        
    return render(request, 'auctions/otp_authentication.html')



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