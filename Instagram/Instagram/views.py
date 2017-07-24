# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,redirect
#from datetime import datetime
from demoapp.forms import SignUpForm, LoginForm, PostForm, CommentForm, LikeForm
from demoapp.models import UserModel, PostModel, LikeModel, CommentModel, SessionToken
from Instagram.settings import BASE_DIR
from datetime import timedelta
from django.utils import timezone
from imgurpython import ImgurClient

# client_id = '005535c6f80c2dc'
# client_secret = '2520684355b7cf9e0941c6d82bcf392af1807084'
# client = ImgurClient(client_id, client_secret)

from django.contrib.auth.hashers import make_password, check_password
#Create your views here
def signup_view(request):
  #business logic.
   if request.method == 'GET':
     # today = datetime.now
     form = SignUpForm()
     template_name = 'signup.html'
   elif request.method == 'POST':
         form = SignUpForm(request.POST)
         if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            # insert data to database
            new_user = UserModel(name=name, password=make_password(password), username=username, email=email )
            new_user.save()
            template_name = 'success.html'
         return render(request, 'success.html')
   else:
         print "Signup failed !try again"
   return render(request, 'signup.html', {'form':form})
def login_view(request):
     if request.method == 'GET':
         #display login form
         template_name = 'login.html'
         login_form = LoginForm()
     elif request.method == 'POST':
        #process the form data
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
                     #login successful
                     template_name = 'login_success.html'
                     return render(request, template_name)
                 else:
                      #login failed.
                      template_name = 'login_fail.html'
                      return render(request, template_name, {'login_form': LoginForm})

             else:
                    #user does not exist in db.
                    template_name = 'login_fail.html'
     return render(request, template_name, {'login_form':LoginForm})






def feed_view(request):
   return render(request, 'feed.html')
def check_validation(request):
   if request.COOKIES.get('session_token'):
      session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
      if session:
         return session.user
   else:
      return None


def post_view(request):
   user = check_validation(request)

   if user:
      if request.method == 'POST':
         form = PostForm(request.POST, request.FILES)
         if form.is_valid():
            image = form.cleaned_data.get('image')
            caption = form.cleaned_data.get('caption')
            post = PostModel(user=user, image=image, caption=caption)
            post.save()

            path = str(BASE_DIR + post.image.url)

            client = ImgurClient(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)
            post.image_url = client.upload_from_path(path, anon=True)['link']
            post.save()

            return redirect('/feed/')


      else:
         form = PostForm()
      return render(request, 'post.html', {'form': form})
   else:
      return redirect('/login/')


def feeds_view(request):
   user = check_validation(request)
   if user:

      posts = PostModel.objects.all().order_by('created_on')

      for post in posts:
         existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
         if existing_like:
            post.has_liked = True

      return render(request, 'feeds.html', {'posts': posts})
   else:

      return redirect('/login/')


def like_view(request):
   user = check_validation(request)
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
      return redirect('/login/')


def comment_view(request):
   user = check_validation(request)
   if user and request.method == 'POST':
      form = CommentForm(request.POST)
      if form.is_valid():
         post_id = form.cleaned_data.get('post').id
         comment_text = form.cleaned_data.get('comment_text')
         comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
         comment.save()
         return redirect('/feed/')
      else:
         return redirect('/feed/')
   else:
      return redirect('/login')


   # For validating the session


def check_validation(request):
   if request.COOKIES.get('session_token'):
      session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
      if session:
         time_to_live = session.created_on + timedelta(days=1)
         if time_to_live > timezone.now():
            return session.user
   else:
      return None


