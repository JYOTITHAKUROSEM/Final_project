# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from datetime import datetime
from Demoapp.forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from django.contrib.auth.hashers import make_password, check_password
from Demoapp.models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from datetime import timedelta
from django.utils import timezone
from Django_Project.settings import BASE_DIR
#from imgurpython import ImgurClient



# Create your views here.
def signup_view(request):
    if request.method == 'GET':
        #display signup form
        signup_form = SignUpForm()
        template_name = 'signup.html'
    elif request.method == 'POST':
        #process the form data
        signup_form = SignUpForm(request.POST)
        #validate the form data
        if signup_form.is_valid():
            #validation successful
            username = signup_form.cleaned_data['username']
            name = signup_form.cleaned_data['name']
            email = signup_form.cleaned_data['email']
            password = signup_form.cleaned_data['password']
            #save data to db
            new_user = UserModel(name=name, email=email, password=make_password(password), username=username)
            new_user.save()
            template_name = 'success.html'

    else:
        form = SignUpForm()


    return render(request, template_name, {'signup_form':signup_form})

def login_view(request):
    if request.method == 'GET':
        #display login form
        login_form = LoginForm()
        template_name = 'login.html'
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
                #compare the password
                if check_password(password, user.password):
                    #login successful
                    template_name = 'login_success.html'
                else:
                    #login failed.
                    template_name = 'login_fail.html'
            else:
                #user does not exist in db.
                template_name = 'login_fail.html'
        else:
            #validation failed
            template_name = 'login_fail.html'

    return render(request, template_name, {'login_form':login_form})







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

