from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('view/<int:image_id>/', views.view_image, name='view_image'),
    path('track/', views.track_location, name='track_location'),
]