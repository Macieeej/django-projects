import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect
from django.core.paginator import Paginator

from .models import User, Post

        

def index(request, page):
    #Dodac nr strony w linku
    if request.method == 'POST':
        user = request.user
        body = request.POST['post_body']
        post = Post.objects.create(user=user, body=body)
        post.save()

    postsAll = Post.objects.all()
    postsAll = postsAll.order_by("-timestamp").all()
    paginator = Paginator(postsAll, 10)
    posts = paginator.get_page(page)
    page_next = page + 1
    page_prev = page - 1

    return render(request, "network/index.html", {
        'posts': posts,
        'page_prev': page_prev,
        'page_next': page_next,
        'has_prev': paginator.page(page).has_previous(),
        'has_next': paginator.page(page).has_next(),
    })


def user_profile(request, user, page):

    followers = User.objects.get(username=user).followed_by.all()
    following = User.objects.get(username=user).following.all()

    postsAll = User.objects.get(username=user).posts.all()
    postsAll = postsAll.order_by("-timestamp").all()
    paginator = Paginator(postsAll, 10)
    posts = paginator.get_page(page)
    page_next = page + 1
    page_prev = page - 1

    # check if user is displaying own profile
    isOwnProfile = True if request.user.username == user else False

    # check if current user is following a user
    isFollower = False
    for foo in followers:
        if request.user == foo:
            isFollower = True

    # Follow/Unfollow functionality
    if request.method == "POST":
        data = request.POST
        action = data.get("followAction")
        if action == "unfollow":
            currUser = request.user
            currUser.following.remove(User.objects.get(username=user))
            currUser.save()
        elif action == "follow":
            currUser = request.user
            currUser.following.add(User.objects.get(username=user))
            currUser.save()

    return render(request, "network/user_profile.html", {
        'queriedUser': user,
        'posts': posts,
        'page_prev': page_prev,
        'page_next': page_next,
        'has_prev': paginator.page(page).has_previous(),
        'has_next': paginator.page(page).has_next(),
        'followersNum': len(followers),
        'followingNum': len(following),
        'isOwnProfile': isOwnProfile,
        'isFollower': isFollower,
    })


@login_required
def following_view(request, page):

    postsAll = Post.objects.all()
    postsAll = postsAll.order_by("-timestamp").all()
    following = User.objects.get(username=request.user.username).following.all()

    postsAll_filter = []
    for post in postsAll:
        if post.user in following:
            postsAll_filter.append(post)

    paginator = Paginator(postsAll_filter, 10)
    posts = paginator.get_page(page)
    page_next = page + 1
    page_prev = page - 1

    return render(request, "network/following.html", {
        'posts': posts,
        'page_prev': page_prev,
        'page_next': page_next,
        'has_prev': paginator.page(page).has_previous(),
        'has_next': paginator.page(page).has_next(),
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
            return HttpResponseRedirect(reverse("index", args=(1,)))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index", args=(1,)))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index", args=(1,)))
    else:
        return render(request, "network/register.html")

@csrf_exempt
@login_required
def edit_post(request, post_id):

    # Query for requested email
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("body") is not None:
            post.body = data["body"]
        #if data.get("archived") is not None:
        #    email.archived = data["archived"]
        post.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

def redirect_view(request):
    response = redirect('/1')
    return response