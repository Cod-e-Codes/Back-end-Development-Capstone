from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


# Create your views here.

def signup(request):
    if request.method == "POST":
        # Get username and password from the POST request
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            # Check if the user already exists
            user = User.objects.filter(username=username).first()
            if user:
                # If user exists, return the signup page with an error message
                return render(request, "signup.html", {"form": SignUpForm(), "message": "User already exists"})
            else:
                # Create a new user with a hashed password
                user = User.objects.create(
                    username=username, 
                    password=make_password(password)
                )
                # Log in the new user
                login(request, user)
                # Redirect to the index page
                return HttpResponseRedirect(reverse("index"))
        except User.DoesNotExist:
            # If something goes wrong, re-render the signup page
            return render(request, "signup.html", {"form": SignUpForm()})
    # Render the signup page for GET requests
    return render(request, "signup.html", {"form": SignUpForm()})



def index(request):
    return render(request, "index.html")


def songs(request):
    # Replace with your Songs microservice URL
    SONGS_URL = "http://songs-sn-labs-codylmarseng.labs-prod-openshift-san-a45631dc5778dc6371c67d206ba9ae5c-0000.us-east.containers.appdomain.cloud"
    try:
        # Fetch songs data from the Songs microservice
        songs = req.get(f"{SONGS_URL}/song").json()
    except req.RequestException as e:
        # Handle errors by showing an empty list or error message
        print(f"Error fetching songs: {e}")
        songs = {"songs": []}
    return render(request, "songs.html", {"songs": songs["songs"]})


def photos(request):
    # Replace with your Pictures microservice URL
    PHOTO_URL = "https://pictures.1p9oyxb0eh1k.us-south.codeengine.appdomain.cloud"
    try:
        # Fetch photos data from the Pictures microservice
        photos = req.get(f"{PHOTO_URL}/picture").json()
    except req.RequestException as e:
        # Handle errors by showing an empty list or error message
        print(f"Error fetching photos: {e}")
        photos = {"photos": []}
    return render(request, "photos.html", {"photos": photos["photos"]})


def login_view(request):
    if request.method == "POST":
        # Get username and password from the POST request
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            # Find the user with the provided username
            user = User.objects.get(username=username)
            # Check if the password is correct
            if user.check_password(password):
                # Log in the user
                login(request, user)
                # Redirect to the index page
                return HttpResponseRedirect(reverse("index"))
            else:
                # If the password is incorrect, re-render the login page with an error
                return render(request, "login.html", {"form": LoginForm(), "message": "Invalid username or password"})
        except User.DoesNotExist:
            # If the user does not exist, re-render the login page with an error
            return render(request, "login.html", {"form": LoginForm(), "message": "Invalid username or password"})
    # Render the login page for GET requests
    return render(request, "login.html", {"form": LoginForm()})


def logout_view(request):
    # Log out the user
    logout(request)
    # Redirect to the login page
    return HttpResponseRedirect(reverse("login"))


def concerts(request):
    if request.user.is_authenticated:
        # Initialize an empty list to hold concert details
        lst_of_concert = []
        # Retrieve all concert objects from the database
        concert_objects = Concert.objects.all()
        # Loop through each concert object
        for item in concert_objects:
            try:
                # Check if the current user is attending this concert
                status = item.attendee.filter(user=request.user).first().attending
            except:
                # If no attendee status exists, set it to "-"
                status = "-"
            # Append the concert and its status to the list
            lst_of_concert.append({
                "concert": item,
                "status": status
            })
        # Render the concerts.html template with the list of concerts
        return render(request, "concerts.html", {"concerts": lst_of_concert})
    else:
        # Redirect to the login page if the user is not authenticated
        return HttpResponseRedirect(reverse("login"))



def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = Concert.objects.get(pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
