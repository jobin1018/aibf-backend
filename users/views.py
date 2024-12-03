from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from .models import User, Event, Registration
from .serializers import EventSerializer, RegistrationSerializer


class GoogleSignInView(APIView):
    def post(self, request):
        token = request.data.get('token')
        print("token>>>", token)
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            email = idinfo.get('email')
            name = idinfo.get('name')

            print("idnfo>>>", idinfo)

            # Find or create the user
            user, created = User.objects.get_or_create(email=email, defaults={"name": name})
            
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "email": user.email,
                    "name": user.name,
                }
            })
        except ValueError as e:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)



class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer