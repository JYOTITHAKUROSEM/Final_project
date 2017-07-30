"""Instagram URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from views import login_view, signup_view, feed_view, post_view, like_view, comment_view, logout_view, like_comm, search
#from django.conf.urls.static import static
# from views import signup_view
# from views import post_view
# from views import feed_view
urlpatterns = [
   url('post/', post_view),
   url('feed/', feed_view),
   url('logout/',logout_view),
   url('like', like_view),
   url('comment', comment_view),
   url('login/', login_view),
   url('', signup_view),
   url('like_comm/', like_comm),
   url('search/',search),
]


