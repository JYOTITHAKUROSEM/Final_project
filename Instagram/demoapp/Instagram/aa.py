# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,redirect
#from datetime import datetime
from demoapp.forms import SignUpForm, LoginForm, PostForm, LikeForm,CommentForm, LikeCommForm
from demoapp.models import UserModel,SessionToken, PostModel, LikeModel, CommentModel, LikeComm
from django.http import HttpResponse
from Instagram.settings import BASE_DIR
from datetime import timedelta
from django.utils import timezone
from imgurpython import ImgurClient
from django.contrib.auth.hashers import make_password, check_password
# client_id = '005535c6f80c2dc'
# client_secret = '2520684355b7cf9e0941c6d82bcf392af1807084'
# client = ImgurClient(client_id, client_secret)


#Create your views here
def signup_view(request):
    if request.method == 'GET':
        signup_form = SignUpForm()                             # calling & display signup form
        template_name = 'signup.html'                          # rendering to signup.html after get reqst
    elif request.method == 'POST':
        signup_form = SignUpForm(request.POST)
        print "line 25"# calling & process the form data
        if signup_form.is_valid():
            print "line 27"# validate the form data
            username = signup_form.cleaned_data['username']
            name = signup_form.cleaned_data['name']
            email = signup_form.cleaned_data['email']
            password =signup_form.cleaned_data['password']
            #data validation
            if(len(username)<5):
                new_user = UserModel(name=name, email=email, password=make_password(password), username=username)
                new_user.save()  # save data to db
                template_name = 'success.html'  # rendering to success.html after post req
            else:
                # return redirect('/signup/')
                dict = {"key": "Pleas fill the form"}
                #return render(request, 'signup.html', dict)
                #return render(request, 'error.html')
        else:
            print "line 41"
            dict={"key":"Pleas fill the form"}
            return render(request,'signup.html',dict)
    print "line 44"
    return render(request,template_name, {'signup_form': signup_form})

def login_view(request):
    response_data = {}
    # if request.method == 'GET':
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            #validation successful
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            #read data from db
            user = UserModel.objects.filter(username=username).first()
            if user:
                #compare password
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('/feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    return render(request,'login_fail.html')
            else:
                return render(request, 'login_fail.html')
        else:
            return HttpResponse("Invalid form data.")
    elif request.method == 'GET':
        form = LoginForm()
        response_data['form'] = form

    return render(request, 'login.html', response_data)

def post_view(request):
    user = check_user(request)
    if user == None:
        return redirect('/login/')
    elif request.method == 'GET':
        post_form = PostForm()
        return render(request, 'post.html', {'post_form': post_form})
    elif request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('image')
            caption = form.cleaned_data.get('caption')
            post = PostModel(user=user, image=image, caption=caption)
            post.save()
            client = ImgurClient('005535c6f80c2dc', '2520684355b7cf9e0941c6d82bcf392af1807084')
            path = str(BASE_DIR + "\\" +  post.image.url)
            post.image_url = client.upload_from_path(path,anon=True)['link']
            post.save()
            return redirect("/feed/")
        else:
            return HttpResponse("Form data is not valid.")
    else:
        return HttpResponse("Invalid request.")


def feed_view(request):
    user = check_user(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post = post.id,user = user)
            if existing_like:
                post.has_liked = True
        return render(request, 'feed.html', {'posts': posts})
        # elif user and request.method== 'POST':

    else:
        return redirect('/login/')
def like_view(request):
    user = check_user(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()
            return redirect('/feed/')
        else:
            HttpResponse("form data is not valid")
    else:
        return redirect('/login/')
def comment_view(request):
    user = check_user(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get("post").id
            comment_text = form.cleaned_data.get("comment_text")
            current_post = PostModel.objects.filter(id=post_id).first()
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')

# For Validating The session
def check_user(request):
    if request.COOKIES.get("session_token"):
        session = SessionToken.objects.filter(session_token = request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
             return session.user
        else:
            return None

def logout_view(request):
    user_id = check_user(request)
    delete_user = SessionToken.objects.filter(user = user_id)
    delete_user.delete()
    return redirect('/signup/')
def like_comm(request):
	user = check_user(request)
	if user and request.method == 'POST':
		form = LikeCommForm(request.POST)
		if form.is_valid():
			comment_id = form.cleaned_data.get('comment').id
			existing_like = LikeComm.objects.filter(comment_id=comment_id, user=user).first()
			if not existing_like:
				LikeComm.objects.create(comment_id=comment_id, user=user,)
			else:
				existing_like.delete()
			return redirect('/feed/')
	else:
		return redirect('/login/')