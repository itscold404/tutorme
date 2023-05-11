from django.urls import path, include
from . import views

app_name = "tutorme"

urlpatterns = [
    path('login_user', views.login_user, name='login_user'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('create_user', views.create_user, name='create_user'),
    path('home', views.go_home, name='home'),
    path('create_post', views.create_post, name='create_post'),
    path('choose_user_type', views.choose_user_type,
         name='choose_user_type'),
    path('search', views.search, name='search'),
    path('book_tutoring_session', views.book_tutoring_session,
         name='book_tutoring_session'),
    path('approving_session', views.approve_session_request,
         name='approving_sessions'),
    path('deleting_session', views.delete_session_request, name='deleting_session'),
    path('go_mailbox', views.go_mailbox, name="go_mailbox"),
    path('switch', views.change_user_type, name="switch"),
    path('profile', views.go_profile, name='profile'),
    path('edit_user', views.edit_user, name='edit_user'),
    path('read_notification/<path:id>', views.read_notification, name='read_notification'),
    path('edit_posts', views.edit_posts, name = "edit_posts"),
]

# path('', views.home, name='home'),
# path('', include("allauth.urls")),
