from django.contrib import admin
from django.urls import path, include
from tutorme import views

urlpatterns = [
    path('tutorme/', include('tutorme.urls')),
    path('tutorme/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('social/signup/', views.signup_redirect, name='signup_redirect'),
    # if allaut url(below) changed, let david know to change on google side
    path('', include("allauth.urls")),
    path('', views.start, name='landing page')
]
