from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import User, Listings, Comments, Auctions, Bids, Trash
import json
from .forms import ImageUploadForm, TrashForm
from geopy.geocoders import Nominatim
import numpy as np
from keras import layers, models

from openai import OpenAI # OpenAI official Python package

import json


def index(request):
    try:
        user = User.objects.get(pk=request.user.pk)
    except:
        return render(request, "auctions/map.html")

    if user.notification is None:
        return render(request, "auctions/map.html")
    elif user.listing_id is None:
        message = user.notification
        user.notification = None
        user.save()
        return render(request, "auctions/map.html", {"message":message})
    else:
        message = user.notification
        listing = user.listing_id
        user.notification = None
        user.listing_id = None
        user.save()
        return render(request, "auctions/map.html", {"message":message, "listing":listing})


def markers_info(request):
    trash_info = Trash.objects.filter(is_active=True)
    new_arr = []
    if trash_info.exists():
        for t in trash_info:
            url = t.image.url
            diction = {'image': url, 'id': t.pk, 'description': t.description, 'location': t.location}
            new_arr.append(diction)
        return JsonResponse(new_arr, safe=False)
    else:
        return JsonResponse(new_arr, safe=False)


def end_trash(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("id_data") is not None:
            id_trash = data["id_data"]
            trash_beta = Trash.objects.get(pk=id_trash)
            trash_beta.is_active = False
            trash_beta.save()
        return JsonResponse("Success", safe=False)


@login_required(login_url=reverse_lazy("login"))
def create(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.instance.owner = request.user
            price = float(form.cleaned_data['custom_input'])
            if price >= 0.00:
                new_item = Bids(price=price, user=request.user)
                new_item.save()
                form.instance.price = new_item
                form.save()
            else:
                print("Failed at price")
        else:
            print("Form not valid")
        return HttpResponseRedirect(reverse("display_listing"))
    else:
        form = ImageUploadForm()
        return render(request, 'auctions/create.html', {'form': form})


@login_required(login_url=reverse_lazy("login"))
def watchlist(request):
    user = request.user
    listings_info = user.user_watchlist.all()

    return render(request, "auctions/watchlist.html", {"listings": listings_info})


@login_required(login_url=reverse_lazy("login"))
def display_category(request):
    data = Listings.objects.filter(is_active=True).order_by("-times_visited")
    return render(request, "auctions/category.html", {"category_list": data})


def rank_images(request):
    # Normalize pixel values to be between 0 and 1
    try:
        new_arr = []
        train_data = Listings.objects.filter(is_active=False)
        for t in train_data:
            if t.price.user == request.user:
                new_arr.append(t)
    except:
        data = Listings.objects.filter(is_active=True).order_by("-times_visited")
        return data
    # Define LeNet-5 model
    model = models.Sequential()
    model.add(layers.Conv2D(6, (5, 5), activation='relu', input_shape=(32, 32, 3)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(16, (5, 5), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(120, activation='relu'))
    model.add(layers.Dense(84, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))  # Binary classification
    # Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    # Train the model with dummy labels (as labels are not provided)
    labels = np.random.randint(0, 2, size=(len(images)))  # Dummy labels (binary classification)
    new_arr = []
    training_data = np.array(train_data) / 255.0
    model.fit(training_data, labels, epochs=10)
    # Make predictions on the images
    predictions = model.predict(images)
    # Rank images based on predictions
    ranked_indices = np.argsort(predictions.flatten())[::-1][:num_images]
    # Return the top-ranked images
    top_images = [images[i] for i in ranked_indices]
    return top_images


@login_required(login_url=reverse_lazy("login"))
def trash(request):
    if request.method == 'POST':
        form = TrashForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.instance.user = request.user
            if not form.instance.location[len(form.instance.location) - 1].isdigit():
                form.instance.location = get_location(form.instance.location)
                form.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        form = TrashForm()
        return render(request, 'auctions/trash.html', {'form': form})


def get_location(address):
    geolocator = Nominatim(user_agent="recycling_deposit")  # Replace 'your_app_name' with a unique identifier for your application
    location = geolocator.geocode(address)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return f"{latitude},{longitude}"


def auctions_won(request):
    auc = Listings.objects.filter(is_active=False)
    new_arr = []
    for a in auc:
        if a.price.user == request.user:
            new_arr.append(a)
    return render(request, "auctions/profile.html", {"category_list": new_arr, "extra": " Won By You"})


def search_item(request):
    if request.method == "POST":
        searched = request.POST["searched"]
        posts = Listings.objects.filter(is_active=True, title__contains=searched)
        return render(request, "auctions/category.html", {"extra": f" UNDER {searched.upper()}", "category_list":posts})


def profile(request):
    new_arr = Listings.objects.filter(owner=request.user, is_active=True)
    trashed = Trash.objects.filter(user=request.user, is_active=True)
    return render(request, "auctions/profile.html", {"category_list": new_arr, "extra": "/Deposits Made By You", "trashes":trashed})


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


@login_required(login_url=reverse_lazy("login"))
def comment(request):
    if request.method == "POST":
        listing_id = request.POST["pk"]
        reply_to = request.POST["comment_info"]
        user_input = request.POST["comment"]
        item = Listings.objects.get(pk=listing_id)
        if reply_to == "":
            user_comment = Comments(comment=user_input, user=request.user, item=item)
        else:
            user_comment = Comments(comment=user_input, reply_to=Comments.objects.get(pk=reply_to), user=request.user, item=item)
            c = Comments.objects.get(pk=reply_to)
            user = User.objects.get(pk=c.user.pk)
            user.notification = f"There has been a reply to your comment on Listing: {item.title}"
            user.listing_id = item.pk
            user.save()
        user_comment.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    else:
        data = json.loads(request.body)
        if data.get('listing_id') is not None:
            listing = Listings.objects.get(pk=data['listing_id'])
            arr = []
            comments = Comments.objects.filter(item=listing)
            for comment in comments:
                if comment.reply_to is None:
                    dict = {"user": comment.user.username, "comment": comment.comment, "id": comment.pk,
                            "reply_to": None, "reply_user":None}
                else:
                    dict = {"user":comment.user.username,"comment":comment.comment, "id":comment.pk, "reply_to":comment.reply_to.pk, "reply_user":comment.reply_to.user.username}
                arr.append(dict)
            return JsonResponse(arr, safe=False)


@login_required(login_url=reverse_lazy("login"))
def place_bid(request):
    if request.method == "POST":
        bid = float(request.POST["bid"])
        listing_id = request.POST["listing_id"]
        value_listing = Listings.objects.get(pk=listing_id)
        if value_listing.is_active is True:
            if bid > value_listing.price.price:
                z = Listings.objects.get(pk=listing_id)
                x = Bids.objects.get(pk=z.price.id)
                x.price = bid
                x.user = request.user
                x.save()
                url = f"{reverse('listing', kwargs={'listing_id': listing_id})}"
                return HttpResponseRedirect(url)
            else:
                return HttpResponse("Bid is not high enough.")
        else:
            return render(request, "auctions/index.html", {"message": "This auction is closed"})


@login_required(login_url=reverse_lazy("login"))
def add_watchlist(request):
    if request.method == "POST":
        listing_id = request.POST["add_item"]
        listing_watchlist = Listings.objects.get(pk=listing_id)
        listing_watchlist.watchlist.add(request.user)
        message = "Added to Watchlist"
        # Adding query parameters to the URL
        url = f"{reverse('listing', kwargs={'listing_id': listing_id})}?message={message}"
        return HttpResponseRedirect(url)


@login_required(login_url=reverse_lazy("login"))
def end_watchlist(request):
    if request.method == "POST":
        listing_id = request.POST["end_item"]
        listing_watchlist = Listings.objects.get(pk=listing_id)
        listing_watchlist.watchlist.remove(request.user)
        message2 = "Removed From Watchlist"
        # Adding query parameters to the URL
        url = f"{reverse('listing', kwargs={'listing_id': listing_id})}?message2={message2}"
        return HttpResponseRedirect(url)


@login_required(login_url=reverse_lazy("login"))
def end_listing(request):
    data = json.loads(request.body)
    if data.get("listing_id") is not None:
        listing_id = data["listing_id"]
        listing = Listings.objects.get(pk=listing_id)
        listing.is_active = False
        listing.save()
        price = listing.price.price
        user = User.objects.get(pk=listing.price.user.pk)
        auction = Auctions(item=listing, highest_bid=price, user=user)
        user.notification = "Please check Auctions Won for recent updates"
        user.save()
        auction.save()
        return JsonResponse("Success", safe=False)
    else:
        return JsonResponse("Failure", safe=False)


@login_required(login_url=reverse_lazy("login"))
def listings(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    message = request.GET.get('message', '')
    message2 = request.GET.get('message2', '')
    listing.times_visited = listing.times_visited + 1
    listing.save()
    comments = Comments.objects.filter(item=listing)
    bids = Bids.objects.get(pk=listing.price.id)
    winner_bid = False
    in_watchlist = False
    if listing.owner == request.user:
        auction_owner = True
    else:
        auction_owner = False
        if request.user in listing.watchlist.all():
            in_watchlist = True
        else:
            in_watchlist = False
    if request.user == bids.user and listing.is_active is False:
        winner_bid = True
    return render(request, "auctions/listing.html", {"listing": listing,
                                                     "comments":comments,
                                                     "auction_owner":auction_owner,
                                                     "in_watchlist":in_watchlist,
                                                     "winner_bid": winner_bid,
                                                     "message":message,
                                                     "message2":message2})


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


def recognize_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_url = data.get('image')
        if image_url:
            client = OpenAI(api_key="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")
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text",
                             "text": "Things that can be recycled are most types of plastics (including Plastic #1 (PET), Plastic #2 (HDPE), Plastic #3 (PVC), Plastic #4 (LDPE), Plastic #5 (Polypropylene), Plastic #7 (Other), Plastic Bottles, and Plastic Cups), paper, metal, and glass. Things that cannot be recycled are wood, cloth, organic materials, chemicals, hazardous waste, and electronics.\nWhat is the item shown in the image? Give me just the answer in as few words as possible.\nCan I recycle the item shown in the image? Give a one word YES or NO answer.\nSeperate the answers with a comma"},
                            {
                                "type": "image_url",
                                "image_url": f"{image_url}",
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            text_output = response.choices[0].message.content

            output_list = text_output.replace(".", "").replace(", ", ",").split(",")
            detected_obj = ""
            recyclable_y_n = ""

            if len(output_list) == 2:
                detected_obj = output_list[0]
                recyclable_y_n = output_list[1].lower()

            print("Detected object:", detected_obj)
            if recyclable_y_n == "yes":
                return JsonResponse({"result": "The item is recyclable.", "object_name":detected_obj})
            elif recyclable_y_n == "no":
                return JsonResponse({"result": "The item is not recyclable.", "object_name":detected_obj})
            else:
                return JsonResponse({"result":"Not sure.", "object_name": detected_obj})
    else:
        return render(request, "auctions/recognize_item.html")

